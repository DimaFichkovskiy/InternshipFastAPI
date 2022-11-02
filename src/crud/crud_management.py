from typing import List
from sqlalchemy import select

from src.database import AsyncSession
from src import schemas, models


class ManagementCRUD:

    @classmethod
    async def get_invite_by_id(cls, db: AsyncSession, invite_id: int) -> models.Invite:
        result = await db.execute(select(models.Invite).filter(models.Invite.id == invite_id))
        return result.scalars().first()

    @classmethod
    async def get_invites_by_user_id(cls, db: AsyncSession, user_id) -> List[models.Invite]:
        result = await db.execute(select(models.Invite).filter(models.Invite.user_id == user_id))
        return result.scalars().all()

    @classmethod
    async def get_invited_user(cls, db: AsyncSession, user_id: int, company_id: int) -> models.User:
        result = await db.execute(select(models.User).filter(
                (models.Invite.user_id == user_id) & (models.Invite.company_id == company_id)
            )
        )
        return result.scalars().first()

    @classmethod
    async def create_invite(
            cls, db: AsyncSession, user: models.User, company: models.Company
    ) -> models.Invite:
        invite = models.Invite(
            company=company,
            user=user
        )

        db.add(invite)
        await db.commit()
        await db.refresh(invite)
        return invite

    @classmethod
    async def update_invite(
            cls, db: AsyncSession, invite: models.Invite, accepted: bool = False, rejected: bool = False
    ) -> models.Invite:

        if accepted:
            invite.accepted = accepted
        if rejected:
            invite.rejected = rejected

        await db.commit()
        await db.refresh(invite)
        return invite

    @classmethod
    async def get_requests_by_user_id_and_company_id(
            cls, db: AsyncSession, user_id: int, company_id: int
    ) -> List[models.Request]:
        result = await db.execute(select(models.Request).filter(
                (models.Company.id == company_id) & (models.User.id == user_id)
            )
        )
        return result.scalars().all()

    @classmethod
    async def create_request_to_company(
            cls, db: AsyncSession, company: models.Company, user: models.User
    ) -> models.Request:
        request = models.Request(
            company=company,
            user=user
        )

        db.add(request)
        await db.commit()
        await db.refresh(request)
        return request

    @classmethod
    async def update_request(
            cls, db: AsyncSession, request: models.Request, accepted: bool = False, rejected: bool = False
    ) -> models.Request:
        if accepted:
            request.accepted = accepted
        if rejected:
            request.rejected = rejected

        await db.commit()
        await db.refresh(request)
        return request
