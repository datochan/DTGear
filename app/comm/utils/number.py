
def int2byte(int32):
    """
    将int32类型的数据转换为byte类型
    :param int32:
    :return:
    """
    return int(0xff & int32)