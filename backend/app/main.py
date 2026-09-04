from __future__ import annotations

from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.services.recipe_service import search_recipes
from app.core.config import get_settings
from app.services.recipe_service import RecipeAPIError

settings = get_settings()
app = FastAPI(title="智能菜谱助手 API", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings["allowed_origins"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=200)


class RecipeResult(BaseModel):
    title: str
    ingredients: List[str]
    instructions: str
    source: str
    steps: List[str] = []


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok", "service": "cooking-agent"}


@app.post("/api/search", response_model=dict)
async def search_recipe(payload: SearchRequest) -> dict:
    query = payload.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="查询内容不能为空")

    try:
        results = await search_recipes(query)
    except RecipeAPIError:
        raise HTTPException(status_code=503, detail="菜谱服务暂时不可用，请稍后重试")
    if not results:
        return {
            "query": query,
            "results": [],
            "message": "没有找到匹配的菜谱，请尝试更具体的菜名或食材组合。",
        }

    return {
        "query": query,
        "results": [RecipeResult(**item).dict() for item in results],
        "message": "搜索成功",
    }
