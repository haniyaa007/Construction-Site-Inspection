from fastapi import FastAPI
from backend import models  # noqa: F401  (import so tables are registered)
from backend.database import Base, engine
from backend.routers import analysis, inspections, projects, uploads,  detections, issues, reports
from fastapi.middleware.cors import CORSMiddleware


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Construction Site Inspection API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(projects.router)
app.include_router(inspections.router)
app.include_router(uploads.router)
app.include_router(analysis.router)
app.include_router(detections.router)
app.include_router(issues.router)
app.include_router(reports.router)

@app.get("/health")
def health():
    return {"status": "ok"}

...
