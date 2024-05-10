#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from pywebio.output import put_button, put_markdown, put_loading, put_scope, put_text, use_scope
from pywebio.pin import pin, put_textarea


class Position:
    def __init__(self):
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
            content = ""

            if pin["ip"]:
                ips = [s.strip() for s in pin["ip"].strip().split("\n")]
                url = "http://ip-api.com/batch?lang=zh-CN"
                response = requests.post(url, json=ips)

                if response.status_code == 200:
                    total_data = response.json()
                    for data in total_data:
                        if data["status"] == "success":
                            ip = data["query"]
                            city = data["city"]
                            country = data["country"]
                            regionName = data["regionName"]
                            lon = "东经" + str(data["lon"]) if data["lon"] >= 0 else "西经" + str(abs(data["lon"]))
                            lat = "北纬" + str(data["lat"]) if data["lat"] >= 0 else "南纬" + str(abs(data["lat"]))
                            content += f"IP 地址 {ip} 对应的地点是：{country} {regionName} {city}，经纬度是：{lon}°，{lat}°。\n"
                        else:
                            content += "无法获取地点信息。\n"
                else:
                    content = "请求失败。"
            else:
                content = "似乎没有输入内容。"

        put_text(content)


if __name__ == "__main__":
    Position()
