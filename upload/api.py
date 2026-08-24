import uuid
import os

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Form,
    Query,
    HTTPException,
    Depends,
)

from sqlalchemy.orm import Session

from database.database import get_db
from admin.service.service import get_current_admin
from logs.service.service import create_user_action_log

from upload.storage import supabase

router = APIRouter(tags=["Data Upload"])


BUCKET = "LivingDev"

ALLOWED_FOLDERS = {
    "cover",
    "poster",
    "gallery_image",
    "promo_video",
}


@router.post("/upload/image")
async def upload_image(
    file: UploadFile = File(...),
    folder: str = Form(...),
    admin_id: str = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    if folder not in ALLOWED_FOLDERS:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Invalid folder. Allowed folders: "
                f"{', '.join(sorted(ALLOWED_FOLDERS))}"
            ),
        )

    filename = None

    try:
        extension = os.path.splitext(file.filename)[1]

        filename = f"{folder}/{uuid.uuid4()}{extension}"

        file_bytes = await file.read()

        upload_response = supabase.storage.from_(BUCKET).upload(
            path=filename,
            file=file_bytes,
            file_options={
                "content-type": file.content_type,
                "upsert": "false",
            },
        )

        print(upload_response)

        public_url = supabase.storage.from_(BUCKET).get_public_url(filename)

        create_user_action_log(
            db=db,
            user_id=admin_id,
            action="FILE_UPLOADED",
            entity="STORAGE",
            entity_id=filename,
            description=(
                f"File '{file.filename}' was uploaded " f"successfully to '{folder}'"
            ),
        )

        return {
            "success": True,
            "folder": folder,
            "filename": filename,
            "url": public_url,
        }

    except Exception:
        db.rollback()

        create_user_action_log(
            db=db,
            user_id=admin_id,
            action="FILE_UPLOADED",
            entity="STORAGE",
            entity_id=filename,
            description=(f"Failed to upload file " f"'{file.filename}' to '{folder}'"),
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to upload file",
        )


@router.get("/storage/search")
def search_files(
    folder: str = Query(...),
    q: str = Query(..., min_length=3),
):
    if folder not in ALLOWED_FOLDERS:
        raise HTTPException(
            status_code=400,
            detail="Invalid folder",
        )

    try:
        result = supabase.storage.from_(BUCKET).list(folder)

        q = q.lower()

        files = []

        for item in result:
            name = item["name"]

            if q in name.lower():
                files.append(
                    {
                        "filename": name,
                        "url": (
                            supabase.storage.from_(BUCKET).get_public_url(
                                f"{folder}/{name}"
                            )
                        ),
                    }
                )

        return {
            "success": True,
            "folder": folder,
            "count": len(files),
            "results": files,
        }

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to search storage",
        )
