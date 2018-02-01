def grab_camera_texture(camera):
    print(camera.texture_size, camera.texture)
    nparr = np.fromstring(camera.texture.pixels, dtype=np.uint8)
    a = np.reshape(nparr, (camera.texture_size[1], camera.texture_size[0], 4))
    # a = nparr
    a = cv2.cvtColor(a, cv2.cv.CV_RGBA2RGB)
    # cv2.imshow("asd", a)

    print(camera.texture.colorfmt, camera.texture.bufferfmt)
    camera.play = False
    ct = camera.texture
    t = Texture.create(
        size=ct.size[:2],
        colorfmt=ct.colorfmt,
        bufferfmt=ct.bufferfmt
    )
    t.blit_buffer(
        ct.pixels,
        colorfmt=ct.colorfmt,
        bufferfmt=ct.bufferfmt
    )
    camera.play = True
    t.flip_vertical()
    return t