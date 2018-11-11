import os


def file_list_in_path(file_path):
    """
    获取指定目录中的文件列表
    :param file_path: 指定的路径
    :return:
    """
    for dirpath, dirnames, filenames in os.walk(file_path):
        return filenames
