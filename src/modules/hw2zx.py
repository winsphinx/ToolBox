#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import time

from pywebio.output import put_button, put_file, put_markdown, put_scope, use_scope
from pywebio.pin import pin, put_file_upload, put_textarea

from utils import display_random_pet

RE_STATIC_USER = re.compile(
    r"static-user\s+(\S+)\s+(\d+\.\d+\.\d+\.\d+)\s+(\d+\.\d+\.\d+\.\d+).*?"
    r"Eth-Trunk\d+\.(\d+)\s+vlan\s+(\d+)\s+qinq\s+(\d+)\s+"
)
RE_INTERFACE_SEGMENT = re.compile(r"(interface Eth-Trunk.*?)(?=interface Eth-Trunk|$)", re.DOTALL)
RE_VID = re.compile(r"interface Eth-Trunk\d+\.(\d+)")
RE_DESCRIPTION = re.compile(r"description (.+)")
RE_IPV4 = re.compile(r"ip address (\d+\.\d+\.\d+\.\d+) (\d+\.\d+\.\d+\.\d+)")
RE_IPV6 = re.compile(r"ipv6 address ([\da-fA-F:]+/\d+)")
RE_POLICY = re.compile(r"traffic-policy\s+(\S+)\s+outbound")
RE_DOT1Q = re.compile(r"dot1q termination vid (\d+)")
RE_QINQ = re.compile(r"qinq termination pe-vid (\d+) ce-vid (\d+)")
RE_BAS = re.compile(r"bas\n")
RE_IPOE = re.compile(r"user-vlan (\d+) qinq (\d+)")
RE_QOS = re.compile(r"qos-profile (\S+) (?:inbound|outbound)")

DOT1Q_TEMPLATE = """interface smartgroup1.{vid}
 description {description}
  ip address {ipv4} {mask}
  encapsulation-dot1q {vid}
  ipv4-access-group egress {policy}
  ipv4 verify unicast source reachable-via any ignore-default-route
"""

IPV6_TEMPLATE = """  ipv6 enable
  ipv6 address {ipv6}
  ipv6-access-group egress {policy}
  ipv6 verify unicast source reachable-via any ignore-default-route
!
"""

QINQ_TEMPLATE = """interface smartgroup1.{vid}
 description {description}
  ip address {ipv4} {mask}
  qinq internal-vlanid {qinq_cv} external-vlanid {qinq_pv}
  ipv4-access-group egress {policy}
  ipv4 verify unicast source reachable-via any ignore-default-route
"""

QINQ_BAS_TEMPLATE = """interface smartgroup1.{vid}
  description {description}
  qinq internal-vlanid {ipoe_iv} external-vlanid {ipoe_ev}
!
vcc-configuration
  interface smartgroup1.{vid}
    encapsulation multi
!
"""

USER_TEMPLATE = """vbui-configuration
  interface vbui1000
    ip-host description {user} {start_ip} {end_ip} smartgroup1.{vid} vlan {vlan} sec-vlan {sec_vlan} author-temp-name {qos} user-info jtznsx_webdeny jtznsx_webdeny JTZNSX group-user  export
!
"""


def smart_decode(content):
    for charset in ["utf-8-sig", "utf-8", "utf-16"]:
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
            rows=12,
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
            code = pin["code"]
        elif pin["code_file"]:
            code = smart_decode(pin["code_file"]["content"])
        else:
            return

        code = code.replace("\r\n", "\n").replace("\xa0", " ")

        static_users = RE_STATIC_USER.findall(code)

        segments = RE_INTERFACE_SEGMENT.findall(code)

        for segment in segments:
            vid_match = RE_VID.search(segment)
            desc_match = RE_DESCRIPTION.search(segment)

            ipv4_match = RE_IPV4.search(segment)
            ipv6_match = RE_IPV6.search(segment)
            policy_match = RE_POLICY.search(segment)

            dot1q_match = RE_DOT1Q.search(segment)
            qinq_match = RE_QINQ.search(segment)

            bas_match = RE_BAS.search(segment)
            ipoe_match = RE_IPOE.search(segment)
            qos_match = RE_QOS.search(segment)

            if vid_match:
                param = {
                    "vid": vid_match.group(1),
                    "description": desc_match.group(1).strip() if desc_match else "No Description",
                    "policy": policy_match.group(1) if policy_match else "NoWebNoDNS",
                    "ipv4": ipv4_match.group(1) if ipv4_match else None,
                    "mask": ipv4_match.group(2) if ipv4_match else None,
                    "ipv6": ipv6_match.group(1) if ipv6_match else None,
                    "dot1q": dot1q_match.group(1) if dot1q_match else None,
                    "qinq_pv": qinq_match.group(1) if qinq_match else None,
                    "qinq_cv": qinq_match.group(2) if qinq_match else None,
                    "ipoe_mode": True if bas_match else None,
                    "ipoe_iv": ipoe_match.group(1) if ipoe_match else None,
                    "ipoe_ev": ipoe_match.group(2) if ipoe_match else None,
                    "qos": qos_match.group(1) if qos_match else None,
                }
                params.append(param)

        for item in params:
            if item["dot1q"]:
                content += DOT1Q_TEMPLATE.format(**item)
                if item["ipv6"]:
                    content += IPV6_TEMPLATE.format(**item)
                else:
                    content += "!\n"

            elif item["qinq_cv"]:
                content += QINQ_TEMPLATE.format(**item)
                if item["ipv6"]:
                    content += IPV6_TEMPLATE.format(**item)
                else:
                    content += "!\n"

            elif item["ipoe_mode"]:
                content += QINQ_BAS_TEMPLATE.format(**item)
                for user, start_ip, end_ip, vlanid, sec_vlan, vlan in static_users:
                    if item["vid"] == vlanid:
                        user_data = {"user": user, "start_ip": start_ip, "end_ip": end_ip, "sec_vlan": sec_vlan, "vlan": vlan}
                        content += USER_TEMPLATE.format(**item, **user_data)

        put_markdown(f"```text\n{content}\n```")

        day = time.strftime("%Y-%m-%d", time.localtime(time.time()))
        put_file(f"{day}.txt", content.encode(), ">> 点击下载脚本 <<")


if __name__ == "__main__":
    Hw2Zx()
