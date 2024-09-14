#!/usr/bin/env python
# -*- coding: utf-8 -*-

from random import choice

from pywebio import config, start_server
from pywebio.output import put_button, put_markdown
from pywebio.session import go_app

from modules.address import Address
from modules.callgroup import Callgroup
from modules.sipcall import Sipcall
from modules.ipcal import IPcal
from modules.reversepolarity import Reversepolarity
from modules.sites import Sites
from modules.flows import Flows
from modules.position import Position
from modules.ngn2ims import NGN2IMS


def index():
    put_markdown("# 七零八落工具箱")

    colors = ["primary", "secondary", "success", "danger", "warning", "info", "dark"]
    put_button("轮选组脚本生成器", onclick=lambda: go_app("callgroup"), color=choice(colors))
    put_button("反极性脚本生成器", onclick=lambda: go_app("reversepolarity"), color=choice(colors))
    put_button("SIP 数字中继脚本生成器", onclick=lambda: go_app("sipcall"), color=choice(colors))
    put_button("IP 地址计算器", onclick=lambda: go_app("ipcal"), color=choice(colors))
    put_button("地址-经纬度 查询工具", onclick=lambda: go_app("address"), color=choice(colors))
    put_button("IP 地址-地理位置 查询工具", onclick=lambda: go_app("position"), color=choice(colors))
    put_button("基站稽核工具", onclick=lambda: go_app("sites"), color=choice(colors))
    put_button("省际流量分析工具", onclick=lambda: go_app("flows"), color=choice(colors))
    put_button("NGN->IMS 脚本生成器", onclick=lambda: go_app("ngn2ims"), color=choice(colors))


def callgroup():
    Callgroup()


def reversepolarity():
    Reversepolarity()


def sipcall():
    Sipcall()


def ipcal():
    IPcal()


def address():
    Address()


def sites():
    Sites()


def flows():
    Flows()


def position():
    Position()


def ngn2ims():
    NGN2IMS()


def server():
    config(title="7086 工具箱", theme="minty")

    start_server(
        [
            index,
            callgroup,
            sipcall,
            reversepolarity,
            address,
            ipcal,
            sites,
            flows,
            position,
            ngn2ims,
        ],
        cdn=False,
        auto_open_webbrowser=True,
        port=7086,
    )


if __name__ == "__main__":
    server()
