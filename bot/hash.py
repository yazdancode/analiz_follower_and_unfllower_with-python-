import bcrypt
from cryptography.fernet import Fernet, InvalidToken
from decouple import config

FERNET_KEY = config("FERNET_KEY")
cipher = Fernet(FERNET_KEY.encode())


def encrypt_password(password: str) -> str:
    """رمزنگاری پسورد با Fernet"""
    encrypted = cipher.encrypt(password.encode("utf-8"))
    return encrypted.decode("utf-8")


def fix_padding(s: str) -> str:
    """اصلاح padding برای base64"""
    return s + "=" * (-len(s) % 4)


def decrypt_password(encrypted_password: str) -> str | None:
    """رمزگشایی پسورد رمزنگاری‌شده با مدیریت خطا"""
    try:
        fixed = fix_padding(encrypted_password)
        decrypted = cipher.decrypt(fixed.encode("utf-8"))
        return decrypted.decode("utf-8")
    except InvalidToken:
        print("❌ رمز نامعتبر یا خراب است")
        return None


def hash_phone(phone: str) -> str:
    """هش کردن شماره تلفن با bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(phone.encode("utf-8"), salt)
    return hashed.decode("utf-8")  # نباید بریده بشه


def verify_phone(phone: str, hashed_phone: str) -> bool:
    """بررسی تطابق شماره تلفن با هش‌شده‌اش"""
    return bcrypt.checkpw(phone.encode("utf-8"), hashed_phone.encode("utf-8"))
