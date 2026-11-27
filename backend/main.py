from fastapi import FastAPI

from backend import models  # noqa: F401  (import so tables are registered)
from backend.database import Base, engine
from backend.routers import analysis, inspections, projects, uploads

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Construction Site Inspection API")

app.include_router(projects.router)
app.include_router(inspections.router)
app.include_router(uploads.router)
app.include_router(analysis.router)

@app.get("/health")
def health():
    return {"status": "ok"}

...
