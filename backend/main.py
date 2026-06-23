from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import chat, knowledge, tts, admin, recommend, vts

app = FastAPI(title="AI智能导游")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(knowledge.router)
app.include_router(tts.router)
app.include_router(admin.router)
app.include_router(recommend.router)
app.include_router(vts.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
