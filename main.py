from fastapi import FastAPI
import uvicorn
from core.database import Base, engine

app = FastAPI(title="Globalworth ESG API")

@app.get("/")
async def root():
    return {"message": "Globalworth ESG API is running"}

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    import asyncio
    asyncio.run(create_tables())
    uvicorn.run(app, host="0.0.0.0", port=8000)