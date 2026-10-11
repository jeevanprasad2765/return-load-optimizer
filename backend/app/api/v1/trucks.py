import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.database import get_db
from app.api.deps import get_current_user, require_role
from app.models.user import User, UserRole
from app.models.truck import Truck
from app.schemas.truck import TruckCreate, TruckResponse, TruckUpdate

router = APIRouter()

@router.get("", response_model=List[TruckResponse])
async def list_trucks(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Truck)
    if current_user.role == UserRole.CARRIER:
        stmt = stmt.where(Truck.carrier_id == current_user.id)
    res = await db.execute(stmt)
    return res.scalars().all()

@router.post("", response_model=TruckResponse, status_code=status.HTTP_201_CREATED)
async def create_truck(
    truck_in: TruckCreate,
    current_user: User = Depends(require_role(UserRole.CARRIER)),
    db: AsyncSession = Depends(get_db)
):
    # Check registration number uniqueness
    stmt = select(Truck).where(Truck.registration_number == truck_in.registration_number)
    existing = (await db.execute(stmt)).scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Truck with registration number '{truck_in.registration_number}' already exists"
        )

    truck = Truck(
        id=str(uuid.uuid4()),
        carrier_id=current_user.id,
        registration_number=truck_in.registration_number.upper(),
        vehicle_type=truck_in.vehicle_type.lower(),
        max_capacity_kg=truck_in.max_capacity_kg,
        model_name=truck_in.model_name
    )
    db.add(truck)
    await db.commit()
    await db.refresh(truck)
    return truck

@router.delete("/{truck_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_truck(
    truck_id: str,
    current_user: User = Depends(require_role(UserRole.CARRIER)),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Truck).where(Truck.id == truck_id, Truck.carrier_id == current_user.id)
    truck = (await db.execute(stmt)).scalar_one_or_none()
    if not truck:
        raise HTTPException(status_code=404, detail="Truck not found")
    await db.delete(truck)
    await db.commit()
