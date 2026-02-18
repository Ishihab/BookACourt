from fastapi import APIRouter, Depends, HTTPException, status
from src.router.depandency import SessionDep, get_current_active_user, get_current_active_superuser
from src.service import (
    create_resource_service,
    get_resource_by_id_service,
    delete_resource_service,
    update_resource_service,
    get_all_resources_service,
    get_resources_by_facility_id_service
)
from src.schemas import ResourceCreate, ResourceResponse, ResourceUpdate, PaginationParams
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID  
from typing import Annotated
from src.utils import get_pagination    


router = APIRouter(prefix="/api/v1/resources", tags=["resources"])

@router.get("/", response_model=list[ResourceResponse])
async def get_resources(
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    session: SessionDep,
    current_user: Annotated[ResourceResponse, Depends(get_current_active_superuser)]
):
    return await get_all_resources_service(session, pagination)

@router.get("/facility/{facility_id}", response_model=list[ResourceResponse])
async def get_resources_by_facility_id(
    facility_id: UUID,
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    session: SessionDep
):
    return await get_resources_by_facility_id_service(session, facility_id, pagination)

@router.post("/", response_model=ResourceResponse, status_code=201)
async def create_resource(
    resource_in: ResourceCreate,
    db: SessionDep,
    current_user: Annotated[ResourceResponse, Depends(get_current_active_superuser)]
):
    return await create_resource_service(db=db, resource_in=resource_in)


@router.get("/{resource_id}", response_model=ResourceResponse)
async def get_resource_by_id(resource_id: UUID, db: SessionDep):
    return await get_resource_by_id_service(db=db, resource_id=resource_id)

@router.put("/{resource_id}", response_model=ResourceResponse)
async def update_resource(
    resource_id: UUID,
    resource_in: ResourceUpdate,
    db: SessionDep,
    current_user: Annotated[ResourceResponse, Depends(get_current_active_superuser)]
):
    return await update_resource_service(db=db, resource_id=resource_id, resource_in=resource_in)


@router.delete("/{resource_id}", status_code=204)
async def delete_resource(
    resource_id: UUID,
    db: SessionDep,
    current_user: Annotated[ResourceResponse, Depends(get_current_active_superuser)]
):
    await delete_resource_service(db=db, resource_id=resource_id)
    return None


