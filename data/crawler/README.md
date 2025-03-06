# 英雄联盟云顶之弈数据爬虫

本目录包含通过爬虫从官方网站获取的英雄联盟云顶之弈游戏数据。数据分为两个主要版本：**天选福星**和**双城传说II**。

## 目录结构

```
data/crawler/
├── api/                    # API数据目录
│   ├── common/             # 通用API数据
│   │   ├── api_other.json  # 其他通用API数据
│   │   └── api_version.json # 版本信息数据
│   ├── 天选福星/           # 天选福星版本数据
│   │   ├── api_chess.json  # 英雄数据
│   │   ├── api_equip.json  # 装备数据
│   │   ├── api_hex.json    # 海克斯数据
│   │   ├── api_job.json    # 职业数据
│   │   ├── api_lineup.json # 阵容数据
│   │   ├── api_other.json  # 其他数据
│   │   ├── api_race.json   # 种族数据
│   │   └── api_trait.json  # 羁绊数据
│   └── 双城传说II/         # 双城传说II版本数据
│       ├── api_chess.json  # 英雄数据
│       ├── api_equip.json  # 装备数据
│       ├── api_hex.json    # 海克斯数据
│       ├── api_job.json    # 职业数据
│       ├── api_lineup.json # 阵容数据
│       ├── api_other.json  # 其他数据
│       ├── api_race.json   # 种族数据
│       └── api_trait.json  # 羁绊数据
└── debug/                  # 调试数据目录
```

## 数据文件说明

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

**使用示例**：
```javascript
// 获取所有3级海克斯
const tier3Hexes = hexData.filter(hex => 
  hex.response.body.data[hex.id].tier === "3");
```

### 4. 职业数据 (api_job.json)

包含游戏中所有职业特质的详细信息。

**主要字段说明**：
- `id`: 职业ID
- `name`: 职业名称
- `desc2`: 职业效果描述(不同等级)
- `numList`: 激活职业效果所需的英雄数量
- `picture`: 职业图标URL

**使用示例**：
```javascript
// 获取特定职业的激活条件
function getJobActivationLevels(jobId) {
  const job = jobData.find(j => j.response.body.data[jobId]);
  if (!job) return null;
  
  return job.response.body.data[jobId].numList.split('|').map(Number);
}
```

### 5. 种族数据 (api_race.json)

包含游戏中所有种族特质的详细信息。

**主要字段说明**：
- `id`: 种族ID
- `name`: 种族名称
- `desc2`: 种族效果描述(不同等级)
- `numList`: 激活种族效果所需的英雄数量
- `picture`: 种族图标URL

**使用示例**：
与职业数据类似的使用方法。

### 6. 羁绊数据 (api_trait.json)

包含游戏中所有羁绊(特质)的详细信息，包括职业和种族。

**主要字段说明**：
- `id`: 羁绊ID
- `name`: 羁绊名称
- `desc2`: 羁绊效果描述
- `numList`: 激活羁绊效果所需的英雄数量
- `picture`: 羁绊图标URL
- `prefix`: 羁绊前缀描述

**使用示例**：
```javascript
// 获取所有羁绊及其激活条件
const traitActivations = traitData.map(trait => {
  const traitInfo = Object.values(trait.response.body.data)[0];
  return {
    name: traitInfo.name,
    levels: traitInfo.numList.split('|').map(Number)
  };
});
```

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

**使用示例**：
```javascript
// 获取所有简单难度的阵容
const easyLineups = lineupData.filter(lineup => 
  lineup.response.body.data.lineup_detail.filter(l => l.difficulty === "1"));
```

### 8. 其他数据 (api_other.json)

包含其他杂项API数据，如图片资源、UI元素等。

### 9. 版本数据 (api_version.json)

包含游戏版本信息。

## 数据使用方法

### 基本读取方法

```javascript
// 使用Node.js读取数据
const fs = require('fs');
const path = require('path');

// 读取英雄数据
const chessDataPath = path.join(__dirname, 'api/天选福星/api_chess.json');
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