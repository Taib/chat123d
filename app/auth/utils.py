from passlib.context import CryptContext
from app.constants import AppConfig
from app.auth.models import TokenData


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_session_token(payload: TokenData) -> str:
    """
    Create a session token.
    """
    import jwt
    from datetime import datetime, timedelta

    # Define the secret key and algorithm
    secret = AppConfig().jwt_secret
    algorithm = AppConfig().jwt_algorithm
    # Define the expiration time
    expiration = datetime.utcnow() + timedelta(seconds=AppConfig().jwt_expiration)
    # Create the token
    token = jwt.encode(
        {
            "exp": expiration,
            "iat": datetime.utcnow(),
            "sub": payload.id,
            "role": payload.role,
            "username": payload.username,
            "email": payload.email,
            "address": payload.address,
            "max_week_loans": payload.max_week_loans,
        },
        secret,
        algorithm=algorithm,
    )
    return token


def decode_session_token(token: str) -> dict[str, str]:
    """
    Decode a session token.
    """
    import jwt
    from fastapi import HTTPException, status

    # Define the secret key and algorithm
    secret = AppConfig().jwt_secret
    algorithm = AppConfig().jwt_algorithm
    try:
        # Decode the token
        payload = jwt.decode(token, secret, algorithms=[algorithm])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
