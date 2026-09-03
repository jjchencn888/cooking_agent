from __future__ import annotations

import re
from typing import Any, Dict, List

import httpx

from app.core.config import get_settings
from app.services.ai_service import generate_steps


def _parse_ingredients(query: str) -> List[str]:
    ingredients = re.split(r"[,，、;；\s]+", query.strip())
    return list(dict.fromkeys(ingredient for ingredient in ingredients if ingredient))


def _ingredient_queries(ingredient: str) -> List[str]:
    aliases = {"番茄": ["西红柿"], "西红柿": ["番茄"]}
    return [ingredient, *aliases.get(ingredient, [])]


def _contains_all_ingredients(item: Dict[str, Any], ingredients: List[str]) -> bool:
    searchable_text = " ".join(
        str(item.get(field, "")) for field in ("cp_name", "yuanliao", "tiaoliao")
    )
    return all(
        any(candidate in searchable_text for candidate in _ingredient_queries(ingredient))
        for ingredient in ingredients
    )


async def search_recipes(query: str) -> List[Dict[str, Any]]:
    ingredients = _parse_ingredients(query)
    settings = get_settings()
    api_key = settings["recipe_api_key"]
    base_url = settings["recipe_api_base_url"]

    if not api_key:
        return [
            {
                "title": f"{'、'.join(ingredients)}料理",
                "ingredients": ingredients,
                "instructions": "当前使用演示数据。请在 backend/.env 中配置 RECIPE_API_KEY 以连接中文菜谱接口。",
                "source": "演示数据",
                "steps": [
                    "准备食材并清洗干净。", "锅中放油，炒香食材。", "加入主料和调味料翻炒。", "装盘即可食用。",
                ],
            }
        ]

    matched_items: Dict[str, Dict[str, Any]] = {}
    async with httpx.AsyncClient(timeout=20.0) as client:
        for ingredient in ingredients:
            for candidate in _ingredient_queries(ingredient):
                params = {
                    "word": candidate, "key": api_key, "num": 20, "page": 1,
                }

                try:
                    response = await client.get(base_url, params=params)
                    response.raise_for_status()
                    payload = response.json()
                except Exception as exc:
                    print("中文菜谱接口请求失败：", repr(exc))
                    continue

                results = payload.get("data", {}).get("list", [])
                for item in results:
                    if not _contains_all_ingredients(item, ingredients):
                        continue
                    item_key = str(item.get("id") or item.get("cp_name") or "")
                    if item_key:
                        matched_items[item_key] = item

    if not matched_items:
        return []

    enriched_results = []
    for item in matched_items.values():
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
