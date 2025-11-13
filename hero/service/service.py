from sqlalchemy.orm import Session
from uuid import uuid4
from typing import List, Optional
from fastapi import HTTPException, status

from hero.model.model import Hero
from hero.schema.schema import HeroCreate, HeroUpdate

def get_heroes(db: Session, skip: int = 0, limit: int = 100) -> List[Hero]:
    return db.query(Hero).offset(skip).limit(limit).all()

def get_hero_by_id(db: Session, hero_id: int) -> Optional[Hero]:
    return db.query(Hero).filter(Hero.id == hero_id).first()

def get_hero_by_uuid(db: Session, hero_uuid):
    return db.query(Hero).filter(Hero.hero_id == hero_uuid).first()

def create_hero(db: Session, hero_in: HeroCreate) -> Hero:
    # FIX: Check if a hero with the provided UUID already exists
    if hero_in.hero_id:
        existing_hero = get_hero_by_uuid(db, hero_in.hero_id)
        if existing_hero:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Hero with hero_id '{hero_in.hero_id}' already exists."
            )

    hero_data = hero_in.model_dump(exclude_unset=True)

    # Convert AnyUrl to str
    if "video_url" in hero_data and hero_data["video_url"] is not None:
        hero_data["video_url"] = str(hero_data["video_url"])
    if "thumbnail_image_url" in hero_data and hero_data["thumbnail_image_url"] is not None:
        hero_data["thumbnail_image_url"] = str(hero_data["thumbnail_image_url"])

    # Convert 'active' from boolean to string if necessary
    if "active" in hero_data and isinstance(hero_data["active"], bool):
        hero_data["active"] = str(hero_data["active"])

    # ensure hero_id exists if not provided
    if not hero_data.get("hero_id"):
        hero_data["hero_id"] = uuid4()

    db_obj = Hero(**hero_data)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update_hero(db: Session, db_obj: Hero, hero_in: HeroUpdate) -> Hero:
    update_data = hero_in.model_dump(exclude_unset=True)

    # Handle URL conversion for updates as well
    if "video_url" in update_data and update_data["video_url"] is not None:
        update_data["video_url"] = str(update_data["video_url"])
    if "thumbnail_image_url" in update_data and update_data["thumbnail_image_url"] is not None:
        update_data["thumbnail_image_url"] = str(update_data["thumbnail_image_url"])
        
    # Convert 'active' from boolean to string if necessary
    if "active" in update_data and isinstance(update_data["active"], bool):
        update_data["active"] = str(update_data["active"])

    for field, value in update_data.items():
        setattr(db_obj, field, value)

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def delete_hero(db: Session, db_obj: Hero):
    db.delete(db_obj)
    db.commit()
    return

def get_heroes_by_type(db: Session, hero_type: str) -> List[Hero]:
    return db.query(Hero).filter(Hero.hero_type == hero_type).all()
