#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time

import requests
from pywebio.output import put_button, put_markdown, put_progressbar, put_row, put_scope, put_table, put_text, set_progressbar, use_scope
from pywebio.pin import pin, put_textarea

from utils import display_random_pet

KEY = "3252a68ab8715c2d869ffc388d9ce580"


def _parse_input(text: str) -> list[str]:
    return list({s.strip() for s in text.strip().split("\n") if s.strip()})


def _api_request(url: str, params: dict) -> dict:
    resp = requests.get(url, params, timeout=10)
    resp.raise_for_status()
    return resp.json()


class Address:
    def __init__(self):
        display_random_pet()

        put_markdown("# 地址-经纬度 查询工具")
        put_textarea(
            "address",
            label="地址",
            placeholder="地址1\n地址2\n...或者\n经度,纬度\n...",
            help_text="每行一个地址，或一对经纬度(英文逗号分割)。一次查询只能相同类型，不能混合。",
        )
        put_row(
            [
                put_button(
                    label="点击这里，根据地址查询经纬度",
                    onclick=self.query_address,
                ),
                None,
                put_button(
                    label="点击这里，根据经纬度查询地址",
                    onclick=self.query_location,
                ),
            ]
        )
        put_markdown("----")
        put_scope("output")

    def get_loc(self, address: str) -> str:
        url = "http://restapi.amap.com/v3/geocode/geo"
        params = {"address": address, "key": KEY}
        j = _api_request(url, params)
        return j["geocodes"][0]["location"]

    @use_scope("output", clear=True)
    def query_address(self):
        try:
            addresses = _parse_input(str(pin["address"]))
            content = [["地址", "经度", "纬度"]]
            total = len(addresses)
            put_progressbar("bar")

            for i, address in enumerate(addresses):
                set_progressbar("bar", (i + 1) / total)
                try:
                    time.sleep(1)
                    location = self.get_loc(address).split(",")
                    content.append([address, location[0], location[1]])
                except KeyError, IndexError:
                    content.append([address, "N/A", "N/A"])

            put_table(content)

        except IndexError:
            put_text("你得按照提示里的格式输入。")

    def get_addr(self, location: str) -> str:
        url = "https://restapi.amap.com/v3/geocode/regeo"
        params = {"location": location, "radius": "25", "key": KEY}
        j = _api_request(url, params)
        return j["regeocode"]["formatted_address"]

    @use_scope("output", clear=True)
    def query_location(self):
        try:
            locations = _parse_input(str(pin["address"]))
            content = [["经度", "纬度", "地址"]]
            total = len(locations)
            put_progressbar("bar")

            for i, location in enumerate(locations):
                set_progressbar("bar", (i + 1) / total)
                try:
                    lat, lon = location.split(",")
                    time.sleep(1)
                    try:
                        address = self.get_addr(location)
                        content.append([lat, lon, address])
                    except KeyError, IndexError:
                        content.append([lat, lon, "N/A"])

                except ValueError:
                    content.append(["N/A", "N/A", f"*{location}* 格式错误"])

            put_table(content)

        except IndexError:
            put_text("你得按照提示里的格式输入。")


if __name__ == "__main__":
    Address()
