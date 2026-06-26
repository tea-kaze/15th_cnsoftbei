"""API 安全中间件：速率限制 + 管理后台鉴权（纯 ASGI 实现，兼容 Python 3.13）"""
import os
import json
import time
from collections import defaultdict
from starlette.types import ASGIApp, Scope, Receive, Send
from starlette.responses import JSONResponse
from dotenv import load_dotenv

load_dotenv()

# 管理后台 API Key（从环境变量读取，默认值仅开发使用）
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", "admin-lingshan-2024")

# 速率限制配置
RATE_LIMIT_WINDOW = 60        # 时间窗口（秒）
RATE_LIMIT_MAX_REQUESTS = 30   # 每窗口最大请求数

# 存储每个 IP 的请求时间戳
_request_log: dict[str, list[float]] = defaultdict(list)


def _clean_old_entries(ip: str, window: float):
    """清理窗口外的旧记录"""
    now = time.time()
    _request_log[ip] = [t for t in _request_log[ip] if now - t < window]


class AdminAuthMiddleware:
    """管理后台 API 鉴权中间件（纯 ASGI）"""

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path = scope.get("path", "")
        method = scope.get("method", "")

        # 需要鉴权的路径前缀
        protected_prefixes = ("/api/admin", "/api/knowledge")
        if any(path.startswith(p) for p in protected_prefixes):
            if method in ("POST", "PUT", "DELETE", "PATCH"):
                # 从 headers 中提取 API Key
                headers = dict(scope.get("headers", []))
                api_key = headers.get(b"x-admin-key", b"").decode()
                if api_key != ADMIN_API_KEY:
                    response = JSONResponse(
                        status_code=401,
                        content={"detail": "需要有效的管理员 API Key"}
                    )
                    await response(scope, receive, send)
                    return

        await self.app(scope, receive, send)


class RateLimitMiddleware:
    """基于 IP 的速率限制中间件（纯 ASGI）"""

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path = scope.get("path", "")

        # 仅限制需要 LLM/TTS 的端点
        rate_limited_prefixes = ("/api/chat/ask", "/api/tts/synthesize")
        if any(path.startswith(p) for p in rate_limited_prefixes):
            # 获取客户端 IP
            client = scope.get("client")
            ip = client[0] if client else "unknown"
            now = time.time()
            _clean_old_entries(ip, RATE_LIMIT_WINDOW)

            if len(_request_log[ip]) >= RATE_LIMIT_MAX_REQUESTS:
                response = JSONResponse(
                    status_code=429,
                    content={
                        "detail": f"请求过于频繁，请稍后再试（每分钟最多 {RATE_LIMIT_MAX_REQUESTS} 次）"
                    }
                )
                await response(scope, receive, send)
                return
            _request_log[ip].append(now)

        await self.app(scope, receive, send)
