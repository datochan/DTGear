
def int2byte(int32):
    """
    将int32类型的数据转换为byte类型
    :param int32:
    :return:
    """
    return int(0xff & int32)


def get_median(data:list):
    """求一个数组中的中位数"""
    if len(data) <= 0:
        return 0

    data.sort()
    half = len(data) // 2
    return (data[half] + data[~(half-1)]) / 2
