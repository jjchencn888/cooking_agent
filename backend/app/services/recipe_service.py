from __future__ import annotations

import re
from typing import Any, Dict, List

import httpx

from app.core.config import get_settings
from app.services.ai_service import generate_steps


class RecipeAPIError(RuntimeError):
    """中文菜谱服务不可用。"""


DEMO_RECIPES = [
    {
        "title": "番茄炒鸡蛋",
        "ingredients": ["番茄 2 个", "鸡蛋 3 个", "食用油 适量", "盐 适量", "白糖 少许"],
        "instructions": "鸡蛋打散。番茄切块。先炒鸡蛋并盛出。再炒番茄至出汁。倒回鸡蛋，加盐和少许白糖翻炒均匀。",
        "steps": ["鸡蛋打散，番茄洗净切块。", "锅中放油，将鸡蛋炒熟后盛出。", "原锅放入番茄，炒至变软出汁。", "倒回鸡蛋，加入盐和少许白糖。", "翻炒均匀后装盘。"],
        "keywords": ["番茄", "西红柿", "鸡蛋"],
    },
    {
        "title": "番茄鸡蛋汤",
        "ingredients": ["番茄 1 个", "鸡蛋 2 个", "清水 适量", "盐 适量", "葱花 少许"],
        "instructions": "番茄炒软后加水煮开，淋入蛋液，调味后撒葱花。",
        "steps": ["番茄洗净切块，鸡蛋打散。", "锅中放少量油，将番茄炒软。", "加入清水并煮沸。", "缓慢淋入蛋液，待其凝固后轻推。", "加盐调味，撒葱花后盛出。"],
        "keywords": ["番茄", "西红柿", "鸡蛋"],
    },
    {
        "title": "青椒土豆丝",
        "ingredients": ["土豆 2 个", "青椒 1 个", "食用油 适量", "盐 适量", "米醋 少许"],
        "instructions": "土豆和青椒切丝，土豆丝洗去淀粉后与青椒大火快炒。",
        "steps": ["土豆去皮切丝，用清水洗去表面淀粉。", "青椒去籽切丝。", "锅中热油，放入土豆丝大火翻炒。", "加入青椒丝、盐和少许米醋。", "炒至断生后立即装盘。"],
        "keywords": ["土豆", "马铃薯", "青椒"],
    },
    {
        "title": "黄瓜炒鸡蛋",
        "ingredients": ["黄瓜 1 根", "鸡蛋 2 个", "食用油 适量", "盐 适量"],
        "instructions": "黄瓜切片，鸡蛋炒熟后与黄瓜快速翻炒。",
        "steps": ["黄瓜洗净切片，鸡蛋打散。", "锅中放油，将鸡蛋炒熟后盛出。", "原锅放入黄瓜片快速翻炒。", "倒回鸡蛋并加盐调味。", "翻炒均匀后装盘。"],
        "keywords": ["黄瓜", "鸡蛋"],
    },
]


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


def _demo_recipes(ingredients: List[str]) -> List[Dict[str, Any]]:
    results = []
    for recipe in DEMO_RECIPES:
        searchable_text = " ".join(recipe["keywords"])
        if not all(
            any(candidate in searchable_text for candidate in _ingredient_queries(ingredient))
            for ingredient in ingredients
        ):
            continue
        result = {key: value for key, value in recipe.items() if key != "keywords"}
        result["source"] = "内置演示菜谱"
        results.append(result)
    return results


def _extract_results(payload: Any) -> List[Dict[str, Any]]:
    if not isinstance(payload, dict):
        return []
    for container_name in ("data", "result"):
        container = payload.get(container_name)
        if isinstance(container, dict) and isinstance(container.get("list"), list):
            return [item for item in container["list"] if isinstance(item, dict)]
    return []
    return all(
        any(candidate in searchable_text for candidate in _ingredient_queries(ingredient))
        for ingredient in ingredients
    )


async def search_recipes(query: str) -> List[Dict[str, Any]]:
    ingredients = _parse_ingredients(query)
    settings = get_settings()
    api_key = settings["recipe_api_key"]
    base_url = settings["recipe_api_base_url"]

    if not ingredients:
        return []

    if not api_key:
        return _demo_recipes(ingredients)

    matched_items: Dict[str, Dict[str, Any]] = {}
    successful_requests = 0
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
                    print("中文菜谱接口请求失败：", type(exc).__name__)
                    continue

                successful_requests += 1
                results = _extract_results(payload)
                for item in results:
                    if not _contains_all_ingredients(item, ingredients):
                        continue
                    item_key = str(item.get("id") or item.get("cp_name") or "")
                    if item_key:
                        matched_items[item_key] = item

    if successful_requests == 0:
        raise RecipeAPIError("中文菜谱服务暂时不可用")

    if not matched_items:
        return []

    enriched_results = []
    for item in list(matched_items.values())[:5]:
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
