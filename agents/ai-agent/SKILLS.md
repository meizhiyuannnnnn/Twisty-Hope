# AI 模型 Agent — 可用 Skills

## gemini-api
- **用途**：调用 Google Gemini 模型（文本/多模态/函数调用/流式）
- **使用时机**：项目选择 Gemini 作为 LLM 底座时
- **效果**：覆盖 Gen AI SDK 全功能，含 context caching、embeddings、Live API

## agents-sdk
- **用途**：构建 Cloudflare Workers 上的有状态 AI Agent
- **使用时机**：需要构建持久化、可调度的 AI Agent 服务时
- **效果**：SQLite 持久状态、RPC、定时调度、WebSocket 实时通信

## agent-platform-prompt-management
- **用途**：Prompt 版本管理（Vertex AI SDK）
- **使用时机**：项目 Prompt 需要版本控制、A/B 测试时
- **效果**：创建/列出/检索/版本化 Prompt，变量组装

## agent-platform-model-registry
- **用途**：ML 模型注册和版本管理
- **使用时机**：管理自训练/微调模型时
- **效果**：模型上传、版本管理、元数据维护

## agent-platform-tuning
- **用途**：LLM 微调完整工作流
- **使用时机**：需要为特定领域微调模型时
- **效果**：数据集准备→验证→模型推荐→提交微调→部署
