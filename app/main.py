from fastapi import FastAPI
from authentication.api.api import router as auth_router
from hero.api.api import router as hero_router
from event.api.api import router as event_router
from schedule.api.api import router as event_schedule_router
from database.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()


app.include_router(auth_router)
app.include_router(hero_router)
app.include_router(event_router)
app.include_router(event_schedule_router)
@app.get("/")
def root():
    return {"msg": "API running"}
