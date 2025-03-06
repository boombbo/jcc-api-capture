# 腾讯JCC API接口监听与分析工具

这是一款基于Playwright的高级网络请求监听工具，专门设计用于捕获并分析jcc.qq.com网站上的所有API接口。该工具能自动访问多个页面，监听网络请求，并按照版本和API类型分类保存数据，方便后续分析与调试。

## 功能特点

- 🌐 **多页面监听**：自动访问多个JCC页面并监听所有网络请求
- 📊 **全面数据捕获**：捕获所有API请求的详细信息，包括URL、方法、头信息、请求参数和响应数据
- 📁 **结构化存储**：按照版本（如"天选福星"/"双城传说II"）和API类型（英雄/装备/阵容等）分类保存数据
- 📄 **多格式输出**：支持JSON格式输出，满足不同使用场景
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
        ├── common/                      # 通用API数据
        │   ├── api_other.json           # 其他通用API数据
        │   └── api_version.json         # 版本信息数据
        ├── 天选福星/                     # 天选福星版本数据
        │   ├── api_chess.json           # 英雄数据
        │   ├── api_equip.json           # 装备数据
        │   ├── api_hex.json             # 海克斯数据
        │   ├── api_job.json             # 职业数据
        │   ├── api_lineup.json          # 阵容数据
        │   ├── api_other.json           # 其他数据
        │   ├── api_race.json            # 种族数据
        │   └── api_trait.json           # 羁绊数据
        └── 双城传说II/                   # 双城传说II版本数据
            ├── api_chess.json           # 英雄数据
            ├── api_equip.json           # 装备数据
            ├── api_hex.json             # 海克斯数据
            ├── api_job.json             # 职业数据
            ├── api_lineup.json          # 阵容数据
            ├── api_other.json           # 其他数据
            ├── api_race.json            # 种族数据
            └── api_trait.json           # 羁绊数据
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
        "urls": []
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
        "base_url": "/4/14.14.7-S14/",
        "lineup_url": "/m14/11/4/",
        "selector": ".tab-bar a:nth-child(1)",
    },
    "13": { ... },
}
```

## 数据文件详细说明

### 1. 英雄数据 (api_chess.json)

包含游戏中所有英雄的详细信息，如属性、技能、费用等。

**主要字段说明**：
- `id`: 英雄ID
- `name`: 英雄名称
- `displayName`: 显示名称
- `cost`: 英雄费用(1-5金币)
- `health`: 生命值
- `damage`: 攻击力
- `armor`: 护甲
- `magicResist`: 魔抗
- `DPS`: 每秒伤害
- `attackSpeed`: 攻击速度
- `range`: 攻击范围
- `skillName`: 技能名称
- `skillDesc`: 技能描述
- `skillImage`: 技能图标URL
- `traits`: 英雄拥有的特质(羁绊)列表

**使用示例**：
```javascript
// 获取所有2费英雄
const twoGoldHeroes = chessData.filter(hero => hero.response.body.data[hero.id].cost === "2");

// 获取拥有特定羁绊的英雄
function getHeroesWithTrait(traitId) {
  return chessData.filter(hero => {
    const traits = hero.response.body.data[hero.id].traits.split('|');
    return traits.includes(traitId);
  });
}
```

### 2. 装备数据 (api_equip.json)

包含游戏中所有装备的详细信息，包括基础装备和合成装备。

**主要字段说明**：
- `id`: 装备ID
- `name`: 装备名称
- `desc`: 装备描述
- `from`: 合成所需的基础装备ID
- `imagePath`: 装备图标URL
- `effects`: 装备效果

**使用示例**：
```javascript
// 获取所有基础装备
const basicItems = equipData.filter(item => 
  item.response.body.data[item.id].from === "");

// 获取特定装备的合成路径
function getItemRecipe(itemId) {
  const item = equipData.find(i => i.response.body.data[itemId]);
  if (!item) return null;
  
  const fromItems = item.response.body.data[itemId].from.split('|');
  return fromItems.map(id => equipData.find(i => i.response.body.data[id]));
}
```

### 3. 海克斯数据 (api_hex.json)

包含游戏中所有海克斯增强的详细信息。

**主要字段说明**：
- `id`: 海克斯ID
- `name`: 海克斯名称
- `desc`: 海克斯描述
- `tier`: 海克斯等级(1-3)
- `imagePath`: 海克斯图标URL

### 4. 职业数据 (api_job.json)

包含游戏中所有职业特质的详细信息。

**主要字段说明**：
- `id`: 职业ID
- `name`: 职业名称
- `desc2`: 职业效果描述(不同等级)
- `numList`: 激活职业效果所需的英雄数量
- `picture`: 职业图标URL

### 5. 种族数据 (api_race.json)

包含游戏中所有种族特质的详细信息。

**主要字段说明**：
- `id`: 种族ID
- `name`: 种族名称
- `desc2`: 种族效果描述(不同等级)
- `numList`: 激活种族效果所需的英雄数量
- `picture`: 种族图标URL

### 6. 羁绊数据 (api_trait.json)

包含游戏中所有羁绊(特质)的详细信息，包括职业和种族。

**主要字段说明**：
- `id`: 羁绊ID
- `name`: 羁绊名称
- `desc2`: 羁绊效果描述
- `numList`: 激活羁绊效果所需的英雄数量
- `picture`: 羁绊图标URL
- `prefix`: 羁绊前缀描述

### 7. 阵容数据 (api_lineup.json)

包含游戏中推荐阵容的详细信息。

**主要字段说明**：
- `id`: 阵容ID
- `title`: 阵容名称
- `author`: 作者
- `difficulty`: 难度
- `heroes`: 阵容英雄列表
- `traits`: 阵容激活的羁绊
- `hexes`: 推荐海克斯
- `equipment`: 推荐装备

## 数据使用方法

### 基本读取方法

```javascript
// 使用Node.js读取数据
const fs = require('fs');
const path = require('path');

// 读取英雄数据
const chessDataPath = path.join(__dirname, 'data/crawler/api/天选福星/api_chess.json');
const chessData = JSON.parse(fs.readFileSync(chessDataPath, 'utf8'));

// 处理数据
const heroNames = chessData.map(item => {
  const heroData = Object.values(item.response.body.data)[0];
  return heroData.name;
});
```

### 数据关联

数据文件之间可以通过ID进行关联，例如：

```javascript
// 获取特定英雄的所有羁绊信息
function getHeroTraits(heroId, chessData, traitData) {
  const hero = chessData.find(h => h.response.body.data[heroId]);
  if (!hero) return null;
  
  const traitIds = hero.response.body.data[heroId].traits.split('|');
  return traitIds.map(traitId => {
    const trait = traitData.find(t => t.response.body.data[traitId]);
    return trait ? trait.response.body.data[traitId] : null;
  }).filter(Boolean);
}
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

## 注意事项

1. 数据结构可能随游戏版本更新而变化
2. 部分数据可能包含HTML标签，使用时需要进行处理
3. 图片URL需要与基础URL拼接才能访问
4. 数据中的数值可能是字符串类型，使用前需要转换为数字

## 数据更新

数据通过运行 `api_capture.py` 脚本进行更新，该脚本会自动爬取最新的游戏数据并保存到对应目录。

```bash
python api_capture.py
```

也可以使用 `update.bat` 脚本自动更新并推送到GitHub：

```bash
# 运行更新脚本
update.bat
# 根据提示输入提交信息或直接回车使用默认信息
```

## 后续计划

- 添加命令行参数支持，灵活配置监听选项
- 实现WebSocket请求的监听与分析
- 开发GUI界面，提供更直观的操作体验
- 添加自动API调用测试功能
- 支持更多游戏版本的自动识别

## 许可证

MIT License

## 作者

bobo
