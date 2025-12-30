from fastapi import FastAPI

app = FastAPI(
    title="AI-GRC Control Tower",
    description="Regulator-first AI governance platform",
    version="0.1.0",
)


@app.get("/health")
def health():
    return {"status": "ok"}
