from fastapi import FastAPI
from router.glossary import router as glossary_router
from core.logger import logger

app = FastAPI()

app.include_router(glossary_router, prefix="/glossary")

@app.get("/")
def root():
    logger.info("Root endpoint accessed.")
    return {"message": "Financial Intelligence Hub is running!"}

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting the server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)