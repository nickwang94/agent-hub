# Agent Hub 前端

基于 React + Vite 的聊天界面，类似 ChatGPT 的用户体验。

## 快速开始

### 1. 启动后端 API

```bash
# 在项目根目录
./start-api.sh
```

或者手动启动：
```bash
source venv/bin/activate
python backend/api.py
```

后端服务将运行在 `http://localhost:5000`

### 2. 启动前端

```bash
cd frontend
npm run dev
```

前端将运行在 `http://localhost:5173`

## 功能

- 💬 实时聊天对话
- 🎨 类似 ChatGPT 的界面
- 📝 建议问题快速提问
- 🔄 自动滚动到最新消息
- ⌨️ 支持 Enter 发送，Shift+Enter 换行

## 截图

界面采用暗色主题，包含：
- 欢迎界面：显示 4 个建议问题
- 聊天界面：显示对话历史，用户和 AI 消息交替显示
- 输入框：固定在底部，支持多行输入

## API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/chat` | POST | 发送消息 |
| `/sessions` | GET | 获取会话列表 |
| `/sessions/:id` | DELETE | 删除会话 |
| `/knowledge/add` | POST | 添加知识 |
| `/knowledge/status` | GET | 知识库状态 |

## 开发

### 修改 API 地址

编辑 `src/App.jsx`：
```javascript
const API_BASE_URL = 'http://localhost:5000'
```

### 自定义样式

编辑 `src/App.css` 修改样式。
