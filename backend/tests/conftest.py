import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database import Base, get_db
from backend.main import app
from backend.services.storage import get_upload_dir
from backend.services.detection import RawDetection, get_detector



class FakeDetector:
    def detect(self, image_path):
        return [
            RawDetection("Person", 0.90, 10, 20, 110, 220),
            RawDetection("Hardhat", 0.80, 30, 20, 60, 45),
            RawDetection("NO-Safety Vest", 0.55, 15, 80, 100, 160),  # flagged (>= 0.40)
            RawDetection("NO-Safety Vest", 0.33, 15, 80, 100, 160),  # stored, not flagged
        ]

@pytest.fixture()
def client(tmp_path):
    # Fresh in-memory database for every test
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,  # keeps one shared connection so the memory DB persists
    )
    TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_upload_dir] = lambda: tmp_path / "uploads"
    app.dependency_overrides[get_detector] = lambda: FakeDetector()
    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)