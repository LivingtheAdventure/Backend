import uuid

from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from upload.storage import supabase

router = APIRouter()

BUCKET = "LivingDev"
ALLOWED_FOLDERS = {"cover", "poster", "gallery_image", "promo_video"}


@router.post("/upload/image")
async def upload_image(
    file: UploadFile = File(...),
    folder: str = Form("cover"),
):
    if folder not in ALLOWED_FOLDERS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid folder. Choose one of: {', '.join(sorted(ALLOWED_FOLDERS))}",
        )

    try:

        extension = file.filename.split(".")[-1]

        filename = f"{folder}/{uuid.uuid4()}.{extension}"

        file_bytes = await file.read()

        response = (
            supabase.storage
            .from_(BUCKET)
            .upload(
                filename,
                file_bytes,
                {
                    "content-type": file.content_type
                }
            )
        )

        public_url = (
            supabase.storage
            .from_(BUCKET)
            .get_public_url(filename)
        )

        return {
            "success": True,
            "url": public_url
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )