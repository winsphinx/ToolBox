#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from pywebio.output import put_button, put_markdown, put_scope, put_table, use_scope
from pywebio.pin import pin, put_input

from utils import display_random_image


class Location:
    def __init__(self):
        display_random_image()

        put_markdown("# 地理位置范围查询工具")
        put_input(
            "keyword",
            label="要定位的关键词",
            placeholder="超市",
        )
        put_input(
            "location",
            label="中心位置经纬度",
            placeholder="120.00,30.00",
            help_text="经纬度用英文逗号隔开，小数最多6位。",
        )
        put_input(
            "radius",
            label="搜寻范围",
            placeholder="5000",
            help_text="单位：米。",
        )
        put_button(
            label="点击查看结果",
            onclick=self.update,
        )
        put_markdown("----")
        put_scope("output")

    @use_scope("output", clear=True)
    def update(self):
        content = [["名称", "地址", "区县", "城市"]]
        keyword = str(pin["keyword"]).strip()
        location = str(pin["location"]).strip()
        radius = str(pin["radius"]).strip()

        KEY = "3252a68ab8715c2d869ffc388d9ce580"
        url = f"https://restapi.amap.com/v3/place/around?key={KEY}&location={location}&keywords={keyword}&radius={radius}&output=json"
        response = requests.get(url)
        data = response.json()

        if data["status"] == "1":
            for poi in data["pois"]:
                content += [[poi["name"], poi["address"], poi["adname"], poi["cityname"]]]
        else:
            content += [[f"请求失败: {data['info']}"]]

        put_table(content)


if __name__ == "__main__":
    Location()
