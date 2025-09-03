from cryptography.fernet import Fernet

key = Fernet.generate_key()
cipher = Fernet(key)

text = "mypassword"
encrypted = cipher.encrypt(text.encode())
print("Encrypted:", encrypted.decode())

# حالا با همون کلید رمزگشایی کن
decrypted = cipher.decrypt(encrypted).decode()
print("Decrypted:", decrypted)
