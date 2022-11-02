from fastapi import APIRouter, Depends, HTTPException, Response, status

from src import schemas, models
from src.crud import ManagementCRUD, UserCRUD, CompanyCRUD
from src.database import AsyncSession, get_db_session
from src.routes.dependencies import get_current_user

router = APIRouter(
    prefix="/management",
    tags=["management"],
    responses={404: {"description": "Not Found"}}
)


@router.post("/create_invite", response_model=schemas.Response, status_code=status.HTTP_201_CREATED)
async def create_invite_to_company(
        company_id: int,
        user_id: int,
        db: AsyncSession = Depends(get_db_session),
        current_user: models.User = Depends(get_current_user)
) -> schemas.Response:
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot invite yourself")

    for worker in current_user.workers:
        if worker.company.id == company_id:
            worker = await CompanyCRUD.get_worker_by_user_id_and_company_id(
                db=db, user_id=current_user.id, company_id=company_id
            )

            if worker.is_owner:
                worker_exist = await CompanyCRUD.get_worker_by_user_id_and_company_id(
                    db=db, user_id=user_id, company_id=company_id
                )
                if worker_exist:
                    raise HTTPException(status_code=400, detail="The user is already an employee of the company")

                user_already_invited = await ManagementCRUD.get_invited_user(
                    db=db, user_id=user_id, company_id=company_id
                )
                if user_already_invited:
                    raise HTTPException(status_code=400, detail="The user is already invited")

                invited_user = await UserCRUD.get_user(db=db, user_id=user_id)
                invite = await ManagementCRUD.create_invite(db=db, user=invited_user, company=worker.company)
                if invite:
                    return schemas.Response(
                        status_code=status.HTTP_201_CREATED,
                        body="Success created invite"
                    )
                else:
                    raise HTTPException(status_code=500, detail="Internal Server Error")

            else:
                raise HTTPException(status_code=400, detail="You are not owner")

    raise HTTPException(status_code=404, detail="Not Found Company")


@router.patch("/accept_invite", response_model=schemas.Response, status_code=status.HTTP_201_CREATED)
async def accept_invite_to_company(
        invite_id: int,
        db: AsyncSession = Depends(get_db_session),
        current_user: models.User = Depends(get_current_user)
) -> schemas.Response:
    for invite in current_user.invites:
        if (invite.id == invite_id) and (invite.accepted is False) and (invite.rejected is False):
            result_update = await ManagementCRUD.update_invite(db=db, invite=invite, accepted=True)
            result_create = await CompanyCRUD.create_worker_in_company(
                db=db, company=invite.company, user=invite.user, is_admin=False, is_owner=False
            )
            if result_update and result_create:
                return schemas.Response(
                    status_code=status.HTTP_201_CREATED,
                    body="Invitation successfully accepted"
                )
            else:
                raise HTTPException(status_code=500, detail="Internal Server Error")
        else:
            raise HTTPException(status_code=404, detail="Not Found Invite")


@router.patch("/cancel_invite", response_model=schemas.Response, status_code=status.HTTP_201_CREATED)
async def cancel_invite_to_company(
        invite_id: int,
        db: AsyncSession = Depends(get_db_session),
        current_user: models.User = Depends(get_current_user)
) -> schemas.Response:
    for invite in current_user.invites:
        if (invite.id == invite_id) and (invite.accepted is False) and (invite.rejected is False):
            result = await ManagementCRUD.update_invite(db=db, invite=invite, rejected=True)
            if result:
                return schemas.Response(
                    status_code=status.HTTP_201_CREATED,
                    body="Invitation canceled successfully"
                )
            else:
                raise HTTPException(status_code=500, detail="Internal Server Error")
        else:
            raise HTTPException(status_code=404, detail="Not Found Invite")


@router.patch("/assign_admin", response_model=schemas.Response, status_code=status.HTTP_201_CREATED)
async def assign_admin_to_company(
        user_id: int,
        company_id: int,
        db: AsyncSession = Depends(get_db_session),
        current_user: models.User = Depends(get_current_user)
) -> schemas.Response:
    for worker in current_user.workers:
        if worker.company.id == company_id:

            if worker.is_owner:
                worker_exist = await CompanyCRUD.get_worker_by_user_id_and_company_id(
                    db=db, user_id=user_id, company_id=company_id
                )
                if not worker_exist:
                    raise HTTPException(status_code=400, detail="The user is not an employee of the company")
                result = await CompanyCRUD.update_worker_admin(
                    db=db, user_id=user_id, company_id=company_id, is_admin=True
                )
                if result:
                    return schemas.Response(
                        status_code=status.HTTP_201_CREATED,
                        body="Admin successfully added"
                    )
                else:
                    raise HTTPException(status_code=500, detail="Internal Server Error")

            else:
                raise HTTPException(status_code=400, detail="You are not owner")

    raise HTTPException(status_code=404, detail="Not Found Company")


@router.patch("/remove_admin", response_model=schemas.Response, status_code=status.HTTP_201_CREATED)
async def remove_admin_from_company(
        user_id: int,
        company_id: int,
        db: AsyncSession = Depends(get_db_session),
        current_user: models.User = Depends(get_current_user)
):
    for worker in current_user.workers:
        if worker.company.id == company_id:

            if worker.is_owner:
                worker_exist = await CompanyCRUD.get_worker_by_user_id_and_company_id(
                    db=db, user_id=user_id, company_id=company_id
                )
                if not worker_exist:
                    raise HTTPException(status_code=400, detail="The user is not an employee of the company")
                result = await CompanyCRUD.update_worker_admin(
                    db=db, user_id=user_id, company_id=company_id, is_admin=False
                )
                if result:
                    return schemas.Response(
                        status_code=status.HTTP_201_CREATED,
                        body="Admin successfully removed"
                    )
                else:
                    raise HTTPException(status_code=500, detail="Internal Server Error")
            else:
                raise HTTPException(status_code=400, detail="You are not owner")

    raise HTTPException(status_code=404, detail="Not Found Company")


@router.post("/apply_to_join", response_model=schemas.Response, status_code=status.HTTP_201_CREATED)
async def apply_to_join_the_company(
        company_id: int,
        db: AsyncSession = Depends(get_db_session),
        current_user: models.User = Depends(get_current_user)
) -> schemas.Response:
    for request in current_user.requests:
        if request.company.id == company_id:
            raise HTTPException(status_code=400, detail="The request has already been sent")

    for worker in current_user.workers:
        if worker.company == company_id:
            raise HTTPException(status_code=400, detail="You are already an employee of this company")
        company = await CompanyCRUD.get_company_by_id(db=db, company_id=company_id)
        result = await ManagementCRUD.create_request_to_company(db=db, company=company, user=current_user)
        if result:
            return schemas.Response(
                status_code=status.HTTP_201_CREATED,
                body="Request sent successfully"
            )
        else:
            raise HTTPException(status_code=500, detail="Internal Server Error")

    raise HTTPException(status_code=404, detail="Not Found Company")


@router.patch("/accept_joining", response_model=schemas.Response, status_code=status.HTTP_201_CREATED)
async def accept_joining_to_company(
        request_id: int,
        db: AsyncSession = Depends(get_db_session),
        current_user: models.User = Depends(get_current_user)
) -> schemas.Response:
    where_im_owner = await CompanyCRUD.get_workers_where_im_owner(db=db, user_id=current_user.id)
    for worker in where_im_owner:
        for request in worker.company.requests:
            if (request.id == request_id) and (request.accepted is False) and (request.rejected is False):
                result_update = await ManagementCRUD.update_request(db=db, request=request, accepted=True)
                result_create = await CompanyCRUD.create_worker_in_company(
                    db=db, company=request.company, user=request.user, is_admin=False, is_owner=False
                )
                if result_update and result_create:
                    return schemas.Response(
                        status_code=status.HTTP_201_CREATED,
                        body="Request successfully accepted"
                    )
                else:
                    raise HTTPException(status_code=500, detail="Internal Server Error")
            else:
                raise HTTPException(status_code=404, detail="Not Found Request")


@router.patch("/cancel_joining")
async def cancel_joining_to_company(
        request_id: int,
        db: AsyncSession = Depends(get_db_session),
        current_user: models.User = Depends(get_current_user)
):
    where_im_owner = await CompanyCRUD.get_workers_where_im_owner(db=db, user_id=current_user.id)
    for worker in where_im_owner:
        for request in worker.company.requests:
            if (request.id == request_id) and (request.accepted is False) and (request.rejected is False):
                result_update = await ManagementCRUD.update_request(db=db, request=request, rejected=True)
                if result_update:
                    return schemas.Response(
                        status_code=status.HTTP_201_CREATED,
                        body="Request canceled successfully"
                    )
                else:
                    raise HTTPException(status_code=500, detail="Internal Server Error")
            else:
                raise HTTPException(status_code=404, detail="Not Found Request")


@router.delete("/delete_worker", response_model=schemas.Response, status_code=status.HTTP_200_OK)
async def delete_worker_from_company(
        company_id: int,
        user_id: int,
        db: AsyncSession = Depends(get_db_session),
        current_user: models.User = Depends(get_current_user)
):
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot delete yourself")

    for company in current_user.companies:
        if company.id == company_id:
            worker = await CompanyCRUD.get_worker_by_user_id_and_company_id(
                db=db, user_id=current_user.id, company_id=company_id
            )

            if worker.is_owner:
                worker_exist = await CompanyCRUD.get_worker_by_user_id_and_company_id(
                    db=db, user_id=user_id, company_id=company_id
                )
                if not worker_exist:
                    raise HTTPException(status_code=400, detail="The user is not an employee of the company")

                await CompanyCRUD.delete_worker(db=db, worker=worker_exist)
                return schemas.Response(
                    status_code=status.HTTP_200_OK,
                    body="Success delete worker"
                )
            else:
                raise HTTPException(status_code=400, detail="You are not owner")

