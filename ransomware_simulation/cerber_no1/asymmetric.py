#!/bin/bash/env python
#pip uninstall pycrypto
# coding=UTF-8
import os
from os import chmod
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA
from Crypto import Random
from Crypto.Cipher import PKCS1_OAEP

class assymetric():
    # Constructor
    def __init__(self):
        self.private_key_path = ""  # 初始化私钥文件路径为空字符串
        self.public_key_path = ""   # 初始化公钥文件路径为空字符串
        self.bit_len = 2048         # 初始化密钥长度为2048位
        self.private_key_PEM = None  # 初始化私钥PEM为None
        self.public_key_PEM = None   # 初始化公钥PEM为None
        self.key = None              # 初始化密钥为None

    def generate_keys(self):  # 生成密钥对
        self.key = RSA.generate(self.bit_len)  # 使用RSA算法生成密钥对
        self.private_key_PEM = self.key.exportKey('OpenSSH')  # 导出私钥为OpenSSH格式
        self.public_key_PEM = self.key.publickey().exportKey('OpenSSH')  # 导出公钥为OpenSSH格式

    def encrypt(self, data):  # 加密
        cipher = PKCS1_OAEP.new(self.key)  # 创建加密对象
        return cipher.encrypt(data)  # 使用加密对象加密数据

    def decrypt(self, data):  # 解密
        cipher = PKCS1_OAEP.new(self.key)  # 创建解密对象
        return cipher.decrypt(data)  # 使用解密对象解密数据

    def save_to_file(self, path):  # 保存密钥对到文件
        self.private_key_path = os.path.join(path, "priv.key")  # 设置私钥文件路径
        self.public_key_path = os.path.join(path, "public.key")  # 设置公钥文件路径

        with open(self.private_key_path, 'w') as content_file:  # 打开私钥文件
            chmod(self.private_key_path, 600)  # 设置私钥文件权限为 -rw-------
            content_file.write(self.private_key_PEM)  # 写入私钥PEM

        with open(self.public_key_path, 'w') as content_file:  # 打开公钥文件
            content_file.write(self.public_key_PEM)  # 写入公钥PEM


if __name__ == "__main__":
    cipher = assymetric()  # 创建assymetric对象
    cipher.generate_keys()  # 生成密钥对
    print(cipher.private_key_PEM)  # 打印出私钥PEM
    print(cipher.public_key_PEM)  # 打印出公钥PEM
