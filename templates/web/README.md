# Web 前端模板 — React + Vite + TypeScript + Tailwind

## 使用方法

```bash
# 1. 创建项目（在新项目目录下执行）
npm create vite@latest web -- --template react-ts
cd web

# 2. 安装依赖
npm install react-router-dom zustand @tanstack/react-query axios
npm install -D tailwindcss @tailwindcss/vite postcss prettier prettier-plugin-tailwindcss

# 3. 复制公司配置文件
cp ../../.prettierrc .prettierrc
cp ../../eslint.config.js eslint.config.js

# 4. 启动开发
npm run dev
```

## 目录结构

```
web/
├── src/
│   ├── components/       # 通用组件
│   │   └── ui/           # shadcn/ui 组件（按需安装）
│   ├── pages/            # 页面组件
│   ├── hooks/            # 自定义 Hooks
│   ├── services/         # API 调用封装
│   ├── stores/           # Zustand stores
│   ├── types/            # TypeScript 类型
│   └── main.tsx          # 入口
├── index.html
├── vite.config.ts
├── tsconfig.json
└── package.json
```

## 关键配置

### vite.config.ts 模板
```ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: { port: 3000 },
});
```

### Tailwind 入口 (main.css)
```css
@import "tailwindcss";
```

## 公司标准依赖

| 类型 | 包 |
|------|-----|
| 路由 | react-router-dom |
| 状态（客户端）| zustand |
| 状态（服务端）| @tanstack/react-query |
| HTTP | axios |
| UI | shadcn/ui（按需安装） |
| 样式 | tailwindcss |
