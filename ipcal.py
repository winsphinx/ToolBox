#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import time

from IPy import IP
from pywebio import start_server
from pywebio.output import put_button, put_markdown, put_scope, put_text, use_scope
from pywebio.pin import pin, put_input


class IPcal:
    def __init__(self):
        put_markdown("# IP 地址计算器")
        put_input(
            "ip",
            label="IP 地址",
            placeholder="输入 IPv4/6 地址，如 10.0.1.0/255.255.255.252，或 10.0.1.0/30，或 ::1/126。",
        )
        put_button(label="点击查看结果", onclick=self.update)
        put_markdown("----")
        put_scope("output")

    @use_scope("output", clear=True)
    def update(self):
        ip = IP(pin["ip"])
        content = f"它的网络长度：{ip.len()}\n"
        content += f"它的网络号是：{ip.net()}\n"
        content += f"它的广播地址是：{ip.broadcast()}\n"
        content += f"它的掩码是：{ip.netmask()}\n"

        put_text(content)


if __name__ == "__main__":
    IPcal()
