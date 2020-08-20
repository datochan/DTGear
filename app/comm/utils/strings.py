"""

"""
import random


def random_mac_address():
    """生成随机的mac地址"""
    mac = [0x80, 0x3F,
           random.randint(0x00, 0x7f),
           random.randint(0x00, 0x7f),
           random.randint(0x00, 0xff),
           random.randint(0x00, 0xff)]
    return ''.join(map(lambda x: "%02X" % x, mac))


def stock_state(state):
    """
    翻译股票的状态
    :param state: L=上市，S=暂停，DE=已退市，UN=未上市，NULL=不确定
    :return:
    """
    if state == 'L':
        return "上市"
    if state == 'S':
        return "停牌"
    if state == 'DE':
        return "已退市"
    if state == 'UN':
        return "未上市"
    if state == 'NULL':
        return "不确定"
    return "未知"


if __name__ == '__main__':
    print(random_mac_address())
