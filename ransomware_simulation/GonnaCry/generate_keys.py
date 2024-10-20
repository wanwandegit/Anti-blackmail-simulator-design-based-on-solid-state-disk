import base64
import os
from Crypto.Random import get_random_bytes

def generate_key(bits, encode=False):
    #generated = crypto.Random.DevURandomRNG()
    #content = generated.read(bits)
    content = get_random_bytes(bits)

    # 如果 encode 参数为 True，则返回经过 base64 编码的密钥
    if(encode):
        return base64.b64encode(content)

    return content

if __name__ == "__main__":
    print(generate_key(32))
