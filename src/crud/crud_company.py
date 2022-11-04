from typing import List
from sqlalchemy import select
from fastapi import HTTPException

from src.database import AsyncSession
from src.models.worker import Role
from src import schemas, models


class CompanyCRUD:

    @classmethod
    async def get_company_by_id(cls, db: AsyncSession, company_id: int) -> models.Company:
        result = await db.execute(select(models.Company).filter(models.Company.id == company_id))
        result = result.scalars().first()
        if result is None:
            raise HTTPException(status_code=404, detail="Not Found Company")
        return result

    @classmethod
    async def get_companies_by_user_id(cls, db: AsyncSession, user_id: int) -> List[models.Company]:
        result = await db.execute(select(models.Company).join(models.Worker).filter(models.Worker.user_id == user_id))
        return result.scalars().all()

    @classmethod
    async def get_all_public_companies(cls, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[models.Company]:
        result = await db.execute(select(models.Company).filter(
            models.Company.hidden == False
        ).offset(skip).limit(limit))
        return result.scalars().all()

    @classmethod
    async def get_owner_by_company_id(cls, db: AsyncSession, company_id: int) -> models.User:
        result = await db.execute(select(models.User).join(models.Worker).filter(
            (models.Worker.company_id == company_id) & (models.Worker.role == Role.owner)
        ))
        return result.scalars().first()

    @classmethod
    async def get_company_where_im_owner(cls, db: AsyncSession, user_id) -> List[models.Worker]:
        result = await db.execute(select(models.Company).join(models.Worker).filter(
                (models.Worker.user_id == user_id) & (models.Worker.role == Role.owner)
            )
        )
        return result.scalars().all()

    @classmethod
    async def get_worker_by_user_id_and_company_id(cls, db: AsyncSession, user_id: int, company_id: int) -> models.Worker:
        result = await db.execute(select(models.Worker).filter(
            (models.Worker.user_id == user_id) & (models.Worker.company_id == company_id)
        ))
        return result.scalars().first()

    @classmethod
    async def create_company(
            cls, db: AsyncSession, company_data: schemas.CreateCompany, user: schemas.User
    ) -> models.Company:

        company = models.Company(
            title=company_data.title,
            description=company_data.description
        )

        db.add(company)
        await db.commit()
        await db.refresh(company)

        await cls.create_worker_in_company(
            db=db,
            company=company,
            user=user,
            role=Role.owner
        )
        return company

    @classmethod
    async def create_worker_in_company(
            cls,
            db: AsyncSession,
            company: models.Company,
            user: models.User,
            role: Role
    ) -> models.Worker:
        worker = models.Worker(
            company=company,
            user=user,
            role=role
        )

        db.add(worker)
        await db.commit()
        await db.refresh(worker)
        return worker

    @classmethod
    async def update_worker_admin(
            cls, db: AsyncSession, user_id: int, company_id: int, owner_id: int, role: Role
    ) -> models.Worker:
        company = await cls.get_company_by_id(db=db, company_id=company_id)

        owner = await cls.get_owner_by_company_id(db=db, company_id=company.id)
        if owner.id is not owner_id:
            raise HTTPException(status_code=403, detail="You are not the owner of this company")

        worker = await cls.get_worker_by_user_id_and_company_id(db=db, user_id=user_id, company_id=company_id)
        if worker is None:
            raise HTTPException(status_code=404, detail="Not Found Worker")

        worker.role = role

        await db.commit()
        await db.refresh(worker)
        return worker

    @classmethod
    async def update_company_status(
            cls, db: AsyncSession, company_id: int, user_id: int, change_data: schemas.ChangeCompanyStatus
    ) -> schemas.Company:
        company = await cls.get_company_by_id(db=db, company_id=company_id)
        if company is None:
            raise HTTPException(status_code=404, detail="Not Found Company")

        owner = await cls.get_owner_by_company_id(db=db, company_id=company_id)
        if owner.id is not user_id:
            raise HTTPException(status_code=403, detail="You are not the owner of this company")

        company.hidden = change_data.hidden

        await db.commit()
        await db.refresh(company)
        return company

    @classmethod
    async def update_company_info(
            cls, db: AsyncSession, company_id: int, user_id, update_data: schemas.CompanyInfoUpdate
    ) -> schemas.Company:
        if (update_data.title and update_data.description) is None:
            raise HTTPException(status_code=400, detail="There is not enough data to update")

        company = await cls.get_company_by_id(db=db, company_id=company_id)
        if company is None:
            raise HTTPException(status_code=404, detail="Not Found Company")

        owner = await cls.get_owner_by_company_id(db=db, company_id=company_id)
        if owner.id is not user_id:
            raise HTTPException(status_code=403, detail="You are not the owner of this company")

        if update_data.title:
            company.title = update_data.title
        if update_data.description:
            company.description = update_data.description

        await db.commit()
        await db.refresh(company)
        return company


    @classmethod
    async def delete_company(cls, db: AsyncSession, company_id: int, user_id: int):
        company = await cls.get_company_by_id(db=db, company_id=company_id)
        if company is None:
            raise HTTPException(status_code=404, detail="Not Found Company")

        owner = await cls.get_owner_by_company_id(db=db, company_id=company_id)
        if owner.id is not user_id:
            raise HTTPException(status_code=403, detail="You are not the owner of this company")

        await cls.delete_all_workers_in_company(db=db, company_id=company.id)
        await db.delete(company)
        await db.commit()

    @classmethod
    async def delete_all_workers_in_company(cls, db: AsyncSession, company_id: int):
        result = await db.execute(select(models.Worker).filter(models.Worker.company_id == company_id))
        workers = result.scalars().all()
        for worker in workers:
            await db.delete(worker)
            await db.commit()

    @classmethod
    async def delete_worker(cls, db: AsyncSession, company_id: int, user_id: int, owner_id: int):
        if user_id == owner_id:
            raise HTTPException(status_code=400, detail="You cannot delete yourself")

        company = await cls.get_company_by_id(db=db, company_id=company_id)

        owner = await cls.get_owner_by_company_id(db=db, company_id=company.id)
        if owner.id is not owner_id:
            raise HTTPException(status_code=403, detail="You are not the owner of this company")

        worker = await cls.get_worker_by_user_id_and_company_id(db=db, user_id=user_id, company_id=company_id)
        if worker is None:
            raise HTTPException(status_code=404, detail="Not Found Worker")

        await db.delete(worker)
        await db.commit()
