"""交互日志与统计分析服务 — SQLite 持久化"""
import sqlite3
import json
import os
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "analytics.db")


def _now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """创建数据库和表（首次运行自动调用）"""
    conn = _get_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS chat_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            sources TEXT DEFAULT '',
            response_time_ms INTEGER DEFAULT 0,
            ip_address TEXT DEFAULT '',
            user_agent TEXT DEFAULT '',
            emotion_tag TEXT DEFAULT '',
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def log_interaction(question: str, answer: str, sources: list,
                    response_time_ms: int, ip_address: str = "",
                    user_agent: str = "", emotion_tag: str = ""):
    """记录一次问答交互"""
    init_db()
    conn = _get_conn()
    conn.execute(
        "INSERT INTO chat_logs (question, answer, sources, response_time_ms, "
        "ip_address, user_agent, emotion_tag, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (question, answer, json.dumps(sources, ensure_ascii=False),
         response_time_ms, ip_address, user_agent, emotion_tag, _now())
    )
    conn.commit()
    conn.close()


def get_dashboard_stats() -> dict:
    """仪表盘概览统计"""
    init_db()
    conn = _get_conn()
    today = datetime.now().strftime("%Y-%m-%d")
    week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

    today_count = conn.execute(
        "SELECT COUNT(*) FROM chat_logs WHERE created_at LIKE ?", (today + "%",)
    ).fetchone()[0]

    week_count = conn.execute(
        "SELECT COUNT(*) FROM chat_logs WHERE created_at >= ?", (week_ago,)
    ).fetchone()[0]

    total_count = conn.execute(
        "SELECT COUNT(*) FROM chat_logs"
    ).fetchone()[0]

    avg_ms_row = conn.execute(
        "SELECT AVG(response_time_ms) FROM chat_logs"
    ).fetchone()
    avg_response_ms = round(avg_ms_row[0], 0) if avg_ms_row[0] else 0

    unique_visitors = conn.execute(
        "SELECT COUNT(DISTINCT ip_address) FROM chat_logs WHERE created_at LIKE ?",
        (today + "%",)
    ).fetchone()[0]

    # 知识库统计
    knowledge_path = os.path.join(os.path.dirname(__file__), "..", "knowledge_index.json")
    doc_count = 0
    chunk_count = 0
    if os.path.exists(knowledge_path):
        with open(knowledge_path, "r", encoding="utf-8") as f:
            chunks = json.load(f)
        chunk_count = len(chunks)
        sources = set(c.get("source", "") for c in chunks)
        doc_count = len(sources)

    conn.close()
    return {
        "today_count": today_count,
        "week_count": week_count,
        "total_count": total_count,
        "avg_response_ms": avg_response_ms,
        "unique_visitors_today": unique_visitors,
        "doc_count": doc_count,
        "chunk_count": chunk_count,
    }


def get_popular_questions(limit: int = 10, days: int = 7) -> list:
    """热门问题 Top-N"""
    init_db()
    conn = _get_conn()
    since = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    rows = conn.execute(
        "SELECT question, COUNT(*) as cnt FROM chat_logs "
        "WHERE created_at >= ? "
        "GROUP BY question ORDER BY cnt DESC LIMIT ?",
        (since, limit)
    ).fetchall()
    conn.close()
    return [{"question": r["question"], "count": r["cnt"]} for r in rows]


def get_interaction_trend(days: int = 30) -> list:
    """每日交互趋势"""
    init_db()
    conn = _get_conn()
    since = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    rows = conn.execute(
        "SELECT SUBSTR(created_at, 1, 10) as date, COUNT(*) as cnt "
        "FROM chat_logs WHERE created_at >= ? "
        "GROUP BY date ORDER BY date",
        (since,)
    ).fetchall()
    conn.close()
    return [{"date": r["date"], "count": r["cnt"]} for r in rows]


def get_hourly_heatmap(date: str = None) -> list:
    """某日各时段交互量"""
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    init_db()
    conn = _get_conn()
    rows = conn.execute(
        "SELECT SUBSTR(created_at, 12, 2) as hour, COUNT(*) as cnt "
        "FROM chat_logs WHERE created_at LIKE ? "
        "GROUP BY hour ORDER BY hour",
        (date + "%",)
    ).fetchall()
    conn.close()
    return [{"hour": int(r["hour"]), "count": r["cnt"]} for r in rows]


def get_recent_interactions(page: int = 1, page_size: int = 20,
                            keyword: str = "", date_from: str = "",
                            date_to: str = "") -> dict:
    """分页查询交互记录"""
    init_db()
    conn = _get_conn()

    conditions = []
    params = []
    if keyword:
        conditions.append("(question LIKE ? OR answer LIKE ?)")
        params.extend([f"%{keyword}%", f"%{keyword}%"])
    if date_from:
        conditions.append("created_at >= ?")
        params.append(date_from)
    if date_to:
        conditions.append("created_at <= ?")
        params.append(date_to + " 23:59:59")

    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""

    total = conn.execute(
        f"SELECT COUNT(*) FROM chat_logs {where}", params
    ).fetchone()[0]

    offset = (page - 1) * page_size
    rows = conn.execute(
        f"SELECT * FROM chat_logs {where} ORDER BY created_at DESC "
        f"LIMIT ? OFFSET ?",
        params + [page_size, offset]
    ).fetchall()
    conn.close()

    items = []
    for r in rows:
        items.append({
            "id": r["id"],
            "question": r["question"],
            "answer": r["answer"][:200] + ("..." if len(r["answer"]) > 200 else ""),
            "answer_full": r["answer"],
            "sources": r["sources"],
            "response_time_ms": r["response_time_ms"],
            "ip_address": r["ip_address"],
            "emotion_tag": r["emotion_tag"],
            "created_at": r["created_at"],
        })

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": max(1, (total + page_size - 1) // page_size),
    }
