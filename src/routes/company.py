from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination import Page, paginate

from src import schemas, models
from src.crud import CompanyCRUD
from src.database import AsyncSession, get_db_session
from src.routes.dependencies import get_current_user

router = APIRouter(
    prefix="/company",
    tags=["company"],
    responses={404: {"description": "Not Found"}}
)


@router.get("/all_companies", response_model=Page[schemas.Company], status_code=status.HTTP_200_OK)
async def get_all_companies(
        skip: int = 0,
        limit: int = 100,
        db: AsyncSession = Depends(get_db_session),
        current_user: models.Company = Depends(get_current_user)
):
    companies = await CompanyCRUD.get_all_public_companies(db=db, skip=skip, limit=limit)
    return paginate(companies)

@router.get("/my", response_model=List[schemas.Company])
async def get_my_companies(
        current_user: models.User = Depends(get_current_user)
) -> List[schemas.Company]:
    result = list()
    for worker in current_user.workers:
        result.append(worker.company)
    return result


@router.post("/create", response_model=schemas.Company)
async def create_company(
        company_data: schemas.CreateCompany,
        db: AsyncSession = Depends(get_db_session),
        current_user: schemas.User = Depends(get_current_user)
) -> schemas.Company:
    company = await CompanyCRUD.create_company(db=db, company_data=company_data, user=current_user)

    return schemas.Company(
        id=company.id,
        title=company.title,
        description=company.description,
        hidden=company.hidden
    )


@router.patch("/change_status", response_model=schemas.Company)
async def change_company_status(
        company_id: int,
        change_data: schemas.ChangeCompanyStatus,
        db: AsyncSession = Depends(get_db_session),
        current_user: models.User = Depends(get_current_user)
 ) -> schemas.Company:
    for worker in current_user.workers:
        if worker.company.id == company_id:
            if worker.is_owner:
                return await CompanyCRUD.update_company_status(db=db, company=worker.company, change_data=change_data)

            else:
                raise HTTPException(status_code=403, detail="You are not the owner of this company")

    raise HTTPException(status_code=404, detail="Not Found Company")


@router.patch("/update_info", response_model=schemas.Company)
async def update_company_info(
        company_id: int,
        update_data: schemas.CompanyInfoUpdate,
        db: AsyncSession = Depends(get_db_session),
        current_user: models.User = Depends(get_current_user)
):
    if update_data.title is None and update_data.description is None:
        raise HTTPException(status_code=400, detail="There is not enough data to update")

    for worker in current_user.workers:
        if worker.company.id == company_id:
            if worker.is_owner:
                return await CompanyCRUD.update_company_info(db=db, company=worker.company, update_data=update_data)

            else:
                raise HTTPException(status_code=403, detail="You are not the owner of this company")

    raise HTTPException(status_code=404, detail="Not Found Company")


@router.delete("/delete", response_model=schemas.CompanyDeleteResponse, status_code=status.HTTP_200_OK)
async def delete_company(
        company_id: int,
        db: AsyncSession = Depends(get_db_session),
        current_user: models.User = Depends(get_current_user)
) -> schemas.CompanyDeleteResponse:
    for worker in current_user.workers:
        if worker.company.id == company_id:
            if worker.is_owner:
                print(worker.company)
                await CompanyCRUD.delete_company(db=db, company=worker.company)
                return schemas.CompanyDeleteResponse(
                    status_code=status.HTTP_200_OK,
                    body="Success delete company"
                )

            else:
                raise HTTPException(status_code=403, detail="You are not the owner of this company")

    raise HTTPException(status_code=404, detail="Not Found Company")
