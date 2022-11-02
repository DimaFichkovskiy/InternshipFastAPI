from typing import List
from fastapi import APIRouter, Depends, status

from src import schemas, models
from src.crud import CompanyCRUD, ManagementCRUD
from src.database import AsyncSession, get_db_session
from src.routes.dependencies import get_current_user

router = APIRouter(
    prefix="/notifications",
    tags=["notifications"],
    responses={404: {"description": "Not Found"}}
)


@router.get("/invitations", response_model=List[schemas.Invite], status_code=status.HTTP_200_OK)
async def read_all_invitations(
        current_user: models.User = Depends(get_current_user)
) -> List[schemas.Invite]:
    result = list()
    for invite in current_user.invites:
        result.append(schemas.Invite(
                id=invite.id,
                accepted=invite.accepted,
                rejected=invite.rejected,
                company=schemas.InviteFrom(
                    id=invite.company.id,
                    title=invite.company.title
                )
            )
        )
    return result


@router.get("/request_to_company", response_model=List[schemas.Request], status_code=status.HTTP_200_OK)
async def request_for_join_to_company(
        db: AsyncSession = Depends(get_db_session),
        current_user: models.User = Depends(get_current_user)
) -> List[schemas.Request]:
    where_im_owner = await CompanyCRUD.get_workers_where_im_owner(db=db, user_id=current_user.id)
    result = list()
    for worker in where_im_owner:
        requests = await ManagementCRUD.get_requests_by_user_id_and_company_id(
            db=db, company_id=worker.company.id, user_id=current_user.id
        )
        for request in requests:
            if request.company.id == worker.company.id:
                result.append(schemas.Request(
                        id=request.id,
                        accepted=request.accepted,
                        rejected=request.rejected,
                        from_user=schemas.RequestFrom(
                            id=request.user.id,
                            email=request.user.email
                        ),
                        to_company=schemas.RequestTo(
                            id=request.company.id,
                            title=request.company.title
                        )
                    )
                )
    return result
