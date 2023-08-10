#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pywebio import start_server
from pywebio.output import put_buttons
from pywebio.session import go_app

from callgroup import Callgroup
from reversepolarity import Reversepolarity


def index():
    put_buttons(["轮选组脚本生成器"], [lambda: go_app("callgroup")])
    put_buttons(["反极性脚本生成器"], [lambda: go_app("reversepolarity")])


def callgroup():
    cg = Callgroup()


def reversepolarity():
    rp = Reversepolarity()


start_server([index, callgroup, reversepolarity], port=7086)
