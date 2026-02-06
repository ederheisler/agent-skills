# src/items/router.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.database import get_db
from src.items import schemas, models

router = APIRouter(prefix="/items", tags=["items"])


@router.get("", response_model=list[schemas.ItemResponse])
async def list_items(
    skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(models.Item).offset(skip).limit(limit))
    return result.scalars().all()


@router.get("/{item_id}", response_model=schemas.ItemResponse)
async def get_item(item_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Item).where(models.Item.id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.post(
    "", response_model=schemas.ItemResponse, status_code=status.HTTP_201_CREATED
)
async def create_item(item_in: schemas.ItemCreate, db: AsyncSession = Depends(get_db)):
    item = models.Item(**item_in.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item
