
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


def get_average(data:list):
    """计算list中所有元素的平均值"""
    total_sum = 0
    length = len(data)

    if length <= 0:
        return 0

    for i in range(len(data)):
        total_sum += data[i]

    return total_sum / length
