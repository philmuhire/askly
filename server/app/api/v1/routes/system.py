from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.main import get_db
from app.models.system import System
from app.schemas.system import SystemCreate, SystemResponse


system_router = APIRouter(
    prefix="/organizations/{organization_id}/systems",
    tags=["Systems"],
)


@system_router.post(
    "",
    response_model=SystemResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_system(
    organization_id: UUID,
    system_data: SystemCreate,
    db: Session = Depends(get_db),
):
    system = System(
        id=uuid4(),
        organization_id=organization_id,
        name=system_data.name,
        description=system_data.description,
        system_type=system_data.system_type,
    )

    db.add(system)
    db.commit()
    db.refresh(system)

    return system


@system_router.get(
    "",
    response_model=list[SystemResponse],
)
def get_systems(
    organization_id: UUID,
    db: Session = Depends(get_db),
):
    systems = db.scalars(
        select(System)
        .where(System.organization_id == organization_id)
        .order_by(System.created_at.desc())
    ).all()

    return systems


@system_router.get(
    "/{system_id}",
    response_model=SystemResponse,
)
def get_system(
    organization_id: UUID,
    system_id: UUID,
    db: Session = Depends(get_db),
):
    system = db.scalar(
        select(System).where(
            System.id == system_id,
            System.organization_id == organization_id,
        )
    )

    if not system:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="System not found",
        )

    return system