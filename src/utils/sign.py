import hashlib


def generate_sign(params: dict, secret_key: str = "s3cr3tk3y") -> str:
    sorted_keys = sorted(params.keys())
    sign_str = "&".join(f"{k}={params[k]}" for k in sorted_keys)
    sign_str += secret_key
    return hashlib.md5(sign_str.encode()).hexdigest()


def verify_sign(params: dict, sign: str, secret_key: str = "s3cr3tk3y") -> bool:
    expected_sign = generate_sign(params, secret_key)
    return hmac.compare_digest(expected_sign, sign)


def md5(text: str) -> str:
    return hashlib.md5(text.encode()).hexdigest()
