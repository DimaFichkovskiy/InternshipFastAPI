from typing import List
from sqlalchemy import select, delete

from src.database import AsyncSession
from src import schemas, models


class CompanyCRUD:

    @classmethod
    async def get_company_by_id(cls, db: AsyncSession, company_id) -> models.Company:
        result = await db.execute(select(models.Company).filter(models.Company.id == company_id))
        return result.scalars().first()

    @classmethod
    async def get_all_public_companies(cls, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[models.Company]:
        result = await db.execute(select(models.Company).filter(models.Company.hidden == False).offset(skip).limit(limit))
        return result.scalars().all()

    @classmethod
    async def get_workers_where_im_owner(cls, db: AsyncSession, user_id) -> List[models.Worker]:
        result = await db.execute(select(models.Worker).filter(
                (models.Worker.user_id == user_id) & (models.Worker.is_owner == True)
            )
        )
        return result.scalars().all()

    @classmethod
    async def get_worker_by_user_id_and_company_id(cls, db: AsyncSession, user_id, company_id) -> models.Worker:
        result = await db.execute(select(models.Worker).filter(
                (models.Worker.user_id == user_id) & (models.Worker.company_id == company_id)
            )
        )
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
            is_owner=True,
            is_admin=False
        )
        return company

    @classmethod
    async def create_worker_in_company(
            cls, db: AsyncSession,
            company: models.Company,
            user: models.User,
            is_owner: bool = False,
            is_admin: bool = False
    ) -> models.Worker:
        worker = models.Worker(
            company=company,
            user=user,
            is_owner=is_owner,
            is_admin=is_admin,
        )

        db.add(worker)
        await db.commit()
        await db.refresh(worker)
        return worker

    @classmethod
    async def update_worker_admin(
            cls, db: AsyncSession, user_id: int, company_id: int, is_admin: bool
    ) -> models.Worker:
        worker = await cls.get_worker_by_user_id_and_company_id(db=db, user_id=user_id, company_id=company_id)
        worker.is_admin = is_admin

        await db.commit()
        await db.refresh(worker)
        return worker

    @classmethod
    async def update_company_status(
            cls, db: AsyncSession, company: schemas.Company, change_data: schemas.ChangeCompanyStatus
    ) -> schemas.Company:

        company.hidden = change_data.hidden

        await db.commit()
        await db.refresh(company)
        return company

    @classmethod
    async def update_company_info(
            cls, db: AsyncSession, company: schemas.Company, update_data: schemas.CompanyInfoUpdate
    ) -> schemas.Company:

        if update_data.title is not None:
            company.title = update_data.title
        if update_data.description is not None:
            company.description = update_data.description

        await db.commit()
        await db.refresh(company)
        return company

    @classmethod
    async def delete_company(cls, db: AsyncSession, company: models.Company):
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
    async def delete_worker(cls, db: AsyncSession, worker: schemas.Worker):
        await db.delete(worker)
        await db.commit()
