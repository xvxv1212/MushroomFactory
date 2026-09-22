from contextlib import asynccontextmanager
from pathlib import Path
import asyncio
import logging

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from database.connection import conn, database_is_available
from routes.admin_route import router

from routes.chat import router as chat_router
from routes.episodes import router as episode_router
from routes.sessions import router as session_router
from core.flow_trace import print_route_map


# Resolve paths from this file instead of from the shell's current directory.
# React source files under src/ are not browser-ready files; Vite's build output
# under dist/ is what FastAPI should serve.
FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"
FRONTEND_DIST = FRONTEND_DIR / "dist"
FRONTEND_INDEX = FRONTEND_DIST / "index.html"

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s %(name)s - %(message)s")
    )
    logger.addHandler(console_handler)
logger.propagate = False

@asynccontextmanager
async def lifespan(app_instance: FastAPI):
    # 개발/DB 연동 확인용: 실제 등록된 API 경로와 함수명을 서버 시작 시 출력합니다.
    print_route_map(app_instance)

    # DB 연결은 학생용 FastAPI가 뜨기 위한 선행조건이 아닙니다.
    # 별도 background task에서 확인하므로 PostgreSQL이 멈춰 있어도
    # /api/sessions, /api/chat 등 학생용 API는 즉시 서비스됩니다.
    app_instance.state.db_available = False

    async def database_monitor():
        initialized = False

        while True:
            try:
                db_ok = await asyncio.to_thread(database_is_available)

                if db_ok and not initialized:
                    await asyncio.to_thread(conn)
                    initialized = True
                    print("[DB] connection ready")

                app_instance.state.db_available = db_ok
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                app_instance.state.db_available = False
                print(
                    f"[DB] background warning: {type(exc).__name__}: {exc}"
                )

            await asyncio.sleep(15)

    monitor_task = asyncio.create_task(database_monitor())

    try:
        yield
    finally:
        monitor_task.cancel()
        try:
            await monitor_task
        except asyncio.CancelledError:
            pass


app = FastAPI(title="2Team API", lifespan=lifespan)


app.add_middleware(
    # 프론트엔드 개발 서버에서 백엔드 API를 호출할 수 있도록 CORS를 설정합니다.
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)
app.include_router(chat_router, prefix="/api")
app.include_router(session_router, prefix="/api")
app.include_router(episode_router, prefix="/api")


@app.get("/api/health")
def health():
    """학생용 API 프로세스와 DB 상태를 분리해서 확인합니다."""
    db_ok = bool(getattr(app.state, "db_available", False))
    logger.debug("app.health()")
    return {
        "api": "ok",
        "database": "ok" if db_ok else "unavailable",
        "student_service": "available"
    }

if (FRONTEND_DIST / "assets").is_dir():
    app.mount(
        "/assets",
        StaticFiles(directory=FRONTEND_DIST / "assets"),
        name="frontend-assets",
    )

@app.get("/")
async def frontend_index():
    logger.debug("app.frontend_index 실행")
    if not FRONTEND_INDEX.is_file():
        return {
            "message": "Frontend build not found. Run `npm run build` in frontend/ first."
        }
    return FileResponse(FRONTEND_INDEX)


@app.get("/{path:path}")
async def frontend_spa_fallback(path: str):
    logger.debug("app.frontend_spa_fallback 실행")
    """Let React Router handle client-side routes after a page refresh."""
    if not FRONTEND_INDEX.is_file():
        return {
            "message": "Frontend build not found. Run `npm run build` in frontend/ first."
        }
    return FileResponse(FRONTEND_INDEX)


if __name__ == "__main__":
    uvicorn.run(
                "app:app",
                host="127.0.0.1",
                port=8000,
                # Directly executing this file from an IDE can make uvicorn
                # watch an unrelated workspace root. Use the stable single
                # process mode here; use `uvicorn app:app --reload` from
                # backend/src when file watching is desired.
                reload=False
                )
