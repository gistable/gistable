import os
import uuid
from PIL import Image
from flask.ext.uploads import extension


def random_filename():
    """生成伪随机uuid字符串，用做文件名"""
    return str(uuid.uuid4())


def process_image(file_storage, upload_set, max_border):
    """
    将Flask中上传的图片进行居中裁剪、缩放，然后保存
    
    @param file_storage: Werkzeug FileStorage对象, 如request.files['image']
    @param upload_set: Flask-Uploads UploadSet对象
    @param max_border: 待缩放的边长
    @return: 图片filename
    """
    # 打开图片
    image = Image.open(file_storage.stream)

    # 居中裁剪
    w, h = image.size
    if w > h:
        border = h
        crop_region = ((w - border) / 2, 0, (w + border) / 2, border)
    else:
        border = w
        crop_region = (0, (h - border) / 2, border, (h + border) / 2)
    image = image.crop(crop_region)
    
    # 缩放
    if border > max_border:
        image = image.resize((max_border, max_border), Image.ANTIALIAS)
    
    # 保存
    ext = extension(file_storage.filename)
    filename = '%s.%s' % (random_filename(), ext)
    folder = upload_set.config.destination
    filename = upload_set.resolve_conflict(folder, filename)
    path = os.path.join(folder, filename)
    image.save(path)
    return filename