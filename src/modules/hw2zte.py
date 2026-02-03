#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import time

from pywebio.output import put_button, put_file, put_markdown, put_scope, use_scope
from pywebio.pin import pin, put_textarea

from utils import display_random_pet


class Hw2Zx:
    def __init__(self):
        display_random_pet()

        put_markdown("# HW 转 ZX 专线脚本生成器")
        put_textarea(
            "code",
            label="HW 脚本",
            placeholder="interface Eth-Trunk...\n.....\n.....\n.....\n#",
            help_text="在这里粘贴 HW 脚本内容，以 # 作为分割。",
        )
        put_button(
            label="点击生成 ZX 脚本",
            onclick=self.update,
        )
        put_markdown("----")
        put_scope("output")

    @use_scope("output", clear=True)
    def update(self):
        code = pin["code"]
        segments = re.findall(r"(\ninterface Eth-Trunk.*?\n#)", code, re.DOTALL)

        params = []
        for segment in segments:
            desc_match = re.search(r"description (.+)", segment)
            vid_match = re.search(r"interface Eth-Trunk([\d.]+)", segment)
            ipv4_match = re.search(r"ip address (\d+\.\d+\.\d+\.\d+) (\d+\.\d+\.\d+\.\d+)", segment)
            ipv6_match = re.search(r"ipv6 address ([\da-fA-F:]+/\d+)", segment)
            policy_match = re.search(r"traffic-policy\s+(\S+)\s+outbound", segment)

            dot1q_match = re.search(r"dot1q termination vid (\d+)", segment)
            qinq_match = re.search(r"qinq termination pe-vid (\d+) ce-vid (\d+)", segment)

            if ipv4_match:
                param = {
                    "vid": vid_match.group(1),
                    "description": desc_match.group(1).strip() if desc_match else "no description",
                    "ipv4": ipv4_match.group(1),
                    "mask": ipv4_match.group(2),
                    "ipv6": ipv6_match.group(1) if ipv6_match else "",
                    "policy": policy_match.group(1) if policy_match else "NoWebNoDNS",
                    "dot1q": dot1q_match.group(1) if dot1q_match else None,
                    "qinq_pv": qinq_match.group(1) if qinq_match else None,
                    "qinq_cv": qinq_match.group(2) if qinq_match else None,
                }
                params.append(param)

        content = ""

        for item in params:
            if item["dot1q"]:
                block = f"""interface smartgroup1.{item["vid"]}
 description {item["description"]}
  ipv6 enable
  ip address {item["ipv4"]} {item["mask"]}
  ipv6 address {item["ipv6"]}
  encapsulation-dot1q {item["vid"]}
  ipv4-access-group egress {item["policy"]}
  ipv6-access-group egress {item["policy"]}
  ipv4 verify unicast source reachable-via any ignore-default-route
  ipv6 verify unicast source reachable-via any ignore-default-route
"""
                content += block + "\n\n"

            elif item["qinq_cv"]:
                block = f"""interface smartgroup1.{item["vid"]}
 description {item["description"]}
  ipv6 enable
  ip address {item["ipv4"]} {item["mask"]}
  ipv6 address {item["ipv6"]}
  qinq internal-vlanid {item["qinq_pv"]} external-vlanid {item["qinq_cv"]}
  ipv4-access-group egress {item["policy"]}
  ipv6-access-group egress {item["policy"]}
  ipv4 verify unicast source reachable-via any ignore-default-route
  ipv6 verify unicast source reachable-via any ignore-default-route
"""
                content += block + "\n\n"

        put_markdown(content)

        day = time.strftime("%Y-%m-%d", time.localtime(time.time()))
        put_file(f"{day}.txt", content.encode(), ">> 点击下载脚本 <<")


if __name__ == "__main__":
    Hw2Zx()
