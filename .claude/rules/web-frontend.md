---
globs: **/web/src/**,**/src/**/*.tsx,**/templates/web/**
version: 1.0.0
alwaysApply: false
---

# 前端开发规范 — React + Vite + TypeScript

## 技术栈约束
- 框架：React 18+（函数组件 + Hooks）
- 构建：Vite 5+
- 语言：TypeScript 5+（strict mode）
- 样式：Tailwind CSS（utility-first）
- 状态管理：Zustand（客户端）/ React Query（服务端）
- 路由：React Router v6

## 文件命名
- 组件文件：PascalCase — `UserProfile.tsx`
- Hook 文件：camelCase + use 前缀 — `useUserData.ts`
- 工具函数：camelCase — `formatDate.ts`
- 类型文件：PascalCase — `User.ts`

## TypeScript 规范
- 禁止 `any`（除非有注释说明理由）
- 所有组件 Props 必须定义 interface
- API 响应必须有类型定义

## 代码结构
```
web/src/
├── components/          # 通用组件
│   ├── ui/              # shadcn/ui 组件
│   └── common/          # 业务通用组件
├── pages/               # 页面组件
├── hooks/               # 自定义 Hooks
├── stores/              # Zustand stores
├── services/            # API 调用层
├── types/               # TypeScript 类型定义
└── utils/               # 工具函数
```

## 代码规范
- API 调用统一封装在 `services/` 层，不在组件中直接 `fetch`
- 每个 API 调用必须有错误处理和用户提示
- 每个异步操作必须有 loading 状态

## 格式化
- Prettier（`.prettierrc`）
- ESLint（`eslint.config.js`）
- TypeScript（`tsc --noEmit`）

## 测试
- Vitest + Testing Library
- 组件测试覆盖核心交互逻辑
