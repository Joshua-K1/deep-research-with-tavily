from api.routes.research import router as research_router
from fastapi import FastAPI

app = FastAPI()

app.include_router(research_router, prefix="/research")


@app.get("/")
async def read_root():
    return {
        "message": "Welcome to the Research Agent API."
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
