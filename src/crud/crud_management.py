from typing import List
from sqlalchemy import select
from fastapi import HTTPException

from src.models.request import RequestFrom, RequestStatus
from src.models.worker import Role
from src.database import AsyncSession
from src.crud import CompanyCRUD, UserCRUD
from src import schemas, models


class ManagementCRUD:

    @classmethod
    async def get_invite_by_id(cls, db: AsyncSession, invite_id: int) -> models.Request:
        result = await db.execute(select(models.Request).filter(models.Request.id == invite_id))
        result = result.scalars().first()
        if not result:
            raise HTTPException(status_code=404, detail="Not Found Invite")
        return result

    @classmethod
    async def get_invites_by_user_id(cls, db: AsyncSession, user_id) -> List[models.Request]:
        result = await db.execute(select(models.Request).filter(
            (models.Request.user_id == user_id) &
            (models.Request.request_from == RequestFrom.company) &
            (models.Request.status == RequestStatus.pending)
        ))
        return result.scalars().all()

    @classmethod
    async def get_invite_by_user_id_and_company_id(
            cls, db: AsyncSession, user_id: int, company_id: int
    ) -> models.Request:
        result = await db.execute(select(models.Request).filter(
            (models.Request.user_id == user_id) & (models.Request.company_id == company_id)
        ))
        return result.scalars().first()

    @classmethod
    async def create_invite(
            cls, db: AsyncSession, user_id: int, company_id: int, owner_id: int
    ) -> models.Request:
        if user_id == owner_id:
            raise HTTPException(status_code=400, detail="You cannot invite yourself")

        invite_exist = await cls.get_invite_by_user_id_and_company_id(db=db, user_id=user_id, company_id=company_id)
        if invite_exist:
            raise HTTPException(status_code=400, detail="The user is already invited")

        company = await CompanyCRUD.get_company_by_id(db=db, company_id=company_id)

        owner = await CompanyCRUD.get_owner_by_company_id(db=db, company_id=company_id)
        if owner.id is not owner_id:
            raise HTTPException(status_code=403, detail="You are not the owner of this company")

        worker_exist = await CompanyCRUD.get_worker_by_user_id_and_company_id(
            db=db, user_id=user_id, company_id=company_id
        )
        if worker_exist:
            raise HTTPException(status_code=400, detail="The user is already an employee of the company")

        user = await UserCRUD.get_user(db=db, user_id=user_id)

        invite = models.Request(
            company=company,
            user=user,
            request_from=RequestFrom.company
        )

        db.add(invite)
        await db.commit()
        await db.refresh(invite)
        return invite

    @classmethod
    async def update_invite(
            cls, db: AsyncSession, invite_id: int, user_id: int, status: RequestStatus
    ) -> models.Request:
        invite_exist = await cls.get_invite_by_id(db=db, invite_id=invite_id)

        if invite_exist.user_id is not user_id:
            raise HTTPException(status_code=400, detail="You don't have this invite")

        invite_exist.status = status

        await db.commit()
        await db.refresh(invite_exist)
        return invite_exist

    @classmethod
    async def get_request_by_id(
            cls, db: AsyncSession, request_id: int
    ) -> models.Request:
        result = await db.execute(select(models.Request).filter(models.Request.id == request_id))
        result = result.scalars().first()
        if not result:
            raise HTTPException(status_code=404, detail="Not Found Request")
        return result

    @classmethod
    async def get_requests_by_company_id_and_status(
            cls, db: AsyncSession, company_id: int, status: RequestStatus
    ) -> List[models.Request]:
        result = await db.execute(select(models.Request).filter(
            (models.Request.company_id == company_id) &
            (models.Request.status == status) &
            (models.Request.request_from == RequestFrom.user)
        ))
        return result.scalars().all()

    @classmethod
    async def get_request_by_user_id_and_company_id(
            cls, db: AsyncSession, user_id: int, company_id: int
    ) -> models.Request:
        result = await db.execute(select(models.Request).filter(
                (models.Request.company_id == company_id) &
                (models.Request.user_id == user_id) &
                (models.Request.request_from == RequestFrom.user)
            )
        )
        return result.scalars().first()

    @classmethod
    async def create_request(
            cls, db: AsyncSession, company_id: int, user_id: int
    ) -> models.Request:
        request_exist = await cls.get_request_by_user_id_and_company_id(
            db=db, user_id=user_id, company_id=company_id
        )
        if request_exist:
            raise HTTPException(status_code=400, detail="The request has already been sent")

        company = await CompanyCRUD.get_company_by_id(db=db, company_id=company_id)

        worker_exist = await CompanyCRUD.get_worker_by_user_id_and_company_id(
            db=db, user_id=user_id, company_id=company_id
        )
        if worker_exist:
            raise HTTPException(status_code=400, detail="The user is already an employee of the company")

        user = await UserCRUD.get_user(db=db, user_id=user_id)

        request = models.Request(
            company=company,
            user=user,
            request_from=RequestFrom.user
        )

        db.add(request)
        await db.commit()
        await db.refresh(request)
        return request

    @classmethod
    async def update_request(
            cls, db: AsyncSession, request_id: int, owner_id: int, status: RequestStatus
    ) -> models.Request:
        request_exist = await cls.get_request_by_id(db=db, request_id=request_id)

        owner = await CompanyCRUD.get_owner_by_company_id(db=db, company_id=request_exist.company_id)
        if owner.id is not owner_id:
            raise HTTPException(status_code=403, detail="You are not the owner of this company")

        request_exist.status = status

        await db.commit()
        await db.refresh(request_exist)
        return request_exist
