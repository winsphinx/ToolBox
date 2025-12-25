#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import time

import requests
from pywebio.output import put_button, put_markdown, put_progressbar, put_row, put_scope, put_table, put_text, set_progressbar, use_scope
from pywebio.pin import pin, put_textarea

from utils import display_random_image

KEY = "3252a68ab8715c2d869ffc388d9ce580"
OUTPUT = "json"


class Address:
    def __init__(self):
        display_random_image()

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

    def get_loc(self, address):
        url = "http://restapi.amap.com/v3/geocode/geo?parameters"
        params = {
            "address": address,
            "key": KEY,
            "output": OUTPUT,
        }
        j = json.loads(requests.get(url, params).content)

        return j["geocodes"][0]["location"]

    @use_scope("output", clear=True)
    def query_address(self):
        try:
            addresses = list(set([s.strip() for s in str(pin["address"]).strip().split("\n")]))
            content = [["地址", "经度", "纬度"]]
            total = len(addresses)
            put_progressbar("bar")

            for address in addresses:
                set_progressbar("bar", (addresses.index(address) + 1) / total)
                try:
                    time.sleep(1)
                    location = self.get_loc(address).split(",")
                    content += [[address, location[0], location[1]]]
                except KeyError:
                    content += [[address, "N/A", "N/A"]]

            put_table(content)

        except IndexError:
            put_text("你得按照提示里的格式输入。")

    def get_addr(self, location):
        url = "https://restapi.amap.com/v3/geocode/regeo?parameters"
        params = {
            "location": location,
            "radius": "25",
            "key": KEY,
            "output": OUTPUT,
        }
        j = json.loads(requests.get(url, params).content)

        return j["regeocode"]["formatted_address"]

    @use_scope("output", clear=True)
    def query_location(self):
        try:
            locations = list(set([s.strip() for s in str(pin["address"]).strip().split("\n")]))
            content = [["经度", "纬度", "地址"]]
            total = len(locations)
            put_progressbar("bar")

            for location in locations:
                set_progressbar("bar", (locations.index(location) + 1) / total)
                try:
                    lat, lon = location.split(",")
                    time.sleep(1)
                    try:
                        address = self.get_addr(location)
                        content += [[lat, lon, address]]
                    except KeyError:
                        content += [[lat, lon, "N/A"]]

                except ValueError:
                    content += [["N/A", "N/A", f"*{location}* 格式错误"]]

            put_table(content)

        except IndexError:
            put_text("你得按照提示里的格式输入。")


if __name__ == "__main__":
    Address()
