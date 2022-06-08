from numpy import array


def dhash(image):
    """
    计算图片的dHash值
    :param image: PIL.Image
    :return: dHash值,string类型
    """
    difference = _difference(image)
    # 转化为16进制(每个差值为一个bit,每8bit转为一个16进制)
    decimal_value = 0
    hash_string = ""
    for index, value in enumerate(difference):
        if value:  # value为0, 不用计算, 程序优化
            decimal_value += value * (2 ** (index % 8))
        if index % 8 == 7:  # 每8位的结束
            hash_string += str(hex(decimal_value)[2:].rjust(2, "0"))  # 不足2位以0填充。0xf=>0x0f
            decimal_value = 0
    return hash_string


def cal_hamming_distance(first, second):
    """
    计算两张图片的汉明距离(基于dHash算法)
    :param first: Image或者dHash值(str)
    :param second: Image或者dHash值(str)
    :return: hamming distance. 值越大,说明两张图片差别越大,反之,则说明越相似
    """
    # A. dHash值计算汉明距离
    if isinstance(first, str):
        return _hamming_distance_with_hash(first, second)

    # B. image计算汉明距离
    image1_diff = _difference(first)
    image2_diff = _difference(second)
    return sum(array(image1_diff) ^ array(image2_diff))


def is_similar(im1, im2):
    if cal_hamming_distance(im1, im2) < 3:
        return True
    return False

def _difference(image):
    """
    计算image的像素差值
    :param image: PIL.Image
    :return: 差值数组。0、1组成
    """
    resize_width = 9
    resize_height = 8
    difference = []
    # 1. resize to (9,8)
    # 2. 灰度化 Grayscale
    data = array(image.resize((resize_width, resize_height)).convert('L'))
    # 3. 比较相邻像素
    for row in range(resize_height):
        for col in range(resize_width - 1):
            difference.append(data[row, col] > data[row, col + 1])
    return difference


def _hamming_distance_with_hash(dhash1, dhash2):
    """
    根据dHash值计算hamming distance
    :param dhash1: str
    :param dhash2: str
    :return: 汉明距离(int)
    """
    difference = (int(dhash1, 16)) ^ (int(dhash2, 16))
    return bin(difference).count("1")
