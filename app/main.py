from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .database import Base, engine
from .api import routes_investigations

# Create DB tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="FinSpectra — Multi-Agent Investigation & Planning Engine",
    description="LangGraph Task-Driven Financial Crime Investigation Engine",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routers
app.include_router(routes_investigations.router, prefix="/api/investigations", tags=["Investigations"])

@app.get("/api/health")
def health():
    return {"status": "online", "version": "2.4.1", "llm_mode": "mock" if settings.mock_llm_mode else "groq"}
