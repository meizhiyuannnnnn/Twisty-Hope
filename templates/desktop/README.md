# 桌面端模板 — Electron + React

## 使用方法

```bash
# 1. 先用 web 模板创建前端项目
# 2. 在项目根目录添加 Electron

mkdir desktop && cd desktop
npm init -y
npm install electron electron-builder
npm install -D concurrently wait-on

# 3. 复制 .prettierrc 等配置文件
```

## 目录结构

```
desktop/
├── main/                 # Electron 主进程
│   └── index.js          # 窗口创建、IPC、托盘
├── preload/              # 预加载脚本
│   └── index.js          # contextBridge 暴露 API
├── electron-builder.yml  # 打包配置
└── package.json
```

## main/index.js 模板

```javascript
const { app, BrowserWindow, Tray, Menu } = require('electron');
const path = require('path');

let mainWindow;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, '../preload/index.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  // 开发模式加载 Vite dev server，生产模式加载打包后的文件
  const isDev = process.env.NODE_ENV === 'development';
  const url = isDev
    ? 'http://localhost:3000'
    : `file://${path.join(__dirname, '../../web/dist/index.html')}`;

  mainWindow.loadURL(url);
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});
```

## preload/index.js 模板

```javascript
const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  // 暴露安全的 IPC 接口给渲染进程
  openFile: () => ipcRenderer.invoke('dialog:openFile'),
  getAppVersion: () => ipcRenderer.invoke('app:version'),
});
```

## electron-builder.yml 模板

```yaml
appId: com.bifaangxiji.app
productName: MyApp
directories:
  output: dist
  buildResources: build
files:
  - main/**/*
  - preload/**/*
  - ../web/dist/**/*
win:
  target:
    - nsis
  icon: build/icon.ico
nsis:
  oneClick: false
  allowToChangeInstallationDirectory: true
```
