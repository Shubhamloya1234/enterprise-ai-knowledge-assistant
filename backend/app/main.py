from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.auth import router as auth_router
from app.api.protected import router as protected_router
from app.api.rbac import router as rbac_router
from app.api.users import router as users_router
from app.api.rag import router as rag_router
from app.api.documents import router as documents_router
from app.api.agent import router as agent_router
from app.api.conversations import router as conversations_router


app = FastAPI(
    title="AI Enterprise Assistant",
    description="Enterprise AI Assistant with RAG, Agents and Tool Calling",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router)
app.include_router(protected_router)
app.include_router(rbac_router)
app.include_router(users_router)
app.include_router(rag_router)
app.include_router(documents_router)
app.include_router(agent_router)
app.include_router(conversations_router)

@app.get("/")
def root():
    return {
        "message": "AI Enterprise Assistant API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


 