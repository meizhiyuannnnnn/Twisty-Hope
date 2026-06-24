const { contextBridge, ipcRenderer } = require('electron');

// 暴露安全的 API 给渲染进程
contextBridge.exposeInMainWorld('electronAPI', {
  // 文件选择
  openFileDialog: (options) => ipcRenderer.invoke('open-file-dialog', options),

  // 平台信息
  platform: process.platform,
});
