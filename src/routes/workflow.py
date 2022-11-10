from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination import Page, paginate

from src import schemas
from src.crud import WorkflowCrud
from src.routes.dependencies import get_current_user

router = APIRouter(
    prefix="/workflow",
    tags=["workflow"],
    responses={404: {"description": "Not Found"}}
)


@router.post("/test", response_model=schemas.TestResponse, status_code=status.HTTP_201_CREATED)
async def passing_the_test(
        company_id: int,
        quiz_id: int,
        answers_data: List[schemas.AnswersFromUser],
        workflow_crud: WorkflowCrud = Depends(),
        current_user: schemas.User = Depends(get_current_user)
) -> schemas.TestResponse:
    general_result = await workflow_crud.get_general_result_by_user_and_company_id(
        user_id=current_user.id, company_id=company_id
    )

    if not general_result:
        general_result = await workflow_crud.create_general_result_for_user(
            answers_from_user=answers_data, company_id=company_id, quiz_id=quiz_id, user_id=current_user.id
        )

    else:
        general_result = await workflow_crud.update_general_result_for_user(
            answers_from_user=answers_data, company_id=company_id, quiz_id=quiz_id, user_id=current_user.id
        )

    return general_result
