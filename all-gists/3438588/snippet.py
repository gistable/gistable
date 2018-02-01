"""

http://saepy.sinaapp.com/topic/24/Tornado%E4%B8%8A%E4%BC%A0%E6%96%87%E4%BB%B6%E7%A4%BA%E4%BE%8B

在bcore的开发过程中，涉及到上传文件有两个地方，一个是相册，一个是文章图文混排。这里作为一个备忘。罗列一些关键点：

文件上传的内容体在tornado.web.RequestHandler.request.files属性中，并且是以数组形式存放的。
使用临时文件存储时，在write完成后要记着把seek重置到文件头。要不然文件无法被读取。
再使用Image模块的thumbnail方法进行缩放时,resample=1作为重载渲染参数能够有效的使图片平滑，消除锯齿。

"""

if self.request.files:
            for f in self.request.files['postfile']:
                rawname = f['filename']
                dstname = str(int(time.time()))+'.'+rawname.split('.').pop()
                thbname = "thumb_"+dstname
                # write a file
                # src = "./static/upload/src/"+dstname
                # file(src,'w+').write(f['body'])
                tf = tempfile.NamedTemporaryFile()
                tf.write(f['body'])
                tf.seek(0)
                 
                # create normal file
                # img = Image.open(src)
                img = Image.open(tf.name)
                img.thumbnail((920,920),resample=1)
                img.save("./static/upload/postfiles/"+dstname)
 
                # create thumb file
                img.thumbnail((100,100),resample=1)
                img.save("./static/upload/postfiles/"+thbname)
 
                tf.close()