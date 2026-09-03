# Cooking Agent

A simple cooking assistant prototype: the user enters a dish name or ingredients, the backend searches for recipe sources, and the frontend displays the dish information and steps.

## Structure

- backend: FastAPI backend
- frontend: Vite + React frontend

## Backend startup

```bash
cd backend
python -m venv .venv
# Windows
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Frontend startup

```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0
```

## Access

- Backend: http://127.0.0.1:8000/health
- Frontend: http://127.0.0.1:5173

## Current status

This is an MVP skeleton with a demo data path by default. You can later connect real third-party recipe APIs and AI services.
=======
# 智能菜谱助手

用户输入一个或多个原材料，后端通过中文菜谱 API 查找同时包含所有原材料的菜品，前端展示食材和烹饪步骤。

## Structure

- backend: FastAPI backend
- frontend: Vite + React frontend

## Backend startup

```bash
cd backend
python -m venv .venv
# Windows
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Frontend startup

```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0
```

## Access

- Backend: http://127.0.0.1:8000/health
- Frontend: http://127.0.0.1:5173

## 当前状态

这是一个 MVP。默认使用演示数据；配置 API 密钥后使用大米中文菜谱 API，并可使用 DeepSeek 将做法整理为中文步骤。

## API 密钥配置

API 配置文件是 `backend/app/core/config.py`，但密钥应保存在 `backend/.env`，不要直接写入代码：

```env
RECIPE_API_KEY=你的大米API密钥
RECIPE_API_BASE_URL=https://api.qqsuu.cn/api/dm-caipu
MODEL_API_KEY=你的DeepSeek密钥
MODEL_API_BASE_URL=https://api.deepseek.com
```
（可以使用自己的菜谱和模型api）
中文菜谱接口来源：大米 API 菜谱查询（按每项原材料查询 `word`，再筛选同时包含全部原材料的结果，返回菜名、原料、调料和做法）。
