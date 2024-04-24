#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from pywebio.output import put_button, put_markdown, put_scope, put_text, use_scope
from pywebio.pin import pin, put_input


class Position:
    def __init__(self):
        put_markdown("# IP 地址-地理位置 查询工具")
        put_input(
            "ip",
            label="IP 地址",
            placeholder="192.168.1.100",
            help_text="输入一个 IP 地址。",
        )
        put_button(
            label="点击查看结果",
            onclick=self.update,
        )
        put_markdown("----")
        put_scope("output")

    @use_scope("output", clear=True)
    def update(self):
        url = f'http://ip-api.com/json/{pin["ip"]}?lang=zh-CN'
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            if data["status"] == "success":
                city = data["city"]
                country = data["country"]
                regionName = data["regionName"]
                lon = data["lon"]
                lat = data["lat"]
                put_text(f'IP 地址 {pin["ip"]} 对应的地点是：{country} {regionName} {city}，经纬度是：{lon}，{lat}')
            else:
                put_text("无法获取地点信息")
        else:
            put_text("请求失败")


if __name__ == "__main__":
    Position()
