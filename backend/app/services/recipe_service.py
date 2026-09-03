from __future__ import annotations

from typing import Any, Dict, List

import httpx

from app.core.config import get_settings
from app.services.ai_service import generate_steps


def _candidate_queries(query: str) -> List[str]:
    raw = query.strip()
    if not raw:
        return []

    candidates = [raw]
    aliases = {"番茄鸡蛋面": ["西红柿鸡蛋面"], "番茄炒蛋": ["西红柿炒鸡蛋"]}

    for alias in aliases.get(raw, []):
        if alias not in candidates:
            candidates.append(alias)
    return candidates


async def search_recipes(query: str) -> List[Dict[str, Any]]:
    settings = get_settings()
    api_key = settings["recipe_api_key"]
    base_url = settings["recipe_api_base_url"]

    if not api_key:
        return [
            {
                "title": query,
                "ingredients": ["示例食材一", "示例食材二"],
                "instructions": "当前使用演示数据。请在 backend/.env 中配置 RECIPE_API_KEY 以连接中文菜谱接口。",
                "source": "演示数据",
                "steps": [
                    "准备食材并清洗干净。", "锅中放油，炒香食材。", "加入主料和调味料翻炒。", "装盘即可食用。",
                ],
            }
        ]

    for candidate in _candidate_queries(query):
        params = {
            "word": candidate, "key": api_key, "num": 5, "page": 1,
        }

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                response = await client.get(base_url, params=params)
                response.raise_for_status()
                payload = response.json()
        except Exception as exc:
            print("中文菜谱接口请求失败：", repr(exc))
            continue

        results = payload.get("data", {}).get("list", [])
        if not results:
            continue

        enriched_results = []
        for item in results:
            title = item.get("cp_name", query)
            ingredient_names = [x for x in [item.get("yuanliao", ""), item.get("tiaoliao", "")] if x]
            instructions = item.get("zuofa", "") or ""
            steps = await generate_steps(title, ingredient_names, instructions)
            enriched_results.append(
                {
                    "title": title,
                    "ingredients": ingredient_names or ["接口未返回食材信息"],
                    "instructions": instructions or "接口未提供详细做法，已根据菜名生成通用烹饪指南。",
                    "source": "大米中文菜谱 API",
                    "steps": steps,
                    "id": item.get("id"),
                }
            )

        return enriched_results

    return []
