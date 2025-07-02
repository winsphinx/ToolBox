#!/usr/bin/env python
# -*- coding: utf-8 -*-

from functools import partial
from random import choice

from pywebio import config, start_server
from pywebio.output import put_button, put_markdown
from pywebio.session import go_app

from modules.addims import AddIMS
from modules.address import Address
from modules.callgroup import Callgroup
from modules.flows import Flows
from modules.ipcal import IPcal
from modules.location import Location
from modules.ngn2ims import Ngn2IMS
from modules.position import Position
from modules.qrcode import QRCode
from modules.reversepolarity import Reversepolarity
from modules.roamusers import Roamusers
from modules.sipcall import Sipcall
from modules.sites import Sites

COLORS = ["primary", "secondary", "success", "danger", "warning", "info", "dark"]

# 工具字典。包含：按钮名称(name), 应用名称(app), 对应的类(cls)
TOOLS_CONFIG = [
    {"name": "轮选组脚本生成器", "app": "callgroup", "cls": Callgroup},
    {"name": "反极性脚本生成器", "app": "reversepolarity", "cls": Reversepolarity},
    {"name": "SIP 数字中继脚本生成器", "app": "sipcall", "cls": Sipcall},
    {"name": "IP 地址计算器", "app": "ipcal", "cls": IPcal},
    {"name": "IP 地址——地理位置 查询工具", "app": "position", "cls": Position},
    {"name": "地址——经纬度 查询工具", "app": "address", "cls": Address},
    {"name": "基站稽核工具", "app": "sites", "cls": Sites},
    {"name": "省际流量分析工具", "app": "flows", "cls": Flows},
    {"name": "IMS 手工加号码脚本生成器", "app": "addims", "cls": AddIMS},
    {"name": "NGN 签转 IMS 脚本生成器", "app": "ngn2ims", "cls": Ngn2IMS},
    {"name": "码化之二维码生成工具", "app": "qrcode", "cls": QRCode},
    {"name": "地理位置范围查询工具", "app": "location", "cls": Location},
    {"name": "漫游用户统计工具", "app": "roamusers", "cls": Roamusers},
]


def create_app_index():
    put_markdown("# 七零八落工具箱")
    for tool in TOOLS_CONFIG:
        put_button(tool["name"], onclick=partial(go_app, tool["app"]), color=choice(COLORS))


if __name__ == "__main__":
    apps = {tool["app"]: (lambda cls=tool["cls"]: lambda: cls())() for tool in TOOLS_CONFIG}
    apps["index"] = create_app_index

    config(title="7086 工具箱", theme="minty")
    start_server(
        apps,
        cdn=True,
        auto_open_webbrowser=True,
        port=7086,
    )
