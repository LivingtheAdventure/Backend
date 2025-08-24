from fastapi import FastAPI
from authentication.api.api import router as auth_router
from database.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth_router)

@app.get("/")
def root():
    return {"msg": "API running"}
