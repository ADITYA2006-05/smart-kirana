from __future__ import annotations

from sqlalchemy.orm import Session
from werkzeug.security import check_password_hash, generate_password_hash

from app.models import User
from app.utils import APIError
from app.utils.auth import issue_token


class AuthService:
    @staticmethod
    def ensure_default_admin(session: Session) -> None:
        from flask import current_app

        username = current_app.config["DEFAULT_ADMIN_USERNAME"]
        password = current_app.config["DEFAULT_ADMIN_PASSWORD"]

        existing = session.query(User).filter(User.username == username).first()
        if existing:
            return

        session.add(
            User(
                username=username,
                password_hash=generate_password_hash(password),
                is_active=True,
            )
        )

    @staticmethod
    def login(session: Session, username: str, password: str) -> dict:
        if not username or not password:
            raise APIError("username and password are required", status_code=400)

        user = session.query(User).filter(User.username == username.strip()).first()
        if not user or not user.is_active:
            raise APIError("Invalid credentials", status_code=401)

        if not check_password_hash(user.password_hash, password):
            raise APIError("Invalid credentials", status_code=401)

        token = issue_token(user.id, user.username)
        return {
            "token": token,
            "tokenType": "Bearer",
            "user": {
                "id": user.id,
                "username": user.username,
            },
        }
