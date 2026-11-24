from fastapi import FastAPI

app = FastAPI(title="Construction Site Inspection API")


@app.get("/health")
def health():
    return {"status": "ok"}