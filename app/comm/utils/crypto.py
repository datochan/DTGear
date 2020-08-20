import os
import hashlib
import binascii
import blowfish


def md5hex(word):
    """ MD5加密算法，返回32位小写16进制符号"""
    m = hashlib.md5()
    m.update(word)
    return m.hexdigest()


def md5sum(filename):
    """
    用于获取文件的md5值
    :param filename: 文件名
    :return: MD5码
    """
    if not os.path.isfile(filename):
        # 如果校验md5的文件不是文件，返回空
        return

    myhash = hashlib.md5()
    f = open(filename, 'rb')
    while True:
        b = f.read(1024 * 16)
        if not b:
            break
        myhash.update(b)
    f.close()
    return myhash.hexdigest()


def encrypt_with_blowfish(package):
    """使用blowfish对封包进行加密"""
    offset = 0
    content = []
    encrypted_result = []
    cipher = blowfish.Cipher(b"SECURE20031107_TDXAB", byte_order="little")
    total_length = len(package)
    # 循环加密
    while offset + 8 <= total_length:
        data_encrypted = cipher.encrypt_block(package[offset:offset + 8])
        encrypted_result.append(data_encrypted)
        offset += 8

    if total_length % 8:
        # 如果封包最后有结余，不足8个字符，就补齐0
        delta = total_length % 8
        content.append(binascii.b2a_hex(package[offset:offset + delta]))
        content.append(b"00" * (8 - delta))
        data_encrypted = cipher.encrypt_block(binascii.a2b_hex(b"".join(content)))
        encrypted_result.append(data_encrypted)

    return b"".join(encrypted_result)


if __name__ == "__main__":
    # test()
    result = md5sum("/Users/datochan/WorkSpace/GoglandProjects/src/data/report/gpcw19960630.zip")
    # result = md5hex("/Users/datochan/WorkSpace/GoglandProjects/src/data/report/gpcw19960630.zip")
    print(result)
