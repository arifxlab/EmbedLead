from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import InvalidCredentialsError, UserAlreadyExistsError
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.repositories.user import UserRepository


class AuthService:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self.session = session
        self.repository = UserRepository(session)

    async def register_user(
        self,
        tenant_id: UUID,
        email: str,
        password: str,
    ) -> User:
        existing_user = await self.repository.get_by_email(email)

        if existing_user is not None:
            raise UserAlreadyExistsError

        user = await self.repository.create(
            tenant_id=tenant_id,
            email=email,
            password_hash=hash_password(password),
        )

        await self.session.commit()
        await self.session.refresh(user)

        return user

    async def authenticate_user(
        self,
        email: str,
        password: str,
    ) -> User:
        user = await self.repository.get_by_email(email)

        if user is None or not verify_password(password, user.password_hash):
            raise InvalidCredentialsError

        return user

    def create_access_token(
        self,
        user_id: UUID,
        tenant_id: UUID,
    ) -> str:
        return create_access_token(
            subject=str(user_id),
            tenant_id=str(tenant_id),
        )
