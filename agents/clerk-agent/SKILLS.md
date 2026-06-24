# 文员 Agent — 可用 Skills

## cli-anything-wps ⭐ 核心
- **用途**：通过 COM 自动化操控 WPS Office（文字/表格/演示）
- **使用时机**：创建或编辑 Word 文档、Excel 表格、PPT 演示文稿时
- **效果**：
  - **Writer（文字）**：添加段落/标题/列表/表格/图片、查找替换、导出 DOCX/PDF
  - **Calc（表格）**：单元格读写、范围填充、公式、Sheet 管理、导出 XLSX/CSV/PDF
  - **Impress（演示）**：幻灯片增删、4 套设计预设、14 种布局模板、5 维度质量审查
  - **Style**：创建/修改/应用样式预设
  - **Export**：导出 DOCX/PDF/XLSX/PPTX/CSV/HTML 等 12 种格式
- **前置条件**：Windows + WPS Office 12.0+ + Python 3.10+ + pywin32
- **Agent 使用要点**：
  - 所有命令支持 `--json` 标志，返回结构化 JSON
  - 使用 `--project` 标志加载项目文件，链式执行命令
  - 做 PPT 时先 `preset apply <名称>` 选择风格，再按序列逐页制作

## pdf
- **用途**：PDF 全功能处理（读/写/合并/拆分/旋转/加密/水印/OCR/填表）
- **使用时机**：需要处理 PDF 文件时——提取内容、转换格式、合并归档、加密保护
- **效果**：
  - **读取**：提取文本（pdfplumber 保布局）、提取表格→DataFrame、元数据读取
  - **写入**：从零创建 PDF（reportlab）、多页文档、子标题/上标支持
  - **操作**：合并多个 PDF、拆分页面、旋转、水印、加密/解密
  - **OCR**：扫描件文字识别（pytesseract + pdf2image）
- **技术栈**：pypdf + pdfplumber + reportlab + qpdf + pytesseract

## pdf-converter
- **用途**：高精度文档格式转换（基于 MinerU 精准解析 API v4）
- **使用时机**：大文件 PDF→Word 转换、扫描件 OCR、需保留公式/表格的复杂文档
- **前置条件**：需注册 MinerU token（`mineru-open-api auth`）
- **效果**：
  - **extract**：高精度，200MB/600页，支持多格式输出（md/json/html/latex/docx）
  - **批量处理**：支持通配符和文件列表批量转换
- **支持格式**：输入 PDF/PNG/JPG/DOCX/PPTX/XLSX/HTML，输出 md/json/html/latex/docx
- **语言**：支持 80+ 语言，默认中文+英文
- **API 参考**：详见 [mineru-api-reference.md](mineru-api-reference.md)

## infographic
- **用途**：模板化信息图生成（KPI 仪表盘、时间轴、路线图、SWOT、漏斗等）
- **使用时机**：需要将数据/流程/对比可视化时
- **效果**：60+ 模板覆盖 7 大类场景：
  - **列表/清单**：功能网格、清单、徽章卡片
  - **时间轴/里程碑**：时间线、产品路线图
  - **步骤/流程**：阶梯图、蛇形步骤、漏斗图
  - **对比**：A vs B 对比、SWOT 分析
  - **矩阵**：优先级四象限
  - **图表**：饼图/环形图/柱状图/折线图/词云
  - **层级**：组织架构树、层级图
- **语法**：空格分隔 key-value（非 YAML），2 空格缩进

## infocard
- **用途**：杂志级排版信息卡（HTML/CSS 直接嵌入 Markdown）
- **使用时机**：制作知识摘要、数据亮点卡、项目快报、事件公告时
- **效果**：
  - 30+ 视觉风格（学术论文/商务简洁/科技蓝图/日式极简/新粗野主义等）
  - 40+ 布局骨架（英雄卡/指标板/对比面板/时间线/合规审计/风险登记等）
  - 自动感应内容密度×结构×情绪，匹配配色和布局
- **关键规则**：HTML 直接嵌入不含代码块，HTML 结构内不能有空行
