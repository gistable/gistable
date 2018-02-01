#!/usr/bin/env python

""" Video stabilization with OpenCV (>=2.3) and Hugin

Adrien Gaidon
INRIA - 2012

TODO: add cropping, clean-up and improve doc-strings
"""


import sys
import os
import shutil
import tempfile
import subprocess

import numpy as np

import cv2
import hsi


def exec_shell(cmd_line, raise_on_err=False):
    """ Execute a shell statement (as a string 'cmd_line')
    in a subprocess and return (stdout, stderr) results

    if 'raise_on_err': raise AssertionError if something was dumped to stderr
    """
    out, err = subprocess.Popen(
        cmd_line,
        shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    ).communicate()
    assert not (raise_on_err and err), \
            "Error: cmd=%s, stderr=%s" % (cmd_line, err)
    return out.strip(), err.strip()


def pto_gen(img_fns, hfov=50, out_pto="project.pto"):
    """ Generate a Hugin .pto project file

    Parameters
    ----------
    img_fns: list,
             the (ordered) full paths to the video frames

    hfov: int, optional, default: 50,
          horizontal field of view in degrees
          (around 50 is ok for most non-fish-eye cameras)

    out_pto: string, optional, default: 'project.pto',
             output path to the generated panotools .pto file

    Notes
    -----
    Suitable as input for further tools such as the cpfind control-point generator.

    Inspired from pto_gen
    (http://hugin.sourceforge.net/docs/html/pto__gen_8cpp-source.html)
    but with some hacks to correct the generated m-line in the header.

    Uses the Hugin python scripting interface (http://wiki.panotools.org/Hugin_Scripting_Interface)
    """
    # projection type: 0 == rectilinear (2 == equirectangular)
    projection = 0
    assert projection >= 0, "Invalid projection number (%d)" % projection
    assert 1 <= hfov <= 360, "Invalid horizontal field of view (%d)" % hfov
    # hugin Panorama object
    pano = hsi.Panorama()
    # add the images in order
    for img_fn in img_fns:
        src_img = hsi.SrcPanoImage(img_fn)
        src_img.setProjection(projection)
        src_img.setHFOV(hfov)
        src_img.setExifCropFactor(1.0)
        pano.addImage(src_img)
    # check we added all of them
    n_inserted = pano.getNrOfImages()
    assert n_inserted == len(img_fns), "Didn't insert all images (%d < %d)" % \
            (n_inserted, len(img_fns))
    # output the .pto file
    pano.writeData(hsi.ofstream(out_pto + '.tmp'))  # same as pano.printPanoramaScript(...)
    # some bug in header: rewrite it manually (TODO through hsi?)
    with open(out_pto + '.tmp', 'r') as tmp_ff:
        with open(out_pto, 'w' ) as ff:
            # re-write the header
            ff.write(tmp_ff.readline())
            ff.write(tmp_ff.readline())
            # force jpeg for the p-line
            p_line = tmp_ff.readline().strip().split()
            assert p_line[0] == 'p', "BUG: should be a p-line"
            ff.write(' '.join(p_line[:7]) + ' n"JPEG q100"\n')
            # remove extra 'f' param in the m-line
            # (screws everything up if left here...)
            m_line = tmp_ff.readline().strip().split()
            assert m_line[0] == 'm', "BUG: should be a m-line"
            ff.write(' '.join(m_line[:3]) + ' ' + ' '.join(m_line[4:]) + '\n')
            # write all other lines
            for l in tmp_ff.readlines():
                ff.write(l)
    os.remove(out_pto + '.tmp')
    print "saved {0}".format(out_pto)


def get_surf_kps(img_fn, img=None, center_out=0.5,
                 cness_thresh=1000, min_pts=30, max_pts=300):
    """ Return the opened gray-scale OpenCV image and its SURF keypoints

    Points "in the middle" of the frames are left out
    (center_out = proportioned of space left out).
    """
    assert center_out < 1, "Too high center part to remove"
    # initialize the SURF keypoint detector and descriptor
    surf = cv2.SURF(cness_thresh)
    # load the gray-scale image
    if img is None:
        img = cv2.imread(img_fn, 0)
    # detect and describe SURF keypoints
    cvkp, ds = surf.detect(img, None, False)
    # re-arrange the data properly
    ds.shape = (-1, surf.descriptorSize())  # reshape to (n_pts, desc_size)
    kp = np.array([p.pt for p in cvkp])
    cness = np.array([p.response for p in cvkp])
    # filter out points in the middle (likely to be on the moving actor)
    if center_out > 0:
        rx = img.shape[1]
        lb = center_out * 0.5 * rx
        ub = (1 - center_out * 0.5) * rx
        mask = (kp[:, 0] < lb) + (kp[:, 0] > ub)
        kp = kp[mask, :]
        ds = ds[mask, :]
        cness = cness[mask]
    # check we're within the limits
    if kp.shape[0] < min_pts:
        if cness_thresh > 100:
            # redo the whole thing with a lower threshold
            _, kp, ds = get_surf_kps(img_fn, img=img, center_out=center_out,
                                     min_pts=min_pts, max_pts=max_pts,
                                     cness_thresh=0.5 * cness_thresh)
        else:
            # we lowered the threshold too much and didn't find enough points
            raise ValueError('Degenerate image (e.g. black) or too high center_out')
    if kp.shape[0] > max_pts:
        # too many points, take those with max cornerness only
        cness_order = np.argsort(cness)[::-1]
        kp = kp[cness_order[:max_pts], :]
        ds = ds[cness_order[:max_pts], :]
    return img, kp, ds


def get_pairwise_matches(pos1, descs1, pos2, descs2, up_to=30):
    """ Get the matching local features from img1 to img2
    """
    assert pos1.shape[0] * pos2.shape[0] < 1e8, \
            "Too many points: increase cornerness threshold"
    assert pos1.shape[0] > 10 and pos1.shape[0] > 10, \
            "Not enough points: lower cornerness threshold"
    # get the similarities between all descriptors
    sims = np.dot(descs1, descs2.T)
    # Note: in practice, using a kernel between histograms works better
    # get the best matches
    mi2 = sims.argmax(axis=1).squeeze()
    ms = sims.max(axis=1).squeeze()
    bmi1 = ms.argsort()[::-1][:up_to]
    bmi2 = mi2[bmi1]
    # return their positions
    bp1 = pos1[bmi1]
    bp2 = pos2[bmi2]
    return bp1, bp2


def gen_pairwise_surf_control_points(proj_file, img_fns, display=False):
    """ Use OpenCV for pairwaise image matching

    cf. <opencv samples dir>/find_obj.py
    """
    # get the kps of the first frame
    img1, kp1, ds1 = get_surf_kps(img_fns[0])
    # match the frame t with t+1
    cpoints = []
    for i2 in range(1, len(img_fns)):
        # get the kps of frame t+1
        img2, kp2, ds2 = get_surf_kps(img_fns[i2])
        # get the control points
        cp1, cp2 = get_pairwise_matches(kp1, ds1, kp2, ds2)
        # estimate the homography
        H, mask = cv2.findHomography(cp1, cp2, cv2.RANSAC)
        mask = mask.squeeze() > 0
        # display the matches and homography
        if display:
            hom_warp_image(img1, cp1, img2, cp2, H, mask)
        # filter out the outlier matches
        cp1 = cp1[mask]
        cp2 = cp2[mask]
        # add the control points
        cpoints.extend([hsi.ControlPoint(i2 - 1, x1, y1, i2, x2, y2)
                        for (x1, y1), (x2, y2) in zip(cp1, cp2)])
        # next -> cur
        img1, kp1, ds1 = img2, kp2, ds2
    # write to pto
    pano = hsi.Panorama()
    pano.readData(hsi.ifstream(proj_file))
    pano.setCtrlPoints(cpoints)
    pano.writeData(hsi.ofstream(proj_file))


def gen_control_points(proj_file, img_fns, hfov, method="surf"):
    """ Generate control points by detecting and matching salient local features
    """
    # initialize the pto project
    pto_gen(img_fns, hfov=hfov, out_pto=proj_file)
    if method == "surf":
        # generate the control points with OpenCV's SURF + RANSAC
        gen_pairwise_surf_control_points(proj_file, img_fns)
    elif method == "cpfind":
        # generate the control points with hugin's cpfind
        # Note: not a good idea because forces points to be spread over the frame
        #       which forces points to be on the actor => we don't want that
        opts = "-v -n 1"  # 1 thread
        # RANSAC to estimate homography
        opts+= "  --ransacmode hom"
        #opts+= " --mulitrow"  # multirow heuristics
        # don't downscale image by 2
        opts+= " --fullscale"
        # --linearmatchlen 5"  # match only pairs (t, t+1), ..., (t, t+n)
        opts+= "  --linearmatch"
        # at most size pts per cell in w x h grid
        opts+= " --sieve1width 5 --sieve1height 5 --sieve1size 10"
        # at most size pts per cell in w x h grid
        opts+= " --sieve2width 5 --sieve2height 5 --sieve2size 1"
        cmd = "cpfind {opts} -o {pto} {pto}"
        exec_shell(cmd.format(opts=opts, pto=proj_file))
    elif method == "sift":
        # with autopano-sift-c
        cmd = "autopano-sift-c --ransac off --projection 0,{hfov} {pto} {imgs}"
        exec_shell(cmd.format(hfov=hfov, pto=proj_file, imgs=' '.join(img_fns)))
    else:
        raise ValueError("Unknown method %s" % method)


def motion_stabilize_frames(img_fns, hfov=50, out_avi="out.avi"):
    """ Motion stabilize a video

    Parameters
    ----------
    img_fns: list,
             the (ordered) full paths to the video frames

    hfov: int, optional, default: 50,
          horizontal field of view in degrees
          (around 50 is ok for most non-fish-eye cameras)

    out_avi: string, optional, default: 'out.avi',
             output path to the generated motion-stabilized video

    Notes
    -----
    Uses opencv, hugin and ffmpeg.
    """
    # create a temporary directory
    tmpd = tempfile.mkdtemp(prefix='tmp_mostab_', dir='.')
    # pano tools project file
    proj_file = "%s/project.pto" % tmpd
    try:
        # generate the control points
        gen_control_points(proj_file, img_fns, hfov)
        # prune the control points  TODO necessary?
        #cmd = "cpclean -p -o {pto} {pto}"
        #exec_shell(cmd.format(pto=proj_file))
        # optimise geometric parameters only
        cmd = "autooptimiser -p -s -o {pto}.optim.pto {pto}"
        # Note: not '-l' as levelling can screw things up
        exec_shell(cmd.format(pto=proj_file))
        # remapping to create the distorted frames in the full scene plane
        cmd = "nona -t 1 -m TIFF_m -o {tmpd}/remapped {pto}.optim.pto"  # 1 thread
        exec_shell(cmd.format(tmpd=tmpd, pto=proj_file))
        # make a video from the tiff frames
        cmd = "ffmpeg -y -f image2 -i {tmpd}/remapped%04d.tif -vcodec mjpeg -qscale 1 -an {avi}"
        exec_shell(cmd.format(tmpd=tmpd, avi=out_avi), raise_on_err=False)
        print "saved {0}".format(out_avi)
    finally:
        # clean up
        shutil.rmtree(tmpd)
    sys.stdout.flush()


# =============================================================================
# some visualization function based on opencv
# =============================================================================


def draw_match(img1, img2, p1, p2, mask=None, H=None):
    """ Draw the matches found from img1 to img2
    """
    h1, w1 = img1.shape[:2]
    h2, w2 = img2.shape[:2]
    vis = np.zeros((max(h1, h2), w1+w2), np.uint8)
    vis[:h1, :w1] = img1
    vis[:h2, w1:w1+w2] = img2
    vis = cv2.cvtColor(vis, cv2.COLOR_GRAY2BGR)

    if H is not None:
        corners = np.float32([[0, 0], [w1, 0], [w1, h1], [0, h1]])
        corners = np.int32(
            cv2.perspectiveTransform(
                corners.reshape(1, -1, 2), H).reshape(-1, 2) + (w1, 0))
        cv2.polylines(vis, [corners], True, (255, 255, 255))
    
    if mask is None:
        mask = np.ones(len(p1), np.bool_)

    green = (63, 255, 0)
    red = (0, 0, 255)
    for (x1, y1), (x2, y2), inlier in zip(np.int32(p1), np.int32(p2), mask):
        col = [red, green][inlier]
        if inlier:
            cv2.line(vis, (x1, y1), (x2+w1, y2), col)
            cv2.circle(vis, (x1, y1), 4, col, 2)
            cv2.circle(vis, (x2+w1, y2), 4, col, 2)
        else:
            r = 2
            thickness = 3
            cv2.line(vis, (x1-r, y1-r), (x1+r, y1+r), col, thickness)
            cv2.line(vis, (x1-r, y1+r), (x1+r, y1-r), col, thickness)
            cv2.line(vis, (x2+w1-r, y2-r), (x2+w1+r, y2+r), col, thickness)
            cv2.line(vis, (x2+w1-r, y2+r), (x2+w1+r, y2-r), col, thickness)
    return vis


def hom_warp_image(img1, pts1, img2, pts2, hom, mask):
    """ Show keypoint matches and the estimated homography
    """
    # warp img2
    if img2.ndim == 2:
        img2 = img2[:,:,np.newaxis]
    wimg2 = np.zeros_like(img2)
    for chan in range(img2.shape[2]):
        _i2 = np.ascontiguousarray(img2[:, :, chan], dtype="f4")
        #wimg2[:,:,chan] = cv2.warpPerspective(_i2, hom, _i2.T.shape)
        zz = cv2.warpPerspective(_i2, hom, _i2.T.shape)
        zx, zy = np.where(zz > 0)
        wimg2[zx, zy, chan] = zz[zx, zy]
    wimg2 = wimg2.squeeze()
    # warp the matches in img2
    wpts2 = cv2.perspectiveTransform(pts2.reshape(1, -1, 2), hom).reshape(-1, 2)
    # show the kept matches
    vis = draw_match(img1, wimg2, pts1, wpts2, mask, hom)
    cv2.imshow("match", vis)
    cv2.waitKey()


if __name__ == "__main__":

    if len(sys.argv) < 4:
        print "usage: video_stabilization.py <out.avi> <frame 1> <frame 2> ..."
        sys.exit(0)

    out_avi = sys.argv[1]
    img_fns = sys.argv[2:]
    
    motion_stabilize_frames(img_fns, out_avi=out_avi)