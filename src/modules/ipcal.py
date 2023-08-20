#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ipaddress

from pywebio.output import put_button, put_markdown, put_scope, put_text, use_scope
from pywebio.pin import pin, put_input


class IPcal:
    def __init__(self):
        put_markdown("# IP 地址计算器")
        put_input(
            "ip",
            label="IP 地址",
            placeholder="输入 IP 地址，如 10.0.1.0/255.255.255.252，或 10.0.1.0/30，或 ::1/126。",
        )
        put_button(label="点击查看结果", onclick=self.update)
        put_markdown("----")
        put_scope("output")

    @use_scope("output", clear=True)
    def update(self):
        try:
            interface = ipaddress.ip_interface(pin["ip"])
            content = f"它的网络地址是：{interface.network}\n"

            network = interface.network

            if network.version == 4:
                content += f"它的广播地址是：{network.broadcast_address}\n"
                content += f"它的网络掩码是：{network.netmask}\n"
                content += f"它的主机掩码是：{network.hostmask}\n"

            elif network.version == 6:
                content += f"它的压缩地址是：{network.compressed}\n"
                content += f"它的扩展地址是：{network.exploded}\n"

            content += f"它的地址数量有：{network.num_addresses} 个\n它的可用地址有：\n"
            hosts = [str(x) for x in list(network.hosts())]
            if len(hosts) > 10:
                hosts = hosts[:5] + ["......"] + hosts[-5:]

            content += f"{hosts}"

        except ValueError:
            content = "这不是一个有效的 IP 地址。"

        put_text(content)


if __name__ == "__main__":
    IPcal()
