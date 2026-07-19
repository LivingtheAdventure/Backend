import uuid
import os
from fastapi import APIRouter, UploadFile, File, Form,Query, HTTPException

from upload.storage import supabase

router = APIRouter(tags=["Data Upload"])

BUCKET = "LivingDev"
ALLOWED_FOLDERS = {"cover", "poster", "gallery_image", "promo_video"}


@router.post("/upload/image")
async def upload_image(
    file: UploadFile = File(...),
    folder: str = Form(...),
):

    if folder not in ALLOWED_FOLDERS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid folder. Allowed folders: {', '.join(sorted(ALLOWED_FOLDERS))}"
        )

    try:

        extension = os.path.splitext(file.filename)[1]

        filename = f"{folder}/{uuid.uuid4()}{extension}"

        file_bytes = await file.read()

        upload_response = (
            supabase.storage
            .from_(BUCKET)
            .upload(
                path=filename,
                file=file_bytes,
                file_options={
                    "content-type": file.content_type,
                    "upsert": "false"
                }
            )
        )

        print(upload_response)

        public_url = (
            supabase.storage
            .from_(BUCKET)
            .get_public_url(filename)
        )

        return {
            "success": True,
            "folder": folder,
            "filename": filename,
            "url": public_url
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("/storage/search")
def search_files(
    folder: str = Query(...),
    q: str = Query(..., min_length=3)
):

    if folder not in ALLOWED_FOLDERS:
        raise HTTPException(
            status_code=400,
            detail="Invalid folder"
        )

    try:

        result = (
            supabase.storage
            .from_(BUCKET)
            .list(folder)
        )

        q = q.lower()

        files = []

        for item in result:

            name = item["name"]

            if q in name.lower():

                files.append({
                    "filename": name,
                    "url": supabase.storage
                        .from_(BUCKET)
                        .get_public_url(f"{folder}/{name}")
                })

        return {
            "success": True,
            "folder": folder,
            "count": len(files),
            "results": files
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )