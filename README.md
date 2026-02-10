# 题库生成系统

一个基于 Python 的题库生成系统，支持接入 Ollama 和 DeepSeek 等模型，用户可以上传中文资料作为知识库，根据关键词、知识库、题型、难度生成题目。

## 项目结构

```
Question-Bank/
├── backend/           # 后端 Python 服务
│   ├── app/           # 应用代码
│   │   ├── generator/ # 题目生成模块
│   │   ├── knowledge/ # 知识库管理模块
│   │   ├── models/    # 模型客户端模块
│   │   └── main.py    # 主应用入口
│   ├── uploads/       # 上传的知识库文件
│   ├── app.log        # 日志文件
│   └── requirements.txt # 依赖文件
└── frontend/          # 前端页面
    └── index.html     # 主页面
```

## 技术栈

- **后端**：FastAPI、Python 3.13.8、Uvicorn
- **前端**：HTML5、CSS3、JavaScript (原生)
- **模型**：Ollama API、DeepSeek API
- **文档**：python-docx (Word 文档生成)
- **日志**：Python logging 模块

## 核心功能

1. **模型配置**：支持 Ollama 和 DeepSeek 模型
2. **知识库管理**：创建、查看、编辑、删除知识库，上传和删除文件
3. **题目生成**：根据关键词、知识库、题型、难度生成题目
   - 支持单选题、多选题、判断题、填空题、问答题
   - 判断题仅支持"是"和"否"两种选项
4. **题目导出**：导出为 Word 文档，使用微软雅黑字体
5. **日志系统**：详细记录服务运行状态，避免打印知识库内容

## 环境要求

- Windows 10+ 或 Linux
- Python 3.13.8+
- Ollama (本地模型)
- 可选：Docker (前端部署)

## 快速开始

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 启动 Ollama 服务

确保 Ollama 服务运行并下载模型（如 `qwen3:1.7b`）。

### 3. 启动后端服务

```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 4. 启动前端服务

```bash
cd frontend
python -m http.server 3000
```

## 访问地址

- **前端界面**：http://localhost:3000
- **后端 API**：http://localhost:8000
- **API 文档**：http://localhost:8000/docs

## 使用流程

1. **配置模型**：选择模型类型、设置服务地址和模型名称
2. **创建知识库**：输入名称和描述，上传中文资料
3. **生成题目**：选择知识库、输入关键词、设置题型和难度
4. **导出题目**：生成后点击 "导出为 Word 文档" 按钮

## API 接口

### 模型配置
- `POST /api/model/config`：保存模型配置

### 知识库管理
- `GET /api/knowledge`：获取所有知识库
- `POST /api/knowledge`：创建知识库
- `PUT /api/knowledge/{kb_id}`：更新知识库
- `DELETE /api/knowledge/{kb_id}`：删除知识库
- `POST /api/knowledge/{kb_id}/upload`：上传文件
- `DELETE /api/knowledge/{kb_id}/files/{filename}`：删除文件

### 题目管理
- `POST /api/questions/generate`：生成题目
- `POST /api/questions/export`：导出题目为 Word 文档

## 日志系统

日志文件位于 `backend/app.log`，记录服务启动、模型调用、题目生成等详细信息，避免打印知识库内容。

## 故障排查

### 端口占用
```bash
# 查找端口 8000 占用
netstat -ano | findstr :8000

# 终止占用进程
taskkill /PID <PID> /F
```

### 模型问题
```bash
# 检查 Ollama 模型
curl http://localhost:11434/api/tags

# 下载模型
ollama pull qwen3:1.7b
```

## 注意事项

- 默认模型：`qwen3:1.7b`
- 支持的文件格式：文本文件、PDF 等
- 日志管理：定期清理 `app.log` 文件
- 性能优化：大型知识库建议使用更强大的模型
- 当知识库没有文件时，点击生成题目会提示具体的中文信息

## 许可证

MIT
