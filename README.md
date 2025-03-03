# 腾讯JCC API接口监听与分析工具

这是一款基于Playwright的高级网络请求监听工具，专门设计用于捕获并分析jcc.qq.com网站上的所有API接口。该工具能自动访问多个页面，监听网络请求，并按照版本和API类型分类保存数据，方便后续分析与调试。

## 功能特点

- 🌐 **多页面监听**：自动访问多个JCC页面并监听所有网络请求
- 📊 **全面数据捕获**：捕获所有API请求的详细信息，包括URL、方法、头信息、请求参数和响应数据
- 📁 **结构化存储**：按照版本（如"天选福星"/"双城传说II"）和API类型（英雄/装备/阵容等）分类保存数据
- 📄 **多格式输出**：每种API数据同时生成JSON、cURL和fetch格式，满足不同使用场景
- 🔄 **版本自动切换**：支持不同游戏版本的数据捕获，自动区分不同版本的API

## 数据存储结构

```
data/
├── all_api_requests_[timestamp].json    # 所有API请求的汇总数据
├── pages/                               # 按页面分类的API数据
│   ├── index_api_[timestamp].json
│   ├── lineup_api_[timestamp].json
│   └── ...
└── crawler/
    └── api/
        ├── 天选福星/                     # 版本1
        │   ├── hero/                    # 英雄相关API
        │   │   ├── json/
        │   │   ├── curl/
        │   │   └── fetch/
        │   ├── equipment/               # 装备相关API
        │   │   ├── json/
        │   │   ├── curl/
        │   │   └── fetch/
        │   ├── lineup/                  # 阵容相关API
        │   │   ├── json/
        │   │   ├── curl/
        │   │   └── fetch/
        │   └── ...
        ├── 双城传说II/                   # 版本2
        │   ├── hero/
        │   ├── equipment/
        │   └── ...
        └── common/                      # 通用API
            ├── json/
            ├── curl/
            └── fetch/
```

## 安装要求

```bash
# 安装依赖
pip install -r requirements.txt

# 安装Playwright浏览器
playwright install chromium
```

## 使用方法

### 基本使用

```bash
# 克隆仓库
git clone https://github.com/your-username/jcc-api-capture.git
cd jcc-api-capture

# 运行脚本
python api_capture.py
```

### 运行过程

1. 脚本将启动Chromium浏览器
2. 依次访问配置的URL（index、lineup、hero等页面）
3. 对每个页面自动切换游戏版本（如"天选福星"和"双城传说II"）
4. 监听并记录所有网络请求
5. 按版本和API类型将数据保存到相应目录

## 配置说明

### API类型配置

`api_config`字典定义了各类API的匹配规则、描述和保存目录：

```python
self.api_config = {
    "chess": {
        "pattern": r"chess\.js",
        "description": "英雄数据",
        "required": True,
        "urls": [],
        "save_dir": "hero",
    },
    # 更多API配置...
}
```

### 版本配置

`version_config`字典定义了不同游戏版本的配置及选择器：

```python
self.version_config = {
    "4": {
        "name": "天选福星",
        "mode": "4",
        "base_url": "/4/14.13.6-S14/",
        "lineup_url": "/m14/11/4/",
        "selector": ".tab-bar a:nth-child(1)",
    },
    "13": { ... },
}
```

## 数据使用指南

### JSON数据

每个API类型的JSON数据存储在对应版本和类型的`json`目录中，包含完整的请求和响应信息：

```json
[
  {
    "url": "https://jcc.qq.com/...",
    "method": "GET",
    "headers": { ... },
    "query_params": { ... },
    "response": {
      "status": 200,
      "headers": { ... },
      "body": { ... }
    },
    "api_type": "chess",
    "api_description": "英雄数据"
  }
]
```

### cURL命令

每个API类型的cURL命令存储在对应版本和类型的`curl`目录中，可以直接在终端中执行测试：

```bash
# 英雄数据 - 天选福星
curl -X GET "https://jcc.qq.com/..." -H "User-Agent: ..." -H "Accept: ..."
```

### fetch命令

每个API类型的fetch命令存储在对应版本和类型的`fetch`目录中，可以在浏览器或Node.js中执行：

```javascript
// 英雄数据 - 天选福星
fetch("https://jcc.qq.com/...", {
  method: "GET",
  headers: { ... }
}).then(response => response.json())
  .then(data => console.log(data))
  .catch(error => console.error("Error:", error));
```

## 常见问题

### 问题1: 浏览器无法启动
**原因**：Playwright浏览器未安装或路径设置不正确。
**解决**：运行`playwright install chromium`安装浏览器。

### 问题2: 某些API未被捕获
**原因**：页面加载时间不足或API请求被阻止。
**解决**：增加`asyncio.sleep()`的等待时间，或检查网络连接。

### 问题3: 数据未按预期存储
**原因**：可能是API分类规则不匹配或目录权限问题。
**解决**：检查`api_config`中的pattern配置，确保匹配规则正确，并检查目录写入权限。

## 后续计划

- 添加命令行参数支持，灵活配置监听选项
- 实现WebSocket请求的监听与分析
- 开发GUI界面，提供更直观的操作体验
- 添加自动API调用测试功能
- 支持更多游戏版本的自动识别

## 许可证

MIT License

## 作者

中国红客联盟技术团队
