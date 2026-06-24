# 桌面端模板 — Electron + React

## 快速启动

```bash
# 1. 先搭建前端（用 web 模板）
cp -r templates/web 新项目/web
cd 新项目/web && npm install

# 2. 再搭建桌面壳
cp -r templates/desktop 新项目/desktop
cd 新项目/desktop
npm install

# 3. 开发模式（web + electron 并发）
npm run dev
```

## 技术栈

| 层面 | 技术 |
|------|------|
| 壳框架 | Electron 28 |
| UI | React（共享 web 模板代码） |
| 打包 | electron-builder |
| IPC | contextBridge + ipcRenderer |

## 模板包含

- ✅ Electron 主进程（窗口管理、IPC）
- ✅ preload 脚本（contextBridge 安全暴露）
- ✅ 文件选择对话框 IPC 示例
- ✅ 开发/生产模式切换
- ✅ electron-builder 打包配置

## 桌面端架构

```
desktop/
├── main/index.js      # Electron 主进程
├── preload/index.js   # 安全桥接层
├── src/               # → 链接或复制 web 模板
└── package.json       # Electron 依赖 + 启动脚本
```

## 变量替换

模板中的 `{{PROJECT_NAME}}` 需替换为实际项目名。

---

> **彼方希冀程序开发公司** | 桌面端模板 v1.0 | 依赖 web 模板
