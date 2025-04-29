from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status

from app.auth.auth_guard import get_librarian_active_user, get_current_active_user
from app.loans.repository import LoanRepository
from app.loans.models import LoanCreate, LoanUpdateDue, LoanUpdateReturn
from app.loans.utils import post_loan_creation_process


loans_router = APIRouter(
    prefix="/loans",
    tags=["loans"],
)


@loans_router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_active_user)],
)
async def get_my_loans(
    repo: LoanRepository = Depends(),
):
    """
    Get all loans for the current user.
    """
    try:
        return repo.get_user_loans()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@loans_router.get(
    "/",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_librarian_active_user)],
)
async def get_loans(repo: LoanRepository = Depends()):
    """
    Get all loans.
    """
    try:
        return repo.get_all_loans()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@loans_router.get(
    "/{loan_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_librarian_active_user)],
)
async def get_loan(
    loan_id: str,
    repo: LoanRepository = Depends(),
):
    """
    Get a loan by ID.
    """
    try:
        loan = repo.get_loan(loan_id)
        if not loan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Loan not found",
            )
        return loan
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@loans_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_active_user)],
)
async def create_loan(
    *,
    loan: LoanCreate,
    repo: LoanRepository = Depends(),
    background_tasks: BackgroundTasks,
):
    """
    Create a new loan.
    """
    try:
        if repo.can_create(loan):
            result = repo.create_loan(loan)
            if result:
                background_tasks.add_task(
                    post_loan_creation_process,
                    loan=loan,
                )
            return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


def update_loan(
    *,
    loan: LoanUpdateReturn | LoanUpdateDue,
    repo: LoanRepository = Depends(),
):
    """
    Utility function to update a loan.
    This function is used by both update_loan_return and update_loan_due.
    """
    try:
        return repo.update_loan(loan)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@loans_router.put(
    "/return",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_librarian_active_user)],
)
async def update_loan_return(
    loan: LoanUpdateReturn,
    repo: LoanRepository = Depends(),
):
    """
    Update a loan returrn.
    Used by loaner or librarian to mark a loan as returned.
    """
    return update_loan(loan=loan, repo=repo)


@loans_router.put(
    "/due",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_librarian_active_user)],
)
async def update_loan_due(
    loan: LoanUpdateDue,
    repo: LoanRepository = Depends(),
):
    """
    Update a loan due date.
    Used by librarian to update the due date of a loan.
    """
    return update_loan(loan=loan, repo=repo)


@loans_router.delete(
    "/{loan_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_loan(
    loan_id: str,
    repo: LoanRepository = Depends(),
):
    """
    Delete a loan.
    """
    try:
        if not repo.delete_loan(loan_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Loan not found",
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
