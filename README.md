# Raspberry Pi OLED 监控仪表盘

[![MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

基于树莓派和SSD1306 OLED屏的实时监控系统

## 演示效果
<img src="images/oled_dashboard.gif" alt="OLED 仪表盘演示" width="500">

## 功能
- 系统信息：CPU温度、内存、磁盘、运行时间
- 天气数据：温度、湿度、风速、天气状况
- 网络状态：IP地址、主机名
- 自动轮播：3秒切换页面

## 快速开始

1. 安装依赖：
```bash
sudo apt install python3-pip python3-pil
pip3 install luma.oled psutil requests
```

2. 启用I2C：
```bash
sudo raspi-config
# 选择 Interfacing Options > I2C > 启用
```

3. 运行程序：
```bash
python3 oled_dashboard.py
```

## 配置
修改脚本头部常量：
- `WEATHER_API_KEY`: OpenWeatherMap API密钥
- `LATITUDE/LONGITUDE`: 您的位置坐标
- `PAGE_SWITCH_INTERVAL`: 页面切换间隔(秒)

## 硬件要求
- 树莓派 + SSD1306 OLED屏(128x64)
- I2C连接(默认地址0x3C)

## 开源协议
MIT License