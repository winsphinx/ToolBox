#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import time

from pywebio.output import put_button, put_file, put_markdown, put_scope, use_scope
from pywebio.pin import pin, put_file_upload, put_textarea

from utils import display_random_pet


def smart_decode(content):
    for charset in ["utf-16", "gbk", "utf-8", "utf-8-sig"]:
        try:
            return content.decode(charset)
        except UnicodeDecodeError:
            continue
    return content


class Hw2Zx:
    def __init__(self):
        display_random_pet()

        put_markdown("# HW 转 ZX 专线脚本生成器")
        put_textarea(
            name="code",
            label="在下面文本框中粘贴 HW 脚本内容，以 # 作为分割。",
            placeholder="interface Eth-Trunk...\n.....\n.....\n.....\n#",
        )
        put_file_upload(
            name="code_file",
            label="或者，直接上传 HW 脚本",
            accept=".txt",
            placeholder="上传 HW 配置文件",
        )
        put_button(
            label="点击生成 ZX 脚本",
            onclick=self.update,
        )
        put_markdown("----")
        put_scope("output")

    @use_scope("output", clear=True)
    def update(self):
        content = ""
        params = []
        if pin["code"]:
            code = "\n" + pin["code"]
        elif pin["code_file"]:
            code = smart_decode(pin["code_file"]["content"])
        else:
            return

        code = code.replace("\r\n", "\n").replace("\xa0", " ")
        segments = re.findall(r"(interface Eth-Trunk.*?(?=interface Eth-Trunk|$))", code, re.DOTALL)

        for segment in segments:
            vid_match = re.search(r"interface Eth-Trunk\d+\.(\d+)", segment)
            desc_match = re.search(r"description (.+)", segment)

            ipv4_match = re.search(r"ip address (\d+\.\d+\.\d+\.\d+) (\d+\.\d+\.\d+\.\d+)", segment)
            ipv6_match = re.search(r"ipv6 address ([\da-fA-F:]+/\d+)", segment)
            policy_match = re.search(r"traffic-policy\s+(\S+)\s+outbound", segment)

            dot1q_match = re.search(r"dot1q termination vid (\d+)", segment)
            qinq_match = re.search(r"qinq termination pe-vid (\d+) ce-vid (\d+)", segment)

            bas_match = re.search(r"bas\s+access-type layer2-subscriber", segment)
            ipoe_match = re.search(r"user-vlan (\d+) qinq (\d+)", segment)
            qos_match = re.search(r"qos-profile (\S+) (?:inbound|outbound)", segment)
            user_match = re.search(r"static-user (\S+) (\d+\.\d+\.\d+\.\d+) .* domain-name (\S+)", segment)

            if vid_match:
                param = {
                    "vid": vid_match.group(1),
                    "description": desc_match.group(1).strip() if desc_match else "No Description",
                    "policy": policy_match.group(1) if policy_match else "NoWebNoDNS",
                    "ipv4": ipv4_match.group(1) if ipv4_match else False,
                    "mask": ipv4_match.group(2) if ipv4_match else False,
                    "ipv6": ipv6_match.group(1) if ipv6_match else False,
                    "dot1q": dot1q_match.group(1) if dot1q_match else False,
                    "qinq_pv": qinq_match.group(1) if qinq_match else False,
                    "qinq_cv": qinq_match.group(2) if qinq_match else False,
                    "ipoe_mode": True if bas_match else False,
                    "ipoe_iv": ipoe_match.group(1) if ipoe_match else False,
                    "ipoe_ev": ipoe_match.group(2) if ipoe_match else False,
                    "qos": qos_match.group(1) if qos_match else False,
                    "user_id": user_match.group(1) if user_match else False,
                    "user_ip": user_match.group(2) if user_match else False,
                    "domain": user_match.group(3) if user_match else False,
                }
                params.append(param)

        for item in params:
            if item["dot1q"]:
                content += f"""\n\ninterface smartgroup1.{item["vid"]}
 description {item["description"]}
  ip address {item["ipv4"]} {item["mask"]}
  encapsulation-dot1q {item["vid"]}
  ipv4-access-group egress {item["policy"]}
  ipv4 verify unicast source reachable-via any ignore-default-route
"""
                if item["ipv6"]:
                    content += f"""  ipv6 enable
  ipv6 address {item["ipv6"]}
  ipv6-access-group egress {item["policy"]}
  ipv6 verify unicast source reachable-via any ignore-default-route
!
"""
                else:
                    content += "!"

            elif item["qinq_cv"]:
                content += f"""\n\ninterface smartgroup1.{item["vid"]}
 description {item["description"]}
  ip address {item["ipv4"]} {item["mask"]}
  qinq internal-vlanid {item["qinq_cv"]} external-vlanid {item["qinq_pv"]}
  ipv4-access-group egress {item["policy"]}
  ipv4 verify unicast source reachable-via any ignore-default-route
"""
                if item["ipv6"]:
                    content += f"""  ipv6 enable
  ipv6 address {item["ipv6"]}
  ipv6-access-group egress {item["policy"]}
  ipv6 verify unicast source reachable-via any ignore-default-route
!
"""
                else:
                    content += "!"

            elif item["ipoe_mode"]:
                domain = item["domain"] or "default"
                prefix = domain.split("_")[0].upper() if "_" in domain else domain.upper()
                content += f"""\n\ninterface smartgroup1.{item["vid"]}
  description {item["description"]}
  qinq internal-vlanid {item["ipoe_iv"]} external-vlanid {item["ipoe_ev"]}
!
vcc-configuration
  interface smartgroup1.{item["vid"]}
    encapsulation multi
!
vbui-configuration
  interface vbui1000
    ip-host description {item["user_id"]} {item["user_ip"]} smartgroup1.{item["vid"]} vlan {item["ipoe_ev"]} sec-vlan {item["ipoe_iv"]} author-temp-name {item["qos"]} user-info {domain} {domain} {prefix} group-user export
!
"""

        put_markdown(content)

        day = time.strftime("%Y-%m-%d", time.localtime(time.time()))
        put_file(f"{day}.txt", content.encode(), ">> 点击下载脚本 <<")


if __name__ == "__main__":
    Hw2Zx()
