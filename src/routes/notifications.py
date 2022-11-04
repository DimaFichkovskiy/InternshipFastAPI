from typing import List
from fastapi import APIRouter, Depends, status

from src import schemas, models
from src.crud import CompanyCRUD, ManagementCRUD
from src.database import AsyncSession, get_db_session
from src.models.request import RequestStatus
from src.routes.dependencies import get_current_user

router = APIRouter(
    prefix="/notifications",
    tags=["notifications"],
    responses={404: {"description": "Not Found"}}
)


@router.get("/invitations", response_model=List[schemas.Invite], status_code=status.HTTP_200_OK)
async def read_all_invitations(
        db: AsyncSession = Depends(get_db_session),
        management_crud: ManagementCRUD = Depends(),
        current_user: models.User = Depends(get_current_user)
) -> List[schemas.Invite]:
    result = list()
    invites = await management_crud.get_invites_by_user_id(db=db, user_id=current_user.id)
    for invite in invites:
        result.append(schemas.Invite(
            id=invite.id,
            status=invite.status,
            company=schemas.InviteFrom(
                id=invite.company.id,
                title=invite.company.title
            )
        ))
    return result


@router.get("/request_to_company", response_model=List[schemas.Request], status_code=status.HTTP_200_OK)
async def request_for_join_to_company(
        company_crud: CompanyCRUD = Depends(),
        management_crud: ManagementCRUD = Depends(),
        db: AsyncSession = Depends(get_db_session),
        current_user: models.User = Depends(get_current_user)
) -> List[schemas.Request]:
    where_im_owner = await company_crud.get_company_where_im_owner(db=db, user_id=current_user.id)
    result = list()
    for company in where_im_owner:
        requests = await management_crud.get_requests_by_company_id_and_status(
            db=db, company_id=company.id, status=RequestStatus.pending
        )
        for request in requests:
            result.append(schemas.Request(
                    id=request.id,
                    status=request.status,
                    from_user=schemas.RequestFrom(
                        id=request.user_id,
                        email=request.user.email
                    ),
                    to_company=schemas.RequestTo(
                        id=request.company_id,
                        title=company.title
                    )
                )
            )
    return result
