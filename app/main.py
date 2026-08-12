from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from authentication.api.api import router as auth_router
from hero.api.api import router as hero_router
from event.api.api import router as event_router
from schedule.api.api import router as event_schedule_router
from special.api.api import router as special_router
from favourite.api.api import router as favourite_router
from database.database import Base, engine
from favourite.model.model import Favourite  # noqa: F401
from admin.api.api import router as admin_router
from upload.api import router as upload_router
from metadata.api.api import router as metadata_router
from payment.api.api import router as payment_router

Base.metadata.create_all(bind=engine)

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        "https://frontend-2-0-ebon.vercel.app",
        "https://livingtheadventure.in",
        "https://www.livingtheadventure.in",
        "https://admin-portal-livingtheadventure.vercel.app",
    ],
    allow_origin_regex=r"https://([a-z0-9-]+\.)*vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Routers
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(hero_router)
app.include_router(event_router)
app.include_router(event_schedule_router)
app.include_router(special_router)
app.include_router(favourite_router)
app.include_router(upload_router)
app.include_router(metadata_router)
app.include_router(payment_router)


@app.get("/")
def root():
    return {"msg": "API running"}
