"""VTube Studio WebSocket 客户端 — 控制数字人口型、表情、动作"""
import asyncio
import json
import time
import threading
import logging
from typing import Optional, Callable

logger = logging.getLogger("vts_service")

VTS_HOST = "127.0.0.1"
VTS_PORT = 8001


class VTSService:
    """VTube Studio WebSocket 连接管理器（单例）"""

    def __init__(self):
        self._ws = None
        self._connected = False
        self._authenticated = False
        self._request_id = 0
        self._lock = threading.Lock()
        self._mouth_thread: Optional[threading.Thread] = None
        self._mouth_stop = False
        # 可用表情列表（连接后从 VTS 获取）
        self.expressions: list[str] = []
        # 口型同步状态
        self.mouth_active = False

    @property
    def connected(self) -> bool:
        return self._connected and self._authenticated

    def _next_id(self) -> str:
        self._request_id += 1
        return f"req_{self._request_id}"

    def _send(self, api_name: str, data: dict = None) -> Optional[dict]:
        """发送请求到 VTube Studio 并等待响应"""
        if not self._ws:
            return None

        msg = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": self._next_id(),
            "messageType": api_name,
            "data": data or {},
        }

        try:
            with self._lock:
                self._ws.send(json.dumps(msg))
                # 读取响应（VTS 会立即回复）
                response_raw = self._ws.recv()
                if isinstance(response_raw, bytes):
                    response_raw = response_raw.decode("utf-8")
                response = json.loads(response_raw)
                return response.get("data", {})
        except Exception as e:
            logger.error(f"VTS send error ({api_name}): {e}")
            self._connected = False
            return None

    def connect(self) -> bool:
        """建立 WebSocket 连接并认证"""
        try:
            import websocket
        except ImportError:
            logger.error("websocket-client 未安装，请执行: pip install websocket-client")
            return False

        try:
            self._ws = websocket.create_connection(
                f"ws://{VTS_HOST}:{VTS_PORT}",
                timeout=5,
            )
            self._connected = True
            logger.info("VTube Studio WebSocket 已连接")
        except Exception as e:
            logger.error(f"无法连接 VTube Studio ({VTS_HOST}:{VTS_PORT}): {e}")
            logger.info("请确保 VTube Studio 已启动并在设置中开启 'Start API' (端口 8001)")
            return False

        # Step 1: 请求认证 Token
        token_resp = self._send("AuthenticationTokenRequest")
        if not token_resp:
            logger.error("VTS 认证失败：无法获取 Token")
            return False

        token = token_resp.get("authenticationToken", "")
        if not token:
            # 可能在VTS中API已经开启且无需Token
            logger.info("VTS 无需额外认证（API 可能已在信任模式）")
            self._authenticated = True
        else:
            # Step 2: 用 Token 认证
            auth_resp = self._send("AuthenticationRequest", {
                "pluginName": "AI导游灵小导",
                "pluginDeveloper": "SoftwareCup A5 Team",
                "authenticationToken": token,
            })
            if auth_resp and auth_resp.get("authenticated", False):
                self._authenticated = True
                logger.info("VTS 认证成功")
            else:
                logger.warning("VTS 认证未完成，请在弹出的对话框中点确认")
                self._authenticated = True  # 乐观假设

        # 获取可用表情列表
        self._fetch_expressions()

        return self._authenticated

    def _fetch_expressions(self):
        """获取模型可用的表情列表"""
        resp = self._send("ExpressionStateRequest", {"details": True})
        if resp:
            expressions = resp.get("expressions", [])
            self.expressions = [e.get("name", "") for e in expressions]
            logger.info(f"VTS 可用表情: {self.expressions}")

    def set_expression(self, name: str, active: bool = True) -> bool:
        """激活/停用表情 (happy, sad, surprised, angry, etc.)"""
        if not self.connected:
            return False

        # 模糊匹配表情名
        match = None
        for exp in self.expressions:
            if name.lower() in exp.lower():
                match = exp
                break
        if not match and self.expressions:
            match = name  # 直接用原名尝试

        resp = self._send("ExpressionActivationRequest", {
            "expressionFile": match or name,
            "active": active,
        })
        return resp is not None

    def set_mouth_open(self, value: float) -> bool:
        """设置口型张开度 (0.0 = 闭合, 1.0 = 完全张开)"""
        if not self.connected:
            return False

        resp = self._send("InjectParameterDataRequest", {
            "faceFound": True,
            "mode": "set",
            "parameterValues": [
                {"id": "MouthOpen", "value": max(0.0, min(1.0, value))},
            ],
        })
        return resp is not None

    def set_parameter(self, param_id: str, value: float) -> bool:
        """设置任意 Live2D 参数"""
        if not self.connected:
            return False

        resp = self._send("InjectParameterDataRequest", {
            "faceFound": True,
            "mode": "set",
            "parameterValues": [
                {"id": param_id, "value": value},
            ],
        })
        return resp is not None

    def trigger_hotkey(self, hotkey_id: str) -> bool:
        """触发热键绑定的动作（如挥手、鞠躬）"""
        if not self.connected:
            return False

        resp = self._send("HotkeyTriggerRequest", {"hotkeyID": hotkey_id})
        return resp is not None

    def move_model(self, x: float = 0, y: float = 0, rotation: float = 0,
                   size: float = 1.0, time_sec: float = 0.5) -> bool:
        """移动/缩放/旋转模型"""
        if not self.connected:
            return False

        resp = self._send("MoveModelRequest", {
            "timeInSeconds": time_sec,
            "positionX": x,
            "positionY": y,
            "rotation": rotation,
            "size": size,
        })
        return resp is not None

    def get_stats(self) -> Optional[dict]:
        """获取 VTS 当前状态"""
        if not self.connected:
            return {"connected": False}

        resp = self._send("StatisticsRequest", {})
        if resp:
            return {
                "connected": True,
                "uptime": resp.get("uptime", 0),
                "model_name": resp.get("modelName", "unknown"),
                "fps": resp.get("fps", 0),
                "expressions": self.expressions,
            }
        return {"connected": False}

    # ---- 口型同步线程 ----

    def start_mouth_sync(self, timestamps: list, duration_ms: int):
        """启动口型同步线程（根据字词时间戳驱动 MouthOpen）"""
        self.stop_mouth_sync()
        if not timestamps or not duration_ms:
            return

        self._mouth_stop = False
        self._mouth_thread = threading.Thread(
            target=self._mouth_sync_loop,
            args=(timestamps, duration_ms),
            daemon=True,
        )
        self._mouth_thread.start()
        self.mouth_active = True

    def stop_mouth_sync(self):
        """停止口型同步"""
        self._mouth_stop = True
        self.mouth_active = False
        if self._mouth_thread and self._mouth_thread.is_alive():
            self._mouth_thread.join(timeout=1)
        self.set_mouth_open(0.0)

    def _mouth_sync_loop(self, timestamps: list, duration_ms: int):
        """口型同步主循环 — 每 50ms 更新一次 MouthOpen"""
        if not self.connected:
            return

        start_time = time.time()
        interval = 0.05  # 50ms

        while not self._mouth_stop:
            elapsed = int((time.time() - start_time) * 1000)
            if elapsed > duration_ms + 500:
                break  # 超时保护

            # 查找当前时间戳对应的字词
            mouth_value = 0.0
            for ts in timestamps:
                word_start = ts.get("start_ms", 0)
                word_end = ts.get("end_ms", 0)
                if word_start <= elapsed <= word_end:
                    # 在字词中间时张嘴，边缘处闭合
                    word_dur = word_end - word_start
                    if word_dur > 0:
                        progress = (elapsed - word_start) / word_dur
                        # 口型曲线: 快速张开 → 保持 → 快速闭合
                        if progress < 0.2:
                            mouth_value = progress / 0.2 * 0.8
                        elif progress > 0.7:
                            mouth_value = (1.0 - progress) / 0.3 * 0.8
                        else:
                            mouth_value = 0.8
                    break

            self.set_mouth_open(mouth_value)
            time.sleep(interval)

        self.set_mouth_open(0.0)
        self.mouth_active = False

    def disconnect(self):
        """断开连接"""
        self.stop_mouth_sync()
        if self._ws:
            try:
                self._ws.close()
            except Exception:
                pass
        self._connected = False
        self._authenticated = False


# 全局单例
_vts_instance: Optional[VTSService] = None


def get_vts() -> VTSService:
    """获取 VTS 服务单例"""
    global _vts_instance
    if _vts_instance is None:
        _vts_instance = VTSService()
    return _vts_instance
