from __future__ import annotations

import json
from typing import List

import httpx

from app.core.config import get_settings


async def generate_steps(title: str, ingredients: List[str], instructions: str = "") -> List[str]:
    settings = get_settings()
    model_key = settings["model_api_key"]
    base_url = settings["model_api_base_url"]
    model_name = "deepseek-chat"

    if not model_key:
        return _fallback_steps(title, ingredients, instructions)

    prompt = (
        "你是一名中文烹饪助手。请根据以下菜谱信息，输出清晰、按顺序排列的中文烹饪步骤。每步只写一个具体动作，不要添加解释。\n\n"
        f"菜名：{title}\n食材：{ingredients}\n参考做法：{instructions or '无'}\n"
        "输出格式必须是 JSON：{\"steps\": [\"步骤一\", \"步骤二\"]}"
    )

    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": "你是中文烹饪助手，只返回指定格式的有效 JSON。"},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.3,
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{base_url.rstrip('/')}/chat/completions",
                headers={
                    "Authorization": f"Bearer {model_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
    except Exception as exc:
        print("中文步骤生成请求失败：", repr(exc))
        return _fallback_steps(title, ingredients, instructions)

    try:
        content = data["choices"][0]["message"]["content"]
        parsed = json.loads(content)
        if isinstance(parsed.get("steps"), list):
            return [str(step) for step in parsed["steps"]]
    except Exception:
        pass

    return _fallback_steps(title, ingredients, instructions)


def _fallback_steps(title: str, ingredients: List[str], instructions: str = "") -> List[str]:
    base_steps = [
        f"准备{title}所需食材，清洗干净并按需切好：{'、'.join(ingredients[:4]) if ingredients else '主料和调味料'}。",
        "锅中放油，炒香葱姜蒜等辅料。",
        "加入主料，炒至熟透或软嫩。",
        "加入适量调味料，继续翻炒或炖煮至入味。",
        "出锅前尝味，根据需要调整咸淡后装盘。",
    ]

    if instructions and isinstance(instructions, str):
        cleaned = instructions.replace("<ol>", "").replace("</ol>", "").replace("<li>", "").replace("</li>", "").replace("<p>", "").replace("</p>", "")
        if cleaned:
            candidate_steps = [part.strip() for part in cleaned.replace('。', '.') .split('.') if part.strip()]
            if len(candidate_steps) >= 3:
                return candidate_steps[:5]

    return base_steps
