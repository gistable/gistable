"""

Compute the TSNR of a bunch of nifti files and generate the equivalent nifti
SNR 3Ds. 

Depends on nibabel, matplotlib and scipy

""" 

import os
import sys
from glob import glob
import getopt
    
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import nanmean
from scipy.io import savemat

from nibabel import load,save 
import nibabel.nifti1 as nifti


def tsnr(data,affine,file_name):
    mean_d = np.mean(data,axis=-1)
    std_d = np.std(data,axis=-1)
    tsnr = mean_d/std_d
    tsnr[np.where(np.isinf(tsnr))] = np.nan
    mean_tsnr = nanmean(np.ravel(tsnr))
    tsnr_image = nifti.Nifti1Image(tsnr,affine)
    save(tsnr_image,file_name)
    savemat(file_name.split('.')[0],{'tsnr':tsnr})
    return mean_tsnr

def usage():
    print "Usage: fmri_tsnr [options] nifti_dir"

def help_me():
    print("This program computes the temporal SNR for a directory of nifti files")

if __name__ == "__main__":

    # Get inputs and options:

    # Last argument is your input:
    path = sys.argv[-1]

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hcvp", ["help",
                                                         "cat",
                                                         "verbose",
                                                          "plot"])
    except getopt.GetoptError, err:
        # print help information and exit:
        print str(err)
        usage()
        sys.exit(2)
    # Set the defaults:
    cat = False
    verbose = False
    p = False

    # Then get the input opts:
    for o,a in opts:
        if o in ["-v","--verbose"]:
            verbose=True
        elif o in ["-h","--help"]:
            usage()
            help_me()
        elif o in ["-c","--cat"]:
            cat = True
        elif o in ["-p","--plot"]:
            p = True
        else:
            usage()
            assert False, "unhandled option"

    # Make sure you have a place to save the results:
    tsnr_path = '%s/TSNR/'%path
    if not os.path.exists(tsnr_path):
        os.mkdir(tsnr_path)
    
    allepi = glob('%s*.nii*'%path) # this will return an unsorted list
    allepi.sort() #This sorts it

    # If you are concatenating initialize the data with the first one:
    if cat: 
        epi1 = load(allepi.pop(0))
        data = epi1.get_data()
        affine = epi1.get_affine()

    # Otherwise, you might want to plot the average tsnr on a scan-by-scan
    # basis:
    else:
        snr = []
        label = []
    for epi in allepi:
        if verbose: 
            print 'Groking %s'%epi
        
        # If you are concatenating, just concatenate:
        if cat: 
            data = np.concatenate([data,load(epi).get_data()],axis=-1)

        # Otherwise, do the analysis on a file-by-file basis:
        else:
            fname = os.path.split(epi)[-1].split('.')[0]
            nibber = load(epi)
            affine = nibber.get_affine()
            data = nibber.get_data()
            snr.append(tsnr(data,affine,'%s%s_tsnr.nii.gz'%(tsnr_path,fname)))
            label.append(fname)
    # Then, if you were cat'ing, do the analysis, when you exit the cat-loop:
    if cat:
        snr = tsnr(data,affine,'%stsnr_mean.nii.gz'%tsnr_path)

    if p==True:
        fig = plt.figure()
        ax = fig.add_subplot(1,1,1)
        ax.bar(np.arange(len(snr))+1,snr)
        ax.set_xticks(np.arange(len(snr))+1)
        ax.set_xticklabels(label)
        labels = ax.get_xticklabels()
        ax.set_ylabel('SNR')
        ax.set_xlabel('File')
        fig.set_size_inches(len(label)*1.2,8)
        plt.setp(labels, rotation=45, fontsize=10)
        fig.savefig('%smean_tsnr_.png'%tsnr_path)
        
