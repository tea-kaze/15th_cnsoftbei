import os
from typing import Generator, Optional
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY", "sk-placeholder"),
    base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"),
)
MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

SYSTEM_PROMPT = """你是一个景区的AI数字人导游。根据提供的知识库内容回答游客的问题。
回答要求：
1. 使用亲切、热情的语气，像真人导游一样
2. 只根据提供的知识内容回答，不要编造信息
3. 如果知识库中没有相关信息，礼貌地告知游客并尝试给出相关建议
4. 回答简洁明了，适合语音播放（不要太长）
5. 如果游客用代词（如"它""这个""那里"）指代之前提到的事物，请结合对话历史理解
6. 用 **重点内容** 加粗关键信息（如数字、名称、特色），用空行分段让回答更易读"""


def _build_messages(question: str, context_chunks: list[str],
                    history: Optional[list[dict]] = None) -> list[dict]:
    """构建 LLM 消息列表"""
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # 插入最近 N 轮对话历史
    if history:
        # 只保留最近消息，防止超出 token 限制
        messages += history[-12:]

    context_text = "\n\n---\n\n".join(context_chunks) if context_chunks else "暂无相关知识库内容"
    messages.append({
        "role": "user",
        "content": f"参考以下知识库内容回答问题：\n\n{context_text}\n\n游客问题：{question}",
    })
    return messages


def answer_with_context(question: str, context_chunks: list[str],
                        history: Optional[list[dict]] = None) -> str:
    """非流式回答（兼容旧接口）"""
    if not context_chunks:
        return "抱歉，我目前的知识库中还没有相关信息。请换个问题试试，或者联系景区工作人员获取帮助。"

    messages = _build_messages(question, context_chunks, history)

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.7,
        max_tokens=500,
    )
    return response.choices[0].message.content


def answer_stream(question: str, context_chunks: list[str],
                  history: Optional[list[dict]] = None) -> Generator[str, None, None]:
    """流式生成回答，逐步 yield token"""
    if not context_chunks:
        yield "抱歉，我目前的知识库中还没有相关信息。请换个问题试试，或者联系景区工作人员获取帮助。"
        return

    messages = _build_messages(question, context_chunks, history)

    stream = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.7,
        max_tokens=500,
        stream=True,
    )
    for chunk in stream:
        delta = chunk.choices[0].delta
        if delta.content:
            yield delta.content
