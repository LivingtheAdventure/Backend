from typing import List
from uuid import UUID

from pydantic import BaseModel


class FavouriteToggleRequest(BaseModel):
    event_id: UUID


class FavouriteStatusResponse(BaseModel):
    event_id: UUID
    is_favourite: bool


class FavouriteListResponse(BaseModel):
    favourites: List[UUID]
