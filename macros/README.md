# MuMu模拟器12 宏按键配置说明

本目录包含MuMu模拟器12的标准宏按键配置模板，所有配置文件均使用JSON格式存储。

## 配置文件说明

### 1. macro_templates.json
包含所有标准宏按键配置模板，可以直接复制使用或根据需要修改。

### 2. 标准模板列表

#### 2.1 多点触控 (multi_touch)
- 功能：同时点击多个位置
- 示例：同时点击5个不同位置
- 参数格式：`x1,y1 x2,y2 x3,y3 ...`

#### 2.2 滑动操作 (slide)
- 功能：实现从一点到另一点的滑动
- 示例：完成一次曲线滑动
- 参数格式：`x1,y1 x2,y2 x3,y3 ...`（支持多个中间点）

## 宏指令详细语法说明

### 基础设置指令

1. **尺寸基准 (size)**
```
语法：size [width] [height]
参数：width=坐标系宽度, height=坐标系高度
示例：size 1028 640
说明：设定坐标点(x,y)的基准分辨率，以左上角为坐标原点
```

### 触控操作指令

1. **点击 (click)**
```
语法：click [points]
参数：points=若干个坐标点(x1,y1...xn,yn)
示例：click 100,100 200,200 300,300
说明：按次序点击指定位置
```

2. **连击 (loopclick)**
```
语法：loopclick [points] [time] [count]
参数：
- points=坐标点列表
- time=点击间隔(毫秒)
- count=连续点击次数
示例：loopclick 100,100 10 3
```

3. **滑动 (slide)**
```
语法：slide [points] [time] [count]
参数：
- points=坐标点列表
- time=滑动时间(毫秒)
- count=中间点数量
示例：slide 100,100 200,200 100 10
```

### 按键操作指令

1. **模拟按键 (keypress)**
```
语法：keypress [keys]
参数：keys=按键列表
示例：keypress ctrl a
支持按键：
- 控制键：ctrl/alt/esc/shift/tab/del/ret
- 方向键：up/down/left/right
- 功能键：f1~f12
- 数字键：n0~n9
```

2. **键盘映射 (mapkeypress)**
```
语法：mapkeypress [keys]
参数：keys=映射按键列表
示例：mapkeypress a b c
```

### 高级触控指令

1. **单点操作**
```
touchdown [point] - 按下指定点
touchup - 抬起已按下的点
```

2. **多点操作**
```
multidown [id] [points] - 同时按下多个点
multiup [id] - 抬起指定ID的所有点
```

### 特殊功能指令

1. **文本输入**
```
语法：inputtext [text]
示例：inputtext hello world
```

2. **延时控制**
```
语法：delay [time]
参数：time=延时毫秒数
示例：delay 100
```

3. **循环控制**
```
loopbegin [id] [count] - 开始循环
loopend [id] - 结束循环
```

### 鼠标控制指令

1. **鼠标操作**
```
mousedown [model] [point] - 按下鼠标
mousemove [model] [point] - 移动鼠标
mouseup [model] - 抬起鼠标
```

2. **准星控制**
```
resetsight - 准星复位
entersight [id] - 进入准星模式
exitsight [id] - 退出准星模式
```

### 条件控制指令

```
onkeydown - 当宏按键按下时执行
onkeyup - 当宏按键抬起时执行
```

## 使用说明

1. 复制需要的模板到新的JSON文件
2. 修改坐标和延时参数
3. 在模拟器中导入配置文件

## 注意事项

1. 坐标值(x,y)基于模拟器窗口的相对位置
2. delay 参数单位为毫秒
3. 建议先使用较长的延时测试，确认无误后再调整
4. 使用 release_actions 时注意动作的执行顺序
5. 循环操作要注意设置合适的间隔时间 