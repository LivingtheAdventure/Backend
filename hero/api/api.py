from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from database.database import get_db
from logs.service.service import create_user_action_log

from hero.service.service import (
    get_heroes,
    get_hero_by_id,
    get_hero_by_uuid,
    create_hero,
    update_hero,
    delete_hero,
    get_heroes_by_type,
)

from hero.schema.schema import HeroOut, HeroCreate, HeroUpdate
from admin.service.service import get_current_admin

router = APIRouter(prefix="/heroes", tags=["heroes"])


@router.get("/", response_model=List[HeroOut])
def list_heroes(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    return get_heroes(db, skip=skip, limit=limit)


@router.get("/{hero_id}", response_model=HeroOut)
def read_hero(
    hero_id: int,
    db: Session = Depends(get_db),
):
    db_hero = get_hero_by_id(db, hero_id)

    if not db_hero:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hero not found",
        )

    return db_hero


@router.get("/by-uuid/{hero_uuid}", response_model=HeroOut)
def read_hero_by_uuid(
    hero_uuid: UUID,
    db: Session = Depends(get_db),
):
    db_hero = get_hero_by_uuid(db, hero_uuid)

    if not db_hero:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hero not found",
        )

    return db_hero


@router.get("/by-type/{hero_type}", response_model=List[HeroOut])
def read_heroes_by_type(
    hero_type: str,
    db: Session = Depends(get_db),
):
    heroes = get_heroes_by_type(db, hero_type)

    if not heroes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No heroes found for type '{hero_type}'",
        )

    return heroes


@router.post("/", response_model=HeroOut, status_code=status.HTTP_200_OK)
def create_new_hero(
    payload: HeroCreate,
    db: Session = Depends(get_db),
    admin_id: str = Depends(get_current_admin),
):
    try:
        created = create_hero(db, payload)

        create_user_action_log(
            db=db,
            user_id=admin_id,
            action="HERO_CREATED",
            entity="HERO",
            entity_id=str(created.id),
            description=f"Hero '{created.title}' was created successfully",
        )

        return created

    except Exception:
        db.rollback()

        create_user_action_log(
            db=db,
            user_id=admin_id,
            action="HERO_CREATED",
            entity="HERO",
            description="Failed to create hero",
        )

        raise


@router.put("/{hero_id}", response_model=HeroOut)
def update_existing_hero(
    hero_id: int,
    payload: HeroUpdate,
    db: Session = Depends(get_db),
    admin_id: str = Depends(get_current_admin),
):
    db_hero = get_hero_by_id(db, hero_id)

    if not db_hero:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hero not found",
        )

    hero_title = db_hero.title

    try:
        updated = update_hero(db, db_hero, payload)

        create_user_action_log(
            db=db,
            user_id=admin_id,
            action="HERO_UPDATED",
            entity="HERO",
            entity_id=str(updated.id),
            description=f"Hero '{updated.title}' was updated successfully",
        )

        return updated

    except Exception:
        db.rollback()

        create_user_action_log(
            db=db,
            user_id=admin_id,
            action="HERO_UPDATED",
            entity="HERO",
            entity_id=str(hero_id),
            description=f"Failed to update hero '{hero_title}'",
        )

        raise


@router.delete("/{hero_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_hero(
    hero_id: int,
    db: Session = Depends(get_db),
    admin_id: str = Depends(get_current_admin),
):
    db_hero = get_hero_by_id(db, hero_id)

    if not db_hero:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hero not found",
        )

    hero_title = db_hero.title

    try:
        delete_hero(db, db_hero)

        create_user_action_log(
            db=db,
            user_id=admin_id,
            action="HERO_DELETED",
            entity="HERO",
            entity_id=str(hero_id),
            description=f"Hero '{hero_title}' was deleted successfully",
        )

        return

    except Exception:
        db.rollback()

        create_user_action_log(
            db=db,
            user_id=admin_id,
            action="HERO_DELETED",
            entity="HERO",
            entity_id=str(hero_id),
            description=f"Failed to delete hero '{hero_title}'",
        )

        raise
