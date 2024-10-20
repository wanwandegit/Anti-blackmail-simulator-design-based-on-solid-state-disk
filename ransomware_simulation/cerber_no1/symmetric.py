import base64
import hashlib

import generate_keys

from Crypto import Random
from Crypto.Cipher import AES
# import generate_keys

class AESCipher(object):

    def __init__(self, key):
        # 初始化方法，在这里我们使用了SHA-256哈希函数来处理密钥
        self.bs = 32 # 块大小
        self.key = hashlib.sha256(key).digest()# 生成32字节的密钥

    def encrypt(self, raw):
        # 加密方法，使用AES的CBC模式来加密
        raw = self._pad(raw) # 填充明文
        iv = Random.new().read(AES.block_size)# 生成随机的初始化向量
        cipher = AES.new(self.key, AES.MODE_CBC, iv)# 创建AES加密器
        return base64.b64encode(iv + cipher.encrypt(raw))# 返回加密的密文

    def decrypt(self, enc, decryption_key=None):
        enc = base64.b64decode(enc)# 对密文进行base64解码
        iv = enc[:AES.block_size] # 提取初始化向量
        if(decryption_key):
            self.key = hashlib.sha256(decryption_key).digest()
            # 如果传入了解密密钥，则更新密钥
        cipher = AES.new(self.key, AES.MODE_CBC, iv)# 创建AES解密器
        return self._unpad(cipher.decrypt(enc[AES.block_size:])) # 返回解密后的明文
    def _pad(self, s):
        

        padding = self.bs - len(s) % self.bs
        return s + padding * bytes([padding])

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])] # 返回去除填充后的字符串

if __name__ == "__main__":
    key = generate_keys.generate_key(32, True)
    cipher_obj = AESCipher(key)
    print("chave: {}".format(key))
    enc = cipher_obj.encrypt("TESTE CRYPTO")
    print(enc)

    back = cipher_obj.decrypt(enc, key)

    print(back)
