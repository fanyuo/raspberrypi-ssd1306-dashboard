#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import netifaces
import socket
import psutil
import requests
import json
from datetime import datetime
from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from luma.core.render import canvas
from PIL import ImageFont, ImageDraw

# =========================
# 常量定义
# =========================
DISPLAY_WIDTH = 128                # OLED屏幕宽度(像素)
DISPLAY_HEIGHT = 64                # OLED屏幕高度(像素)
I2C_ADDRESS = 0x3C                  # OLED设备I2C地址
REFRESH_RATE = 0.1                  # 屏幕刷新间隔(秒)
PAGE_SWITCH_INTERVAL = 5            # 页面切换间隔(秒)
WEATHER_REFRESH_INTERVAL = 60       # 天气信息刷新间隔(秒)
WEATHER_API_KEY = "9b02f684888deb143d54343a65c7833b"  # 天气API密钥
LATITUDE = "39.7228"                 # 纬度
LONGITUDE = "116.3478"               # 经度
WEATHER_URL = (
    f"http://api.openweathermap.org/data/2.5/weather?"
    f"lat={LATITUDE}&lon={LONGITUDE}&appid={WEATHER_API_KEY}&units=metric"
)

# =========================
# 初始化 OLED
# =========================
def init_oled():
    """初始化OLED屏幕"""
    try:
        serial = i2c(port=1, address=I2C_ADDRESS)
        device = ssd1306(serial, width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT)
        device.contrast(50)
        return device
    except Exception as e:
        print(f"OLED初始化失败: {str(e)}")
        raise

# =========================
# 系统信息获取函数
# =========================
def get_interface_ip(iface='wlan0'):
    """获取网络接口IP地址"""
    try:
        addrs = netifaces.ifaddresses(iface)
        return addrs[netifaces.AF_INET][0]['addr']
    except (KeyError, ValueError):
        return "N/A"

def get_hostname():
    """获取设备主机名"""
    try:
        return socket.gethostname()
    except:
        return "UNKNOWN"

def get_cpu_temp():
    """获取CPU温度(摄氏度)"""
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            temp = int(f.read()) / 1000
            return f"{temp:.1f}°C"
    except:
        return "N/A"

def get_memory_usage():
    """获取内存使用百分比"""
    try:
        mem = psutil.virtual_memory()
        return f"{mem.percent}%"
    except:
        return "N/A"

def get_disk_usage():
    """获取磁盘空间使用情况"""
    try:
        disk = psutil.disk_usage('/')
        used = disk.used / (1024**3)
        total = disk.total / (1024**3)
        return f"{used:.1f}G/{total:.1f}G"
    except:
        return "N/A"

def get_uptime():
    """获取系统运行时间"""
    try:
        uptime = datetime.now() - datetime.fromtimestamp(psutil.boot_time())
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{days}d {hours}h {minutes}m {seconds}s"
    except:
        return "N/A"

# =========================
# 天气信息
# =========================
def get_weather():
    """从OpenWeatherMap获取天气信息"""
    try:
        response = requests.get(WEATHER_URL, timeout=5)
        response.raise_for_status()
        data = response.json()
        return {
            'location': 'BUCEA',
            'temp': data['main']['temp'],
            'feels_like': data['main']['feels_like'],
            'humidity': data['main']['humidity'],
            'description': data['weather'][0]['description'],
            'wind': data['wind']['speed'] if 'wind' in data else 0
        }
    except requests.exceptions.RequestException as e:
        print(f"天气API请求失败: {str(e)}")
        return None
    except (KeyError, IndexError) as e:
        print(f"天气数据解析失败: {str(e)}")
        return None

# =========================
# 字体初始化
# =========================
def init_fonts():
    """初始化字体配置"""
    try:
        font_small = ImageFont.truetype("DejaVuSansMono.ttf", 10)
        font_medium = ImageFont.truetype("DejaVuSansMono.ttf", 12)
        font_large = ImageFont.truetype("DejaVuSansMono.ttf", 14)
    except:
        print("警告: 无法加载指定字体，使用默认字体")
        font_small = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_large = ImageFont.load_default()
    return font_small, font_medium, font_large

# =========================
# 绘制状态信息
# =========================
def draw_status(page_num, device, fonts, weather_data, weather_update_time):
    """在OLED屏幕上绘制状态信息"""
    font_small, font_medium, font_large = fonts
    try:
        now = datetime.now()
        current_date = now.strftime("%Y-%m-%d")
        current_time = now.strftime("%H:%M:%S")
        weather_update_time = time.strftime("%H:%M:%S", time.localtime(weather_update_time))
        eth0_ip = get_interface_ip('eth0')
        wlan0_ip = get_interface_ip('wlan0')
        hostname = get_hostname()
        cpu_temp = get_cpu_temp()
        mem_usage = get_memory_usage()
        disk_usage = get_disk_usage()
        uptime = get_uptime()

        with canvas(device) as draw:
            draw.rectangle((0, 0, DISPLAY_WIDTH-1, DISPLAY_HEIGHT-1), outline="white")

            if page_num == 0:  # 页面1
                draw.text((2, 0),  f"HOST:{hostname}", font=font_small, fill="white")
                draw.text((2, 10), f"DATE:{current_date}", font=font_small, fill="white")
                draw.text((2, 20), "IP ADDRESS:", font=font_small, fill="white")
                draw.text((2, 30), f"ETH: {eth0_ip}", font=font_small, fill="white")
                draw.text((2, 40), f"WIFI:{wlan0_ip}", font=font_small, fill="white")

            elif page_num == 1:  # 页面2
                draw.text((2, 0),  f"CPU:{cpu_temp}", font=font_small, fill="white")
                draw.text((2, 10), f"MEM:{mem_usage}", font=font_small, fill="white")
                draw.text((2, 20), f"DISK:{disk_usage}", font=font_small, fill="white")
                draw.text((2, 30), f"UPTIME:{uptime}", font=font_small, fill="white")

            elif page_num == 2:  # 页面3: 天气信息
                if weather_data:
                    draw.text((2, 0),  f"{weather_data['location']}:{weather_data['description']}", font=font_small, fill="white")
                    draw.text((2, 10), f"T:{weather_data['temp']:.1f} °C", font=font_small, fill="white")
                    draw.text((64, 10), f"H:{weather_data['humidity']} %", font=font_small, fill="white")
                    draw.text((2, 20), f"FL: {weather_data['feels_like']:.1f} °C", font=font_small, fill="white")
                    draw.text((2, 30), f"Wind:{weather_data['wind']} m/s", font=font_small, fill="white")
                    draw.text((2, 40), f"UpdatedTime:{weather_update_time}", font=font_small, fill="white")
                else:
                    draw.text((10, 20), "Weather: Failed", font=font_medium, fill="white")

            draw.line((0, 52, DISPLAY_WIDTH, 52), fill="white")
            draw.text((2, 51), f"Page {page_num+1}/3 {current_time}", font=font_small, fill="white")

    except Exception as e:
        print(f"显示错误: {str(e)}")
        with canvas(device) as draw:
            draw.rectangle((0, 0, DISPLAY_WIDTH, DISPLAY_HEIGHT), fill="black")
            draw.text((10, 20), "SYSTEM ERROR", font=font_large, fill="white")
            draw.text((10, 40), "Check logs", font=font_medium, fill="white")

# =========================
# 主程序
# =========================
def main():
    try:
        device = init_oled()
        fonts = init_fonts()
        current_page = 0
        last_page_switch = time.time()
        last_weather_refresh = 0
        weather_data = None

        print("OLED系统监控已启动. 按Ctrl+C退出...")

        while True:
            current_time_ts = time.time()

            if current_time_ts - last_weather_refresh > WEATHER_REFRESH_INTERVAL:
                valid_weather_data = weather_data
                weather_data = get_weather()
                if not weather_data:
                    weather_data = valid_weather_data
                else:
                    weather_update_time = current_time_ts
                last_weather_refresh = current_time_ts

            if current_time_ts - last_page_switch > PAGE_SWITCH_INTERVAL:
                current_page = (current_page + 1) % 3
                last_page_switch = current_time_ts

            # current_page = 2  # 当前锁定为天气页面

            draw_status(current_page, device, fonts, weather_data, weather_update_time)
            time.sleep(REFRESH_RATE)

    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"致命错误: {str(e)}")
    finally:
        try:
            with canvas(device) as draw:
                draw.rectangle((0, 0, DISPLAY_WIDTH, DISPLAY_HEIGHT), fill="black")
            print("显示已清空")
        except:
            pass

# =========================
# 程序入口
# =========================
if __name__ == "__main__":
    main()
