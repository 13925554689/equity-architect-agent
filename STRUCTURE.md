# 项目结构说明

投融资股权架构智能体/
├── app.py                    # Flask主应用（端口5299）
├── requirements.txt          # Python依赖
├── start.bat                 # Windows启动脚本
├── start.sh                  # Linux/Mac启动脚本
├── README.md                 # 项目文档
│
├── knowledge_base/           # 知识库目录
│   ├── regulations/          # 法规库（JSON格式）
│   │   ├── jiuminiyao.json  # 九民纪要（对赌协议）
│   │   └── ...
│   ├── cases/                # 案例库
│   │   ├── deepseek.json    # DeepSeek股权架构案例
│   │   └── ...
│   └── templates/            # 架构模板库
│       ├── startup_basic.json  # 创业公司基础架构
│       └── ...
│
├── modules/                  # 核心模块
│   ├── __init__.py
│   ├── knowledge_base.py    # 知识库引擎（SQLite+FTS5）
│   ├── analyzer.py          # 架构分析引擎
│   ├── generator.py         # 架构生成引擎
│   ├── risk_scanner.py      # 风险扫描器（22类风险）
│   ├── optimizer.py         # 优化建议引擎
│   └── renderer.py          # 报告渲染器
│
├── templates/                # Web界面
│   ├── index.html           # 首页（口令入口）
│   ├── generate.html        # 生成架构页面
│   └── audit.html           # 审核架构页面
│
├── scripts/                  # 脚本
│   └── init_db.py           # 初始化数据库
│
├── data/                     # 数据库
│   └── equity_architect.db  # SQLite数据库
│
├── uploads/                  # 上传文件临时目录
│
└── outputs/                  # 输出目录
    ├── reports/              # 生成的报告（TXT格式）
    └── diagrams/             # 架构图（ASCII格式）

## 文件说明

### 核心文件
- **app.py**: Flask应用入口，处理HTTP请求，路由到各个模块
- **modules/knowledge_base.py**: 知识库管理，支持法规/案例/模板的检索
- **modules/generator.py**: 根据用户需求生成最优股权架构方案
- **modules/analyzer.py**: 分析现有架构，识别问题
- **modules/risk_scanner.py**: 扫描22类常见风险（P0/P1/P2三级）
- **modules/optimizer.py**: 基于分析结果给出优化方案
- **modules/renderer.py**: 生成文本报告和架构图

### 知识库格式
所有知识库文件采用JSON格式，便于扩展和维护。

**法规示例** (knowledge_base/regulations/jiuminiyao.json):
```json
{
  "regulation_id": "jiuminiyao_2019",
  "title": "全国法院民商事审判工作会议纪要",
  "category": "对赌协议",
  "effective_date": "2019-11-08",
  "keywords": ["对赌协议", "估值调整", "股权回购"],
  "key_points": [...]
}
```

**案例示例** (knowledge_base/cases/deepseek.json):
```json
{
  "case_id": "deepseek_2025",
  "company": "DeepSeek（杭州深度求索）",
  "architecture_type": "多层持股平台",
  "highlights": [...],
  "structure": {...},
  "lessons": [...]
}
```

**模板示例** (knowledge_base/templates/startup_basic.json):
```json
{
  "template_id": "startup_basic",
  "name": "创业公司基础架构",
  "architecture_type": "有限合伙持股平台",
  "applicable_scenarios": [...],
  "structure": {...},
  "pros": [...],
  "cons": [...]
}
```

## 扩展指南

### 1. 添加新法规
在 `knowledge_base/regulations/` 创建JSON文件，重启应用自动加载。

### 2. 添加新案例
在 `knowledge_base/cases/` 创建JSON文件。

### 3. 添加新模板
在 `knowledge_base/templates/` 创建JSON文件。

### 4. 新增风险规则
编辑 `modules/risk_scanner.py` 的 `_load_risk_rules()` 方法。

### 5. 自定义报告格式
编辑 `modules/renderer.py` 的报告生成方法。

## 数据库结构

SQLite数据库（data/equity_architect.db）包含3张主表：

1. **regulations**: 法规库
2. **cases**: 案例库  
3. **templates**: 模板库

支持FTS5全文检索。
