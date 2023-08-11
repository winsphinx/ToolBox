#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pywebio import start_server
from pywebio.output import put_buttons, put_markdown
from pywebio.session import go_app

from callgroup import Callgroup
from reversepolarity import Reversepolarity


def index():
    put_markdown("# 七零八落工具箱")

    put_buttons(["轮选组脚本生成器"], onclick=lambda: go_app("callgroup"))
    put_buttons(["反极性脚本生成器"], onclick=lambda: go_app("reversepolarity"))


def callgroup():
    cg = Callgroup()


def reversepolarity():
    rp = Reversepolarity()


start_server([index, callgroup, reversepolarity], port=7086)
