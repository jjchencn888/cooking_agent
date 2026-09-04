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

# 智能菜谱助手

输入一种或多种现有原材料，查找同时使用这些原材料的可制作菜品。例如输入“番茄，鸡蛋”，演示模式会返回番茄炒鸡蛋和番茄鸡蛋汤。

## 在线部署架构

- 前端：React + Vite，推荐部署到 Vercel。
- 后端：FastAPI，推荐通过 Docker 部署到 Render。
- 第三方服务：大米中文菜谱 API，可选 DeepSeek 中文步骤整理。

API 密钥只保存在后端部署平台的环境变量中，不会进入前端代码。

## 本地演示

后端：

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

前端：

```bash
cd frontend
copy .env.example .env.local
npm install
npm run dev
```

打开 `http://127.0.0.1:5173`，可以使用以下样例：

- `番茄，鸡蛋`：番茄炒鸡蛋、番茄鸡蛋汤
- `土豆，青椒`：青椒土豆丝
- `黄瓜，鸡蛋`：黄瓜炒鸡蛋
- `鸡蛋`：返回所有包含鸡蛋的内置菜谱

未配置 `RECIPE_API_KEY` 时自动使用内置演示菜谱；配置后则查询中文菜谱 API。
