# Cooking Agent 网页化部署实施计划

## 1. 项目目标

将 Cooking Agent 改造为用户打开网址即可使用的云端网页应用。用户不需要在本地安装依赖、启动前端或启动后端。

目标架构：

```text
用户浏览器
    ↓ HTTPS
前端静态网站
    ↓ HTTPS API 请求
FastAPI 云端后端
    ├── 中文菜谱 API
    └── DeepSeek API
```

## 2. 推荐部署方案

### 前端

- 技术：React + Vite
- 部署平台：Vercel
- 部署形式：静态网站
- 构建命令：`npm run build`
- 输出目录：`dist`

### 后端

- 技术：FastAPI
- 部署平台：Render 或 Railway
- 启动命令：

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### 代码托管

- 使用 GitHub 保存项目代码
- 前端和后端可以放在同一个仓库中
- 通过 GitHub 推送自动触发云端部署

## 3. 前端改造

### 3.1 移除本地地址

当前前端请求地址写死为：

```text
http://127.0.0.1:8000/api/search
```

应改为环境变量：

```javascript
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
fetch(`${API_BASE_URL}/api/search`, options);
```

### 3.2 增加环境变量示例

新增文件：

```text
frontend/.env.example
```

内容：

```env
VITE_API_BASE_URL=https://你的后端域名
```

Vercel 中配置正式值，例如：

```env
VITE_API_BASE_URL=https://cooking-agent-api.onrender.com
```

### 3.3 前端交互完善

- 搜索按钮显示加载状态
- 后端不可用时显示中文错误提示
- 空输入时不发送请求
- 保持中文菜名、食材和烹饪步骤展示
- 必要时增加后端地址配置说明

## 4. 后端改造

### 4.1 环境变量

新增或完善文件：

```text
backend/.env.example
```

内容：

```env
APP_ENV=production
RECIPE_API_KEY=你的中文菜谱API密钥
RECIPE_API_BASE_URL=https://api.qqsuu.cn/api/dm-caipu
MODEL_API_KEY=你的DeepSeek密钥
MODEL_API_BASE_URL=https://api.deepseek.com
ALLOWED_ORIGINS=https://你的前端域名
```

真实密钥只配置在 Render/Railway 的环境变量中，不提交到 GitHub。

### 4.2 CORS

将当前的全开放配置：

```python
allow_origins=["*"]
```

改为从 `ALLOWED_ORIGINS` 读取正式前端域名，只允许已部署的前端访问。

开发环境可以允许：

```text
http://127.0.0.1:5173
http://localhost:5173
```

生产环境只允许正式 HTTPS 域名。

### 4.3 API 异常处理

- 第三方 API 超时后返回友好的中文提示
- 不向用户暴露 API 密钥、请求 URL 或内部堆栈
- 对第三方 API 返回格式进行校验
- 记录状态码和错误类型，避免记录密钥
- 对查询内容做长度和空值校验

### 4.4 菜谱搜索逻辑

保留现有中文菜谱 API 适配，但确认以下逻辑：

- 支持中文菜名输入
- 支持多个食材输入
- 将用户输入的食材拆分为关键词
- 使用 API 的食材搜索参数查询可制作菜品
- 对 API 返回的菜名、原料、调料、做法进行统一格式化
- API 没有结果时返回明确的中文提示

## 5. 部署文件

建议新增：

```text
frontend/.env.example
backend/.env.example
backend/Dockerfile
render.yaml
```

### Dockerfile 建议

后端 Dockerfile 应完成以下工作：

1. 使用 Python 基础镜像。
2. 安装 `backend/requirements.txt`。
3. 复制后端代码。
4. 使用 `$PORT` 启动 Uvicorn。

### Render 配置建议

- Root Directory：`backend`
- Runtime：Python 或 Docker
- Health Check Path：`/health`
- 自动从 GitHub 部署
- 配置所有后端环境变量

## 6. 域名和 HTTPS

初期可以直接使用平台提供的域名：

```text
前端：https://cooking-agent.vercel.app
后端：https://cooking-agent-api.onrender.com
```

稳定运行后可以绑定自定义域名：

```text
www.example.com
api.example.com
```

前端和后端都必须使用 HTTPS，避免浏览器拦截跨域请求或泄露请求数据。

## 7. 密钥和安全要求

- 删除代码中所有硬编码 API 密钥。
- 如果旧密钥曾经提交到 Git 或公开环境，应立即到对应平台撤销并重新生成。
- 前端环境变量只能放公开配置，不能放 `MODEL_API_KEY` 或 `RECIPE_API_KEY`。
- `.env` 加入 `.gitignore`。
- 生产环境关闭详细调试信息。
- 限制单次查询长度和调用频率。

## 8. 测试计划

### 本地测试

- 后端能访问 `/health`。
- 使用中文菜名搜索，例如“番茄炒蛋”。
- 使用多个食材搜索，例如“番茄，鸡蛋”。
- 空输入能得到中文校验提示。
- API 密钥缺失时，演示数据或明确配置提示可以正常显示。
- 第三方 API 失败时，前端显示中文错误信息。

### 线上测试

- 直接打开前端网址可以加载页面。
- 前端可以访问线上后端。
- 浏览器控制台没有 CORS 错误。
- 浏览器端无法看到第三方 API 密钥。
- `/health` 返回正常状态。
- 手机浏览器可以完成搜索和查看步骤。

## 9. 实施顺序

1. 修改前端 API 地址为 `VITE_API_BASE_URL`。
2. 完善后端环境变量和 CORS 配置。
3. 增加 `.env.example`、`.gitignore` 和部署配置。
4. 本地构建并测试前后端接口。
5. 将代码推送到 GitHub。
6. 在 Render/Railway 部署后端。
7. 在 Vercel 部署前端，并配置后端地址。
8. 配置生产环境 CORS 域名。
9. 完成线上功能、安全和移动端验收。

## 10. 验收标准

项目完成后应满足：

- 用户只需打开网址即可使用。
- 不要求用户本地启动任何服务。
- 中文输入能够搜索中文菜谱。
- 菜名、食材、做法、错误信息均能以中文展示。
- API 密钥不出现在前端代码和浏览器请求中。
- 前后端均通过 HTTPS 访问。
- 线上服务具备健康检查和基本异常处理。

