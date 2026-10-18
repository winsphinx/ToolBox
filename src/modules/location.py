#!/usr/bin/env python

import os
from typing import Any

import requests
from pywebio.output import put_button, put_markdown, put_scope, put_table, use_scope
from pywebio.pin import pin, put_input

from utils import display_random_pet

AMAP_KEY = os.environ.get("AMAP_KEY", "")


def _amap_get(url: str, params: dict, timeout: int = 10) -> dict:
    resp = requests.get(url, params=params, timeout=timeout)
    resp.raise_for_status()
    return resp.json()


class Location:
    def __init__(self):
        display_random_pet()

        put_markdown("# 地理位置范围查询工具")
        put_input(
            name="keyword",
            label="要定位的关键词",
            placeholder="超市",
        )
        put_input(
            name="location",
            label="中心位置经纬度",
            placeholder="120.00,30.00",
            help_text="经纬度用英文逗号隔开，小数最多6位。",
        )
        put_input(
            name="radius",
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

    @use_scope(name="output", clear=True)
    def update(self):
        content: list[Any] = [["名称", "地址", "区县", "城市"]]
        keyword = str(pin["keyword"]).strip()
        location = str(pin["location"]).strip()
        radius = str(pin["radius"]).strip()

        data = _amap_get(
            "https://restapi.amap.com/v3/place/around",
            {
                "key": AMAP_KEY,
                "location": location,
                "keywords": keyword,
                "radius": radius,
                "output": "json",
            },
        )

        if data["status"] == "1":
            for poi in data["pois"]:
                content += [[poi["name"], poi["address"], poi["adname"], poi["cityname"]]]
        else:
            content += [[f"请求失败: {data['info']}"]]

        put_table(content)


if __name__ == "__main__":
    Location()
