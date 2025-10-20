from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from authentication.api.api import router as auth_router
from hero.api.api import router as hero_router
from event.api.api import router as event_router
from schedule.api.api import router as event_schedule_router
from special.api.api import router as special_router
from database.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()

# ✅ Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
   allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://frontend-three-mu-66.vercel.app" # <-- Your new frontend URL
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Routers
app.include_router(auth_router)
app.include_router(hero_router)
app.include_router(event_router)
app.include_router(event_schedule_router)
app.include_router(special_router)

@app.get("/")
def root():
    return {"msg": "API running"}
