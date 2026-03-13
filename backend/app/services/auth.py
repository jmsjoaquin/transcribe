from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.repositories import user as user_repository
from app.schemas.auth import UserLogin, UserRegister


class AuthError(Exception):
    pass


def register_user(db: Session, payload: UserRegister) -> User:
    normalized_email = payload.email.lower()
    existing_user = user_repository.get_by_email(db, normalized_email)
    if existing_user is not None:
        raise AuthError("A user with that email already exists.")

    user = user_repository.create(
        db,
        email=normalized_email,
        hashed_password=hash_password(payload.password),
        given_name=payload.given_name,
        last_name=payload.last_name,
    )
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, payload: UserLogin) -> tuple[User, str]:
    user = user_repository.get_by_email(db, payload.email.lower())
    if user is None or not verify_password(payload.password, user.hashed_password):
        raise AuthError("Invalid email or password.")

    if not user.is_active:
        raise AuthError("This user account is inactive.")

    token, _ = create_access_token(str(user.id))
    return user, token
