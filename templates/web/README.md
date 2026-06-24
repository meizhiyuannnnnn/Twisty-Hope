# Web 前端模板 — React + Vite + TypeScript + Tailwind

## 快速启动

```bash
# 1. 复制模板到新项目
cp -r templates/web 新项目/web
cd 新项目/web

# 2. 安装依赖
npm install

# 3. 复制公司配置文件
cp ../../.prettierrc .prettierrc
cp ../../eslint.config.js eslint.config.js

# 4. 启动开发
npm run dev
```

## 技术栈

| 层面 | 技术 |
|------|------|
| 框架 | React 18 + Vite 5 |
| 类型 | TypeScript 5.x |
| 样式 | Tailwind CSS 3 |
| 路由 | react-router-dom |
| 状态 | Zustand + React Query |
| HTTP | axios |
| 测试 | Vitest |
| 格式化 | Prettier + ESLint |

## 模板包含

- ✅ 可运行的 Hello World 页面
- ✅ React Router 路由配置
- ✅ Zustand store 示例
- ✅ axios API 客户端封装（含错误拦截）
- ✅ TypeScript 类型定义
- ✅ Tailwind CSS 配置
- ✅ Vite 开发代理（`/api` → `localhost:8000`）
- ✅ 404 页面

## 变量替换

模板中的 `{{PROJECT_NAME}}` 需替换为实际项目名。
