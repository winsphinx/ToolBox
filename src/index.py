#!/usr/bin/env python
# -*- coding: utf-8 -*-

from random import choice

from pywebio import start_server
from pywebio.output import put_button, put_markdown
from pywebio.session import go_app

from modules.callgroup import Callgroup
from modules.reversepolarity import Reversepolarity
from modules.ipcal import IPcal


def index():
    put_markdown("# 七零八落工具箱")

    colors = ["primary", "secondary", "success", "danger", "warning", "info", "light", "dark"]
    put_button("轮选组脚本生成器", onclick=lambda: go_app("callgroup"), color=choice(colors))
    put_button("反极性脚本生成器", onclick=lambda: go_app("reversepolarity"), color=choice(colors))
    put_button("IP 地址计算器", onclick=lambda: go_app("ipcal"), color=choice(colors))


def callgroup():
    Callgroup()


def reversepolarity():
    Reversepolarity()


def ipcal():
    IPcal()


def server():
    start_server(
        [
            index,
            callgroup,
            reversepolarity,
            ipcal,
        ],
        auto_open_webbrowser=True,
        port=7086,
    )


if __name__ == "__main__":
    server()
