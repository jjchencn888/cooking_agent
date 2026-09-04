<<<<<<< HEAD
=======
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
>>>>>>> 9d789742d6af2f23cefecd8ec4270ebe1c132a66
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

## 云端部署

### 部署后端到 Render

1. 将项目推送到 GitHub。
2. 在 Render 中选择 Blueprint，并读取仓库根目录的 `render.yaml`。
3. 配置 `RECIPE_API_KEY`、`MODEL_API_KEY` 和 `ALLOWED_ORIGINS`。
4. `ALLOWED_ORIGINS` 填写正式前端地址，例如 `https://cooking-agent.vercel.app`。
5. 部署完成后记录后端 HTTPS 地址。

### 部署前端到 Vercel

1. 导入同一个 GitHub 仓库。
2. 将 Root Directory 设置为 `frontend`。
3. 配置环境变量 `VITE_API_BASE_URL=https://你的Render后端域名`。
4. 部署前端。
5. 将实际 Vercel 域名更新到 Render 的 `ALLOWED_ORIGINS`，然后重新部署后端。

## 环境变量

后端变量保存在 `backend/.env` 或云平台环境变量中，读取配置位于 `backend/app/core/config.py`：

```env
APP_ENV=production
RECIPE_API_KEY=你的中文菜谱API密钥
RECIPE_API_BASE_URL=https://api.qqsuu.cn/api/dm-caipu
MODEL_API_KEY=你的DeepSeek密钥
MODEL_API_BASE_URL=https://api.deepseek.com
ALLOWED_ORIGINS=https://你的前端域名
```
（可以使用自己的菜谱和模型api）

<<<<<<< HEAD
前端只保存公开的后端地址：

```env
VITE_API_BASE_URL=https://你的后端域名
```

## 接口

- `GET /health`：服务健康检查
- `POST /api/search`：按原材料搜索菜谱
- `GET /docs`：交互式接口文档

请求样例：

```json
{
  "query": "番茄，鸡蛋"
}
```

更完整的实施与验收方案见 `plan.md`。
=======
中文菜谱接口来源：大米 API 菜谱查询（按每项原材料查询 `word`，再筛选同时包含全部原材料的结果，返回菜名、原料、调料和做法）。
>>>>>>> 9d789742d6af2f23cefecd8ec4270ebe1c132a66
