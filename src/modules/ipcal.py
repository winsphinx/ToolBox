#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ipaddress

from pywebio.output import put_button, put_markdown, put_scope, put_text, use_scope
from pywebio.pin import pin, put_input

from utils import display_random_pet


class IPcal:
    def __init__(self):
        display_random_pet()

        put_markdown("# IP 地址计算器")
        put_input(
            "ip",
            label="IP 地址",
            placeholder="192.168.0.1/24",
            help_text="输入 IP 地址，如 10.0.1.0/255.255.255.252，或 10.0.1.0/30，或 ::1/126。",
        )
        put_input(
            "ip2",
            label="要挖掉的 IP 地址",
            placeholder="192.168.0.10/25",
            help_text="用不到留空。格式同上。",
        )
        put_button(
            label="点击查看结果",
            onclick=self.update,
        )
        put_markdown("----")
        put_scope("output")

    @use_scope("output", clear=True)
    def update(self):
        try:
            interface = ipaddress.ip_interface(pin["ip"])
            network = interface.network
            context = [f"它的网络地址是：{interface.network}"]

            if network.version == 4:
                context.extend(
                    [
                        f"它的广播地址是：{network.broadcast_address}",
                        f"它的网络掩码是：{network.netmask}",
                        f"它的主机掩码是：{network.hostmask}",
                    ]
                )
            else:
                context.extend(
                    [
                        f"它的压缩地址是：{network.compressed}",
                        f"它的扩展地址是：{network.exploded}",
                    ]
                )

            num = network.num_addresses
            power = (num - 1).bit_length()
            context.append(f"它的地址数量有：{num} 个，即 2 的 {power} 次方。")

            if num <= 65536:
                hosts = list(network.hosts())
                if len(hosts) > 10:
                    hosts = [str(h) for h in hosts[:5]] + ["......"] + [str(h) for h in hosts[-5:]]
                else:
                    hosts = [str(h) for h in hosts]
                context.append(f"它的可用地址有：\n{hosts}")

            if pin["ip2"]:
                excluded = ipaddress.ip_interface(pin["ip2"]).network
                remaining = [str(n) for n in network.address_exclude(excluded)]
                context.append(f"\n从 {network} 里抠掉 {excluded} 后，留下的网络是：\n{remaining}")

            put_text("\n".join(context))

        except ValueError, ipaddress.AddressValueError:
            put_text("这不是一个有效的 IP 地址（段）。")


if __name__ == "__main__":
    IPcal()
