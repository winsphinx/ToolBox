#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from pywebio.output import put_button, put_loading, put_markdown, put_scope, put_text, use_scope
from pywebio.pin import pin, put_textarea

from utils import display_random_pet


class Position:
    def __init__(self):
        display_random_pet()

        put_markdown("# IP 地址-地理位置 查询工具")
        put_textarea(
            "ip",
            label="IP 地址",
            placeholder="192.168.1.100\n110.0.0.0\n...",
            help_text="输入一个或多个 IP 地址，每行一个。因 api 限制，每分钟最大查询请求为15次，超出会被封禁1小时。",
        )
        put_button(
            label="点击查看位置",
            onclick=self.update,
        )
        put_markdown("----")
        put_scope("output")

    @use_scope("output", clear=True)
    def update(self):
        with put_loading():
            if not pin["ip"] or not pin["ip"].strip():
                put_text("请输入 IP 地址")
                return

            ips = [s.strip() for s in pin["ip"].strip().split("\n") if s.strip()]
            if not ips:
                put_text("请输入有效的 IP 地址")
                return

            url = "http://ip-api.com/batch?lang=zh-CN"
            try:
                response = requests.post(url, json=ips, timeout=10)
                response.raise_for_status()
                total_data = response.json()
            except requests.exceptions.RequestException as e:
                put_text(f"请求失败: {e}")
                return
            except (ValueError, KeyError) as e:
                put_text(f"解析响应失败: {e}")
                return

            results = []
            for data in total_data:
                if data.get("status") == "success":
                    lon = f"{'东经' if data['lon'] >= 0 else '西经'}{abs(data['lon'])}°"
                    lat = f"{'北纬' if data['lat'] >= 0 else '南纬'}{abs(data['lat'])}°"
                    results.append(f"IP: {data['query']} → {data['country']} {data['regionName']} {data['city']} ({lon}, {lat})")
                else:
                    results.append(f"IP: {data.get('query', 'unknown')} → 无法获取")

            put_text("\n".join(results))


if __name__ == "__main__":
    Position()
