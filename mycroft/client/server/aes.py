from Crypto.Cipher import AES
from Crypto import Random
secret_message = b'Attack at dawn'
key = Random.get_random_bytes(32)

iv = Random.new().read(AES.block_size)
iv_size = len(iv)

cipher = AES.new(key, AES.MODE_CFB, iv)

ciphertext = iv + cipher.encrypt(secret_message)

print "Encrypted: " + ciphertext
print "Decrypted: " + cipher.decrypt(ciphertext)[iv_size:]