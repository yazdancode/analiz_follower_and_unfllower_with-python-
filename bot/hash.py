import bcrypt


def hash_password(password: str) -> str:
    """هش کردن پسورد با bcrypt"""
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def check_password(password: str, hashed_password: str) -> bool:
    """بررسی درستی پسورد با bcrypt"""
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))
