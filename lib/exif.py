from PIL import Image
import piexif


def encode_EXIF(title='', comment='', author=''):
    zeroth_ifd = {piexif.ImageIFD.XPTitle: title.encode('utf-8'),
                  piexif.ImageIFD.XPComment: comment.encode('utf-8'),
                  piexif.ImageIFD.XPAuthor: author.encode('utf-8'),
                  }
    return piexif.dump({"0th": zeroth_ifd})


def get_EXIF(im):
    if isinstance(im, str):
        with Image.open(im) as im:
            exif = im.getexif()
    else:
        exif = im.getexif()

    return {'title': exif[40091].decode('utf-8'), 'comment': exif[40092].decode('utf-8'),
            'author': exif[40093].decode('utf-8')}


if __name__ == '__main__':
    path = r'C:\Users\123\Desktop\realcugan-ncnn-vulkan-20220318-windows\1.jpg'
    path_t = r'C:\Users\123\Desktop\realcugan-ncnn-vulkan-20220318-windows\test.jpg'

    with Image.open(path) as im1:
        im1.save(path_t, exif=encode_EXIF('我是标题', '我是注释', '我是作者'))

    with Image.open(path_t) as im2:
        print(get_EXIF(im2))
