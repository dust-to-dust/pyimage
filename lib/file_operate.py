# Coding: UTF-8
# Author: 尘
# Datetime: 2021/8/13 
# DebugInfo: 

from os.path import splitext, join
from os import listdir, mkdir
from shutil import move


def get_suffix(filepath):
    return splitext(filepath)[-1]  # 取后缀 -1和1等价


def del_suffix(filepath):
    return splitext(filepath)[0]


def is_img(filename):
    ftype = get_suffix(filename)
    support = ['.jpg', '.png', '.jpeg', '.webp', '.gif', '.heic', '.heif', '.bmp']
    return True if ftype in support else False
