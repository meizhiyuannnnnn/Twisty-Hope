# Technical Preferences — 《彼方希冀》

<!-- Populated by /setup-engine. Updated as the user makes decisions throughout development. -->
<!-- All agents reference this file for project-specific standards and conventions. -->

## Engine & Language

- **Engine**: Godot 4.7 (stable, Win64)
- **Language**: GDScript 2.0
- **Rendering**: Forward+ (默认 3D 渲染器，2D 游戏使用)
- **Physics**: Jolt Physics (Godot 4.7 默认)

## Input & Platform

<!-- Written by /setup-engine. Read by /ux-design, /ux-review, /test-setup, /team-ui, and /dev-story -->
<!-- to scope interaction specs, test helpers, and implementation to the correct input methods. -->

- **Target Platforms**: PC (Windows) — 首发平台，后续考虑 Linux/Mac
- **Input Methods**: 键盘 + 鼠标（当前），后续扩展手柄
- **Primary Input**: 键盘（快捷键控制火车、交互、暂停）
- **Gamepad Support**: None（Phase 2 暂不支持）
- **Touch Support**: None（PC 游戏）
- **Platform Notes**: 桌面端，窗口化运行，支持全屏切换

## Naming Conventions

- **Classes**: PascalCase（`TrainController`, `ResourceManager`）
- **Variables**: snake_case（`max_health`, `fuel_consumption_rate`）
- **Signals/Events**: snake_case + 过去式动词（`health_changed`, `character_died`）
- **Files**: snake_case（`resource_manager.gd`, `event_bus.gd`）
- **Scenes/Prefabs**: PascalCase（`Train.tscn`, `Character.tscn`）
- **Constants**: UPPER_SNAKE_CASE（`MAX_HEALTH`, `FRAME_BUDGET_MS`）

## Performance Budgets

- **Target Framerate**: 60 fps
- **Frame Budget**: ≤ 16.67ms (1000ms / 60fps)
- **Draw Calls**: ≤ 50 (2D 游戏，精灵图集优化)
- **Memory Ceiling**: ≤ 512 MB (PC 平台合理范围)

## Testing

- **Framework**: GUT (Godot Unit Test) — 待 Phase 3 启用
- **Minimum Coverage**: 核心系统 80%（资源/事件/车厢），UI 60%
- **Required Tests**: 资源计算公式、事件触发逻辑、存档/读档、车厢效果

## Forbidden Patterns

<!-- Add patterns that should never appear in this project's codebase -->
- `_process` 中创建对象（`new`、`[]`、`{}`）→ 预分配或缓存
- `find_node()` 在 `_ready` 外调用 → 用 `@onready` 缓存
- 全局变量 → 用 Autoload 单例
- 超过 500 行的单文件脚本 → 拆分
- 字符串拼接在 `_process` 中 → 用 `StringName` 或预分配
- `call_deferred` 滥用 → 只在确实需要延迟到下一帧时使用
- 直接引用其他系统（紧耦合）→ 通过 EventBus 信号通信

## Allowed Libraries / Addons

<!-- Add approved third-party dependencies here -->
- **GUT** (Godot Unit Test) — 待 Phase 3 启用
- 其他第三方插件需经李振远审批后加入此列表

## Architecture Decisions Log

<!-- Quick reference linking to full ADRs in docs/architecture/ -->

| ADR | 决策 | 理由 |
|-----|------|------|
| ADR-001 | 雪花用 CPUParticles2D | 性能足够，GPU 粒子不需要 |
| ADR-002 | 背景用 Sprite2D 双层 + z_index | Godot 原生方案，简单可靠 |
| ADR-003 | 铁轨用 TrackDrawer 独立节点 | 在背景之上、火车之下，z_index 分层 |
| ADR-004 | 火车用 `_draw()` 代码绘制 | 下载素材风格不匹配 |
| ADR-005 | 暂停系统自定义实现 | 不用 `get_tree().paused`，更灵活 |
| ADR-006 | 背景接缝用 Python PIL 边缘融合 | cosine falloff，精度可控 |
| ADR-007 | 地面视觉由 track_drawer.gd 统一处理 | 渐变+枕木色差+积雪点集中管理 |

## Engine Specialists

<!-- Written by /setup-engine when engine is configured. -->
<!-- Read by /code-review, /architecture-decision, /architecture-review, and team skills -->
<!-- to know which specialist to spawn for engine-specific validation. -->

- **Primary**: godot-specialist (Godot 4 总专家)
- **Language/Code Specialist**: godot-gdscript-specialist (GDScript 专项)
- **Shader Specialist**: godot-shader-specialist (Shader 专项，需要时唤醒)
- **UI Specialist**: ui-programmer (UI 专项，需要时唤醒)
- **Additional Specialists**: godot-gdextension-specialist (C++ 扩展)、godot-csharp-specialist (C# 绑定)
- **Routing Notes**: 默认路由到 godot-gdscript-specialist（90% 任务），复杂视觉问题路由到 technical-artist

### File Extension Routing

<!-- Skills use this table to select the right specialist per file type. -->
<!-- If a row says [TO BE CONFIGURED], fall back to Primary for that file type. -->

| File Extension / Type | Specialist to Spawn |
|-----------------------|---------------------|
| Game code (`.gd`) | godot-gdscript-specialist |
| Shader / material files (`.gdshader`) | godot-shader-specialist |
| UI / screen files (`.tscn` with UI nodes) | ui-programmer |
| Scene / prefab / level files (`.tscn`) | godot-specialist |
| Native extension / plugin files (C++) | godot-gdextension-specialist |
| General architecture review | lead-programmer |
