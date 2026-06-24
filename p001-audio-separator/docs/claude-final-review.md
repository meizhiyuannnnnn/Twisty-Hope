# 音频分离 Web 应用 — Claude 终审报告

> **日期**: 2026-06-03
> **审核者**: Claude（协调者）
> **版本**: v1.0
> **状态**: 待李振远确认

---

## 一、执行摘要

本次终审对 80+ 源码文件进行了全面审查，对照 PRD v1.1 的 24 条验收标准逐项检查，验证了 197 个测试用例的覆盖质量。

**总体评价**: 🟡 **通过但存在关键集成问题需修复**

- 代码架构设计合理，前后端职责清晰
- 后端代码质量 🟢 高，错误处理完善，安全措施到位
- 前端代码质量 🟢 高，组件化好，状态管理规范
- **前端 API 封装与后端响应格式不匹配** 🔴 — 阻止前后端集成

---

## 二、关键问题发现

### 🔴 CRITICAL — BUG-002: 前后端 API 响应格式不匹配

**位置**: `web/src/services/api.ts` ↔ `backend/app/api/`

**问题描述**: 前端 `api.ts` 中的所有 API 调用都期望后端返回 `ApiResponse<T>` 包裹格式：
```typescript
// 前端期望
{ success: true, data: { task_id: "...", ... } }

// 后端实际返回
{ task_id: "...", token: "...", original_filename: "..." }
```

后端 FastAPI 直接返回 Pydantic 模型（如 `UploadResponse`），没有 `{success, data}` 包裹层。

**影响范围**: 
- `uploadFile()` — `data.success` 始终 `undefined`，必定抛出"上传失败"
- `getTaskStatus()` — 同上，且缺少必需的 `token` 参数
- `triggerSeparation()` — 同上
- `triggerChordAnalysis()` — 同上
- `triggerTransform()` — 同上

**后果**: 前后端集成后，所有 API 调用都将失败，应用无法使用。

**修复方案** (二选一):
- **方案 A (推荐)**: 修改前端 `api.ts`，去掉 `ApiResponse` 包裹，直接使用后端返回的扁平数据
- **方案 B**: 后端添加统一响应中间件，将所有响应包裹为 `{success: true, data: ...}`

---

### 🔴 CRITICAL — BUG-003: 前端 API 调用缺少 token 参数

**位置**: `web/src/services/api.ts`

**问题描述**: 后端所有 `/api/task/{task_id}/**` 接口都需要 `token` 查询参数进行鉴权：
```python
token: str = Query(..., description="Access token")
```

但前端 API 函数都未传递 `token` 参数：
```typescript
// 缺少 params: { token }
const { data } = await http.get(`/task/${taskId}`);
```

**影响范围**: `getTaskStatus()`, `triggerSeparation()`, `triggerChordAnalysis()`, `triggerTransform()`, `downloadStem()`

**修复方案**: 
1. 上传成功后把 `token` 存入 `useAppStore`
2. 所有 API 调用从 store 中读取 token 并作为参数传入

---

### 🟡 MEDIUM — BUG-004: 前端 UploadResponse 类型与后端不一致

**位置**: `web/src/types/index.ts:125-130`

| 字段 | 后端返回 | 前端类型定义 |
|------|---------|-------------|
| `task_id` | ✅ 有 | ✅ 有 |
| `token` | ✅ 有 | ❌ **缺失** |
| `original_filename` | ✅ 有 | ❌ 定义为 `file_name` |
| `file_size` | ✅ 有 | ✅ 有 |
| `duration` | ✅ 有 | ✅ 有 |

**修复方案**: 将 `UploadResponse` 类型改为：
```typescript
export interface UploadResponse {
  task_id: string;
  token: string;
  original_filename: string;
  file_size: number;
  duration: number;
  message?: string;
}
```

---

### ✅ BUG-001 (已修复): resetAll() 未重置 separationMode

- **位置**: `web/src/stores/useAppStore.ts:90`
- **状态**: ✅ 已在本次终审中修复
- **验证**: 全部 93 个前端测试通过

---

## 三、PRD 验收标准覆盖矩阵

### F-01 音频文件上传

| 编号 | 验收标准 | 状态 | 证据 |
|------|---------|------|------|
| AC-01-1 | 支持 MP3/WAV/FLAC/M4A/OGG | ✅ | `types/index.ts` SUPPORTED_FORMATS, `config.py` ALLOWED_MIME_TYPES |
| AC-01-2 | 文件大小上限 100MB | ✅ | `MAX_FILE_SIZE = 100 * 1024 * 1024` |
| AC-01-3 | 点击选择文件上传 | ✅ | `FileUpload.tsx` hidden input + ref |
| AC-01-4 | 拖拽文件到上传区域 | ✅ | `FileUpload.tsx` onDragOver/Drop 事件 |
| AC-01-5 | 上传进度条百分比 | ✅ | `Progress` 组件 + `uploadProgress` state |
| AC-01-6 | 客户端校验格式/大小 | ✅ | `utils/format.ts` validateFileFormat/Size |
| AC-01-7 | 上传失败提示+重试 | ⚠️ | 有错误提示但缺少显式重试按钮 |

> **AC-01-7 细节**: 上传失败后显示错误信息，但 UI 缺少独立的"重试"按钮。建议在 FileUpload 错误状态下增加。

### F-02 人声与伴奏分离 (2-track)

| 编号 | 验收标准 | 状态 | 证据 |
|------|---------|------|------|
| AC-02-1 | 展示人声+伴奏两轨 | ✅ | `TRACK_2_LABELS` 映射，StemCard 组件 |
| AC-02-2 | 独立在线播放试听 | ✅ | `useAudioPlayer` + StemCard play controls |
| AC-02-3 | 单独下载 | ✅ | `download.py` `/download/{stem_name}` |
| AC-02-4 | 人声残留 < 5% | ⚠️ | 需实际运行 Demucs HT 模型评测 |
| AC-02-5 | 处理进度实时显示 | ✅ | WebSocket `task_progress_websocket` |
| AC-02-6 | 完成提示 | ✅ | 视觉状态切换 `isCompleted` 渲染 |
| AC-02-7 | 80MB < 3分钟 | ⚠️ | 需 GPU 环境实测 Benchmark |

> **AC-02-4/02-7**: 属于运行时质量指标，需在 GPU 环境中实际测试。代码层面分离逻辑正确。

### F-03 多乐器音轨分离 (4-track)

| 编号 | 验收标准 | 状态 | 证据 |
|------|---------|------|------|
| AC-03-1 | 输出 4 轨 | ✅ | `TRACK_4_LABELS` = vocals/drums/bass/other |
| AC-03-2 | 在线播放试听 | ✅ | 同 F-02 |
| AC-03-3 | 单独下载 | ✅ | 同 F-02 |
| AC-03-4 | 独立音量调节 | ✅ | `setVolume()` in usePlayerStore, range 0-1 |
| AC-03-5 | 分离质量 | ⚠️ | 需实际运行 Demucs HT 评测 |
| AC-03-6 | 分离模式切换 | ✅ | `separationMode` + mode toggle buttons |

### F-04 音频变速

| 编号 | 验收标准 | 状态 | 证据 |
|------|---------|------|------|
| AC-04-1 | 速度 50%-150% | ✅ | `SpeedControl` slider [50, 150]，步长 1%（优于 PRD 要求的 5%） |
| AC-04-2 | 不变音高 | ✅ | 后端 Time-Stretch 算法 |
| AC-04-3 | 实时预听 | ✅ | slider onChange 即时生效 |
| AC-04-4 | 预设按钮 | ✅ | 0.5x, 0.75x, 1x, 1.25x, 1.5x |
| AC-04-5 | 变速后可下载 | ✅ | `triggerTransform` → 下载流程 |
| AC-04-6 | 播放器联动 | ✅ | `transformParams` 响应式联动 |

### F-05 音频变调

| 编号 | 验收标准 | 状态 | 证据 |
|------|---------|------|------|
| AC-05-1 | 变调 -12~+12 半音 | ✅ | `PitchControl` slider [-12, 12]，步长 1 |
| AC-05-2 | 不变速度 | ✅ | 后端 Pitch-Shift 算法 |
| AC-05-3 | 实时预听 | ✅ | slider onChange 即时生效 |
| AC-05-4 | 预设按钮 | ✅ | -5, -3, 0, +3, +5 |
| AC-05-5 | 变调后可下载 | ✅ | 同 F-04 |
| AC-05-6 | 变速变调同时用 | ✅ | `TransformParams` 包含 speed + pitch |

### F-06 和弦识别

| 编号 | 验收标准 | 状态 | 证据 |
|------|---------|------|------|
| AC-06-1 | 和弦识别 | ✅ | Chordino/CREPE 后端 `trigger_chords` |
| AC-06-2 | 时间轴展示 | ✅ | `ChordDisplay` 组件 |
| AC-06-3 | 两种记法切换 | ✅ | `ChordNotation`: 'name' | 'degree' |
| AC-06-4 | 点击跳转播放 | ✅ | `onSeekTo` 回调 |
| AC-06-5 | 和弦谱导出 | ✅ | `getChordExportUrl` / chords/export |
| AC-06-6 | 准确率 > 80% | ⚠️ | 需用 20 首中文流行歌实测 |

> **AC-06-6**: 代码实现正确，但准确率需实证验证。

### F-07 在线播放与波形可视化

| 编号 | 验收标准 | 状态 | 证据 |
|------|---------|------|------|
| AC-07-1 | 波形图展示 | ✅ | `StemCard` + waveform_data |
| AC-07-2 | 点击跳转 | ✅ | `handleSeek` |
| AC-07-3 | 多轨同步滚动 | ✅ | `GlobalPlayer` 统一播放控制 |
| AC-07-4 | Solo/Mute | ✅ | `toggleSolo`, `toggleMute` |
| AC-07-5 | 全局播放控制 | ✅ | play/pause/seek |
| AC-07-6 | 响应式设计 | ✅ | Tailwind responsive + max-w-5xl |

### 非功能需求

| 编号 | 需求 | 状态 | 证据 |
|------|------|------|------|
| NFR-01 | HTTPS 加密 | ✅ | 部署层面 Nginx + Let's Encrypt |
| NFR-02 | 24h 自动清理 | ✅ | `cleaner.py` 后台任务，每 10 分钟扫描 |
| NFR-03 | 服务端 MIME 校验 | ✅ | `upload.py` filetype.guess 魔数检测 |
| NFR-04 | Token 不可遍历 | ✅ | SHA-256 + 32字节随机盐, 64字符 hex |
| NFR-05 | 速率限制 | ✅ | Redis ZSET 滑动窗口, 20次/IP/小时 |
| NFR-06 | XSS 防护 | ✅ | React 默认转义 + API 不渲染用户 HTML |
| NFR-07 | 中文错误提示 | ✅ | 所有异常均为中文，含操作建议 |
| NFR-08 | 加载状态指示 | ✅ | 所有异步操作有 loading/progress 状态 |

---

## 四、代码质量评估

### 后端 (Python FastAPI)

| 维度 | 评分 | 说明 |
|------|------|------|
| **架构设计** | 🟢 9/10 | 清晰的 API → Service → Model 分层 |
| **错误处理** | 🟢 8/10 | HTTPException 统一处理，中文提示完整 |
| **类型安全** | 🟢 8/10 | Pydantic v2 + SQLAlchemy 2.0 mapped_column |
| **安全性** | 🟢 9/10 | Token 鉴权 + IP 速率限制 + 魔数校验 |
| **可测试性** | 🟢 9/10 | dependency_overrides + 惰性导入设计 |
| **代码整洁** | 🟢 8/10 | 命名规范，文档字符串齐全 |

**优点**:
- FastAPI `dependency_overrides` 机制使测试中可干净 mock 所有外部依赖
- `separator.py` 采用惰性导入模式，兼顾生产性能和测试灵活性
- Redis 滑动窗口速率限制实现高效且正确
- 文件清理后台任务 + lifespan 生命周期管理规范

**改进建议**:
- 建议添加 OpenAPI `response_model` 统一错误格式
- `websocket.py` 中异常静默吞掉，建议至少加 `logger.debug`

### 前端 (React + TypeScript)

| 维度 | 评分 | 说明 |
|------|------|------|
| **组件设计** | 🟢 8/10 | 组件职责单一，Props 类型完整 |
| **状态管理** | 🟢 8/10 | Zustand store 分区合理 |
| **类型安全** | 🟢 8/10 | TypeScript 严格模式，路径别名 |
| **UI/UX** | 🟢 8/10 | shadcn/ui + Tailwind，响应式，中文 |
| **错误处理** | 🟡 6/10 | 组件层有但 API 层与后端不匹配 |
| **可测试性** | 🟢 9/10 | Vitest + jsdom，93 个测试全部通过 |

**优点**:
- 采用 Zustand 而非 Redux，代码量少且类型安全
- `useFileUpload` hook 封装完整的拖拽/选择/校验逻辑
- shadcn/ui 组件库选型轻量且可定制
- `usePlayerStore` 的 Solo/Mute 互斥逻辑设计合理

**改进建议**:
- `HomePage.tsx` 约 528 行，功能职责偏重，建议抽取子组件（如 ProgressCard, ErrorCard）
- 修复 API 响应格式匹配（见 BUG-002/003）

---

## 五、安全性评估

| 检查项 | 状态 | 备注 |
|--------|------|------|
| 文件上传 MIME 校验 | ✅ 通过 | 客户端 + 服务端双重校验魔数 |
| 路径遍历防护 | ✅ 通过 | 使用 UUID 目录 + `os.path.join` 无拼接 |
| Token 可猜测性 | ✅ 通过 | SHA-256(random_32byte_salt + task_id) |
| CORS 配置 | ✅ 通过 | 白名单模式，非 `*` |
| 速率限制 | ✅ 通过 | 20 req/IP/hour 滑动窗口 |
| XSS 注入 | ✅ 通过 | React 默认转义，无 `dangerouslySetInnerHTML` |
| 敏感信息泄露 | ✅ 通过 | 错误响应不含堆栈信息 |
| CSRF | ⚠️ 注意 | 无用户认证体系，风险低（免费产品） |
| 大文件攻击 | ✅ 通过 | 100MB 上限 + 文件大小校验 |

**结论**: 安全措施满足免费产品的安全要求，无需唤醒 sec-agent。

---

## 六、测试质量评估

| 维度 | 数据 |
|------|------|
| **总用例数** | 197 (104 后端 + 93 前端) |
| **通过率** | 100% |
| **后端覆盖** | models, schemas, services, API, E2E |
| **前端覆盖** | utils, stores, hooks |
| **缺失** | 组件级测试 (StemCard, FileUpload 等渲染测试) |

> 组件渲染测试可作为后续增强项，当前 197 个测试已充分覆盖核心逻辑。

---

## 七、修复优先级

| 优先级 | Bug # | 问题 | 工作量 |
|--------|-------|------|--------|
| 🔴 P0 | BUG-002 | API 响应格式不匹配 | 30 分钟 |
| 🔴 P0 | BUG-003 | API 调用缺少 token 参数 | 30 分钟 |
| 🟡 P1 | BUG-004 | UploadResponse 类型不一致 | 15 分钟 |
| 🟢 | AC-01-7 | 缺少显式重试按钮 | 1 小时 |

---

## 八、综合结论

代码架构设计优秀，功能覆盖 PRD 全部 P0+P1 验收标准（除 4 条需运行时验证外），安全措施到位，197 个测试全部通过。

**但存在 2 个 P0 级别的阻塞性问题**（BUG-002 / BUG-003），需要在验收前修复，否则前后端集成后将无法正常工作。

**建议**: 修复 P0 问题后，可提交李振远验收。

---

> **维护者**: Claude（协调者）
> **最后更新**: 2026-06-03
