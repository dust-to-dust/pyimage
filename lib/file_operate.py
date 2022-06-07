# Coding: UTF-8
# Author: 尘
# Datetime: 2021/8/13 
# DebugInfo:
from os.path import splitext, join
from os import scandir, mkdir, makedirs, remove
from shutil import move, rmtree
import PIL


def get_suffix(filepath):
    return splitext(filepath)[-1]


def del_suffix(filepath):
    return splitext(filepath)[0]


def is_img(filename):
    ftype = get_suffix(filename)
    support = ['.jpg', '.png', '.jpeg', '.webp', '.gif', '.heic', '.heif', '.bmp', '.avif']
    return True if ftype in support else False


def img_classify(path: str):
    """
    删除指定目录下小于要求的文件
    @param path: 目标文件目录
    @return:
    """
    assert path
    try:
        mkdir(path + '/低分辨率类')
        mkdir(path + '/高分辨率类')
        mkdir(path + '/表情包类')
        mkdir(path + '/非图片类')
    except FileExistsError:
        pass

    for file in scandir(path):
        if file.is_dir():
            continue
        file_info = file.stat()
        try:
            img = PIL.Image.open(file.path)
        except PIL.UnidentifiedImageError:
            move(file.path, path + '/非图片类')
            continue
        size = file_info[6] // 1024
        width = img.width
        height = img.height
        min_ = min(width, height)
        max_ = max(width, height)
        img.close()

        # 分类逻辑
        if size < 20 or max_ < 150:
            remove(file)
        elif size < 60 and max_ < 800:
            move(file.path, path + '/表情包类')
        elif size < 150 or max_ < 1000:
            move(file.path, path + '/低分辨率类')
        elif size > 1000 and min_ > 2000:
            move(file.path, path + '/高分辨率类')
        else:
            pass
