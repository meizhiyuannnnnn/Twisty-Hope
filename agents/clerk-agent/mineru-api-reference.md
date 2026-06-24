# MinerU API 参考文档

> 本文档从 `clerk-agent/SKILLS.md` 剥离，供文员 Agent 调用 MinerU 时参考。

---

## MinerU Agent API（Flash 模式 — 免费免登录 ⭐ 日常办公首选）

> 这是 `/api/v1/agent/parse/url` 所属的 API。免 Token，IP 限频，适合日常办公文档快解析。

### 基本信息

| 项目 | 内容 |
|------|------|
| **Base URL** | `https://mineru.net/api/v1/agent` |
| **认证** | 无需 Token（IP 限频，约 50 次/小时） |
| **文件限制** | ≤ 10 MB，≤ 20 页 |
| **输出格式** | 仅 Markdown（CDN 临时链接，24h 有效） |
| **模型** | 固定 pipeline 轻量模型 |

### 端点一览

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/parse/url` | 提交远程 URL 进行解析 |
| `POST` | `/parse/file` | 提交文件上传后进行解析 |
| `GET` | `/parse/{task_id}` | 轮询任务状态，获取结果 |

### 调用流程

```
① POST /parse/url  ──→  { data: { task_id: "..." } }
        │
② GET /parse/{task_id}  —— 每隔 3-5 秒轮询
        │
        ├── status: "waiting-file" | "uploading" | "pending" | "running" → 继续轮询
        ├── status: "done"    →  data.markdown_url ✅（24h CDN 链接）
        └── status: "failed"  →  data.err_code + err_msg ❌
```

### POST /parse/url — 请求体

```json
{
  "url": "https://example.com/document.pdf",
  "language": "zh",
  "page_range": "1-20",
  "ocr": false,
  "table": true,
  "formula": true
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `url` | string | ✅ | 可公开访问的文档链接 |
| `language` | string | ❌ | 文档语言，默认 `"zh"` |
| `page_range` | string | ❌ | 页码范围，如 `"1-20"`（PDF 超 20 页时用于分块） |
| `ocr` | bool | ❌ | 是否强制 OCR，默认 `false` |
| `table` | bool | ❌ | 是否提取表格，默认 `true` |
| `formula` | bool | ❌ | 是否提取公式，默认 `true` |

### POST /parse/file — 请求体

```json
{
  "file_name": "report.pdf",
  "language": "zh",
  "ocr": false,
  "table": true,
  "formula": true
}
```

返回 `data.file_url`（签名上传 URL）和 `data.task_id`，然后 `PUT` 文件到 `file_url`。

### GET /parse/{task_id} — 响应

```json
// 处理中
{ "data": { "task_id": "...", "status": "running", "progress": 45 } }

// 完成
{
  "data": {
    "task_id": "...",
    "status": "done",
    "progress": 100,
    "markdown_url": "https://cdn.mineru.net/result/xxx.md"
  }
}

// 失败
{
  "data": {
    "task_id": "...",
    "status": "failed",
    "err_code": 1001,
    "err_msg": "file too large"
  }
}
```

### Agent 调用方式

Agent 使用 `WebFetch` 工具直接调用 MinerU API，无需经过项目后端：

**步骤 1：提交解析任务**
```
WebFetch POST https://mineru.net/api/v1/agent/parse/url
Body: { "url": "<文档链接>", "language": "zh" }
→ 获取 task_id
```

**步骤 2：轮询结果**（每 3 秒一次，直到 `done` 或 `failed`）
```
WebFetch GET https://mineru.net/api/v1/agent/parse/{task_id}
→ status == "done" → 获取 markdown_url
```

**步骤 3：抓取 Markdown 内容**
```
WebFetch GET {markdown_url}
→ 获取解析后的 Markdown 原文
```

### 超 20 页的分块策略

超过 20 页的 PDF 不能直接提交，需分块：
1. 先下载文件到本地
2. 用 `pdf` skill 拆分为多个 ≤20 页的分片
3. 逐个提交 `/parse/file` 解析
4. 合并所有 Markdown 结果

### 与高精度模式的选择

| 场景 | 用哪个 |
|------|--------|
| 日常办公文档、网页文章、快速提取 | **Agent API**（免登录） |
| 大文件（>10MB）、复杂排版、需保留原格式 | pdf-converter 高精度模式 |
| 批量处理、需要 docx/json 输出 | pdf-converter 高精度模式 |
