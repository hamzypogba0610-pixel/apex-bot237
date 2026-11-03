from fastapi import FastAPI

app = FastAPI(title="APEX-BI")


@app.get("/")
def root():
    return {"message": "APEX-BI bot is alive", "version": "0.1.0"}


@app.get("/healthz")
def healthz():
    return {"status": "ok"}
