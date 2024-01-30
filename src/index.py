#!/usr/bin/env python
# -*- coding: utf-8 -*-

from random import choice

from pywebio import start_server
from pywebio.output import put_button, put_markdown
from pywebio.session import go_app

from modules.address import Address
from modules.callgroup import Callgroup
from modules.sipcall import Sipcall
from modules.ipcal import IPcal
from modules.reversepolarity import Reversepolarity
from modules.sites import Sites
from modules.flows import Flows


def index():
    put_markdown("# 七零八落工具箱")

    colors = ["primary", "secondary", "success", "danger", "warning", "info", "light", "dark"]
    put_button("轮选组脚本生成器", onclick=lambda: go_app("callgroup"), color=choice(colors))
    put_button("反极性脚本生成器", onclick=lambda: go_app("reversepolarity"), color=choice(colors))
    put_button("SIP 数字中继脚本生成器", onclick=lambda: go_app("sipcall"), color=choice(colors))
    put_button("IP 地址计算器", onclick=lambda: go_app("ipcal"), color=choice(colors))
    put_button("地址-经纬度 查询工具", onclick=lambda: go_app("address"), color=choice(colors))
    put_button("基站稽核工具", onclick=lambda: go_app("sites"), color=choice(colors))
    put_button("省际流量汇总工具", onclick=lambda: go_app("flows"), color=choice(colors))


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


def server():
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
        ],
        auto_open_webbrowser=True,
        port=7086,
    )


if __name__ == "__main__":
    server()
