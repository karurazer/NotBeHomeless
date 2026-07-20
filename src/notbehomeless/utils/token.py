import time

import jwt


def is_token_expired(token):
    payload = jwt.decode(token, options={"verify_signature": False})
    return time.time() > payload["exp"] - 300  # Consider token expired if it's within 5 minutes of expiring
