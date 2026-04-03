#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import time

from pywebio.output import put_button, put_file, put_markdown, put_scope, use_scope
from pywebio.pin import pin, put_file_upload, put_textarea

from utils import display_random_pet

RE_HOST_PATTERN = re.compile(
    r"ip-host description (?P<user>\S+) (?P<ip>\d+\.\d+\.\d+\.\d+) "
    r"(?P<iface>smartgroup\d+\.\d+) vlan (?P<ev>\d+) sec-vlan (?P<iv>\d+)"
    r"(?:\s+author-temp-name\s+(?P<qos>\S+))?"
)
RE_INTERFACE_SEGMENT = re.compile(r"(interface smartgroup\d+\.\d+.*?)(?=interface smartgroup\d+\.\d+|!|\$)", re.DOTALL)
RE_IFACE_NAME = re.compile(r"(smartgroup\d+\.\d+)")
RE_IFACE_VID = re.compile(r"interface smartgroup\d+\.(\d+)")
RE_DESCRIPTION = re.compile(r"description\s+(.+)")
RE_IPV4 = re.compile(r"ip address\s+(\d+\.\d+\.\d+\.\d+)\s+(\d+\.\d+\.\d+\.\d+)")
RE_IPV6 = re.compile(r"ipv6 address\s+([\da-fA-F:]+/\d+)")
RE_DOMAIN = re.compile(r"user-info\s+(\S+)")

BASE_TEMPLATE = """interface Eth-Trunk1.{vid}
  description {description}
"""

IPV4_TEMPLATE = "  ip address {ipv4} {mask}\n"

DOT1Q_TEMPLATE = """ encapsulation dot1q-termination
 dot1q termination vid {vid}
 arp broadcast enable
 traffic-policy Anti-Urpf-In inbound
 traffic-policy NoWeb  outbound
#
"""

QINQ_TEMPLATE = """ encapsulation qinq-termination
 qinq termination pe-vid {pe_vid} ce-vid {ce_vid}
 arp broadcast enable
 traffic-policy Anti-Urpf-In inbound
 traffic-policy NoWeb  outbound
#
"""


def smart_decode(content):
    for charset in ["utf-8-sig", "utf-8", "utf-16"]:
        try:
            return content.decode(charset)
        except UnicodeDecodeError:
            continue
    return content


class Zx2Hw:
    def __init__(self):
        display_random_pet()

        put_markdown("# ZX 转 HW 专线脚本生成器")
        put_textarea(
            name="code",
            label="在下面文本框中粘贴 ZX 脚本内容，以 $ 作为分割。",
            placeholder="interface smartgroup...\n.....\n.....\n.....\n$",
            rows=12,
        )
        put_file_upload(
            name="code_file",
            label="或者，直接上传脚本文件",
            accept=".txt",
            placeholder="上传 ZX 配置文件",
        )
        put_button(
            label="点击生成 HW 脚本",
            onclick=self.update,
        )
        put_markdown("----")
        put_scope("output")

    @use_scope("output", clear=True)
    def update(self):
        content = ""
        code = ""

        if pin["code"]:
            code = pin["code"]
        elif pin["code_file"]:
            code = smart_decode(pin["code_file"]["content"])
        else:
            return

        code = code.replace("\r\n", "\n").replace("\xa0", " ")

        host_map = {}
        for m in RE_HOST_PATTERN.finditer(code):
            iface = m.group("iface")
            if iface not in host_map:
                host_map[iface] = []
            host_map[iface].append({"user": m.group("user"), "ip": m.group("ip"), "ev": m.group("ev"), "iv": m.group("iv"), "qos": m.group("qos")})

        segments = RE_INTERFACE_SEGMENT.findall(code)

        processed_interfaces = set()

        for segment in segments:
            iface_match = RE_IFACE_NAME.search(segment)
            vid_match = RE_IFACE_VID.search(segment)
            if not iface_match or not vid_match:
                continue

            full_iface = iface_match.group(1)
            vid = vid_match.group(1)

            if full_iface in processed_interfaces:
                continue

            desc_match = RE_DESCRIPTION.search(segment)
            description = desc_match.group(1).strip() if desc_match else "No Description"

            ipv4_match = RE_IPV4.search(segment)
            ipv6_match = RE_IPV6.search(segment)

            bas_users = host_map.get(full_iface, [])

            if not ipv4_match and not bas_users:
                continue

            processed_interfaces.add(full_iface)

            if ipv4_match:
                ipv4 = ipv4_match.group(1)
                mask = ipv4_match.group(2)
                ipv6 = ipv6_match.group(1) if ipv6_match else None
                item_data = {"vid": vid, "description": description, "ipv4": ipv4, "mask": mask, "ipv6": ipv6}

                segment_out = BASE_TEMPLATE.format(**item_data)
                if ipv6:
                    segment_out += " ipv6 enable\n"
                segment_out += IPV4_TEMPLATE.format(**item_data)
                if ipv6:
                    segment_out += f"  ipv6 address {ipv6}\n  ipv6 nd ns multicast-enable\n"

                if len(vid) == 8:
                    item_data["pe_vid"], item_data["ce_vid"] = vid[:4], vid[4:]
                    segment_out += QINQ_TEMPLATE.format(**item_data)
                else:
                    segment_out += DOT1Q_TEMPLATE.format(**item_data)
                content += segment_out

            elif bas_users:
                domain_match = RE_DOMAIN.search(code)
                domain = domain_match.group(1) if domain_match else "jtznsx_webdeny"

                first_user = bas_users[0]
                qos_str = ""
                if first_user["qos"]:
                    qos_str = f"   qos-profile {first_user['qos']} inbound identifier none\n"
                    qos_str += f"   qos-profile {first_user['qos']} outbound identifier none\n"

                segment_out = BASE_TEMPLATE.format(vid=vid, description=description)
                segment_out += f"  user-vlan {first_user['iv']} qinq {first_user['ev']}\n"
                segment_out += "  bas\n   access-type layer2-subscriber\n   authentication-method bind\n"
                segment_out += qos_str
                segment_out += "   ip-trigger\n   arp-trigger\n   quit\nquit\n\n"

                for u in bas_users:
                    ip_parts = u["ip"].split(".")
                    gw = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.1"
                    segment_out += f"static-user {u['user']} {u['ip']} {u['ip']} gateway {gw} interface Eth-Trunk1.{vid} vlan {u['iv']} qinq {u['ev']} domain-name {domain} detect export\n"

                segment_out += "!\n"
                content += segment_out

        put_markdown(f"```text\n{content}\n```")

        day = time.strftime("%Y-%m-%d", time.localtime(time.time()))
        put_file(f"{day}.txt", content.encode(), ">> 点击下载脚本 <<")


if __name__ == "__main__":
    Zx2Hw()
