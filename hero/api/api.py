
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from database.database import get_db
from hero.service.service import (
    get_heroes, get_hero_by_id, get_hero_by_uuid,
    create_hero, update_hero, delete_hero, get_heroes_by_type
)
from hero.schema.schema import HeroOut, HeroCreate, HeroUpdate

router = APIRouter(prefix="/heroes", tags=["heroes"])

@router.get("/", response_model=List[HeroOut])
def list_heroes(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    return get_heroes(db, skip=skip, limit=limit)

@router.get("/{hero_id}", response_model=HeroOut)
def read_hero(hero_id: int, db: Session = Depends(get_db)):
    db_hero = get_hero_by_id(db, hero_id)
    if not db_hero:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hero not found")
    return db_hero

@router.get("/by-uuid/{hero_uuid}", response_model=HeroOut)
def read_hero_by_uuid(hero_uuid: UUID, db: Session = Depends(get_db)):
    db_hero = get_hero_by_uuid(db, hero_uuid)
    if not db_hero:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hero not found")
    return db_hero

# ✅ NEW ENDPOINT
@router.get("/by-type/{hero_type}", response_model=List[HeroOut])
def read_heroes_by_type(hero_type: str, db: Session = Depends(get_db)):
    heroes = get_heroes_by_type(db, hero_type)
    if not heroes:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No heroes found for type '{hero_type}'")
    return heroes

@router.post("/", response_model=HeroOut, status_code=status.HTTP_200_OK)
def create_new_hero(payload: HeroCreate, db: Session = Depends(get_db)):
    created = create_hero(db, payload)
    return created

@router.put("/{hero_id}", response_model=HeroOut)
def update_existing_hero(hero_id: int, payload: HeroUpdate, db: Session = Depends(get_db)):
    db_hero = get_hero_by_id(db, hero_id)
    if not db_hero:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hero not found")
    updated = update_hero(db, db_hero, payload)
    return updated

@router.delete("/{hero_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_hero(hero_id: int, db: Session = Depends(get_db)):
    db_hero = get_hero_by_id(db, hero_id)
    if not db_hero:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hero not found")
    delete_hero(db, db_hero)
    return
