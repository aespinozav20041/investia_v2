import base64
from typing import Optional

from cryptography.fernet import Fernet
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.broker import BrokerConnection


class BrokerService:
    def __init__(self) -> None:
        self.fernet = self._build_fernet()

    def _build_fernet(self) -> Fernet:
        # Fernet requires a 32-byte url-safe base64 key; derive from configured secret
        raw = settings.ENCRYPTION_SECRET_KEY.encode()
        key = base64.urlsafe_b64encode(raw[:32].ljust(32, b"0"))
        return Fernet(key)

    def encrypt(self, secret: str) -> str:
        return self.fernet.encrypt(secret.encode()).decode()

    def decrypt(self, secret: str) -> str:
        return self.fernet.decrypt(secret.encode()).decode()

    async def save_connection(
        self,
        db: AsyncSession,
        *,
        user_id: int,
        broker_name: str,
        api_key: str,
        api_secret: str,
        live_trading_enabled: bool = False,
    ) -> BrokerConnection:
        encrypted_key = self.encrypt(api_key)
        encrypted_secret = self.encrypt(api_secret)
        connection = BrokerConnection(
            user_id=user_id,
            broker_name=broker_name,
            encrypted_api_key=encrypted_key,
            encrypted_api_secret=encrypted_secret,
            is_live_trading_enabled=live_trading_enabled,
        )
        db.add(connection)
        await db.commit()
        await db.refresh(connection)
        return connection

    async def list_connections(self, db: AsyncSession, user_id: int) -> list[BrokerConnection]:
        res = await db.execute(select(BrokerConnection).where(BrokerConnection.user_id == user_id))
        return res.scalars().all()


broker_service = BrokerService()
