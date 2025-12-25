#!/usr/bin/env python
# -*- coding: utf-8 -*-


from pywebio.output import put_button, put_file, put_loading, put_markdown, put_scope, put_text, use_scope
from pywebio.pin import pin, put_input, put_radio

from utils import display_random_image


class Ngn2IMS:
    def __init__(self):
        display_random_image()

        put_markdown("# NGN->IMS 脚本生成器")
        put_radio(
            "area",
            label="区县",
            options=[
                {"label": "越城", "value": ["10.0.2.147", "10.0.2.19"]},
                {"label": "上虞", "value": ["10.0.2.148", "10.0.2.20"]},
                {"label": "新昌", "value": ["10.0.2.149", "10.0.2.21"]},
                {"label": "嵊州", "value": ["10.0.2.150", "10.0.2.22"]},
                {"label": "柯桥", "value": ["10.0.2.151", "10.0.2.23"]},
                {"label": "诸暨", "value": ["10.0.2.152", "10.0.2.24"]},
            ],
            inline=True,
        )
        put_input(
            "name",
            label="名称",
            placeholder="某某公司",
            help_text="公司名称，不要超过 32 字符。",
        )
        put_button(
            label="点击生成脚本",
            onclick=self.update,
        )
        put_markdown("----")
        put_scope("output")

    @use_scope("output", clear=True)
    def update(self):
        with put_loading():
            put_text("开始生成脚本...")
            area = pin["area"]
            name = str(pin["name"]).strip()
            TXT = f"""
ring check enable

autosave interval on

snmp-agent target-host trap-hostname NCE_P address 10.17.254.41 udp-port  162 trap-paramsname NCE_P

snmp-agent target-host trap-hostname NCE_S address 10.17.254.72 udp-port  162 trap-paramsname NCE_S

snmp-agent target-host trap-paramsname NCE_P v1 securityname private

snmp-agent target-host trap-paramsname NCE_S v1 securityname private

local-digitmap delete all
y

local-digitmap add DefaultNormalDmm normal [2-8]xxxxxSxx|1[34568]xxxxxxxxx|17[0-8]xxxxxxxx|017[0-8]xxxxxxxx|1010xxxx|01[34568]xxxxxxxxx|0[3-9]xxxxxxxxxSx|010xxxxxxxx|02xxxxxxxxx|[48]00xxxxxxx|9xxxx|179xxSx.S|100xx|11[0-69]|116x.|11[68]114|12[02]|12[3-9]xx|x.F|[0-9].S

local-digitmap add DefaultSccDmm scc EExx|ExxFx.E|ExxFx.L|ExFx.E|ExFx.L|Exx.F|EFxx.F|Fxx.F|Exx.Ex.F|ExxEx.Ex.Ex.F|ExxEx.Ex.F|Fxx.Ex.Ex.F|EFxx.Ex.F|Fxx.Ex.F|ExxE.S|EFxxE.S|ExxEx.s

vlan 101 smart

protocol-8021p-pri 6 vlan 101

port vlan 101 0/0 0

port vlan 101 0/0 1

interface vlanif 101

dhcp-client enable

quit

interface sip 0
y

if-sip attribute basic signal-port 5060 media-ip media-dhcp-vlan 101 signal-ip signal-dhcp-vlan 101 home-domain zj.ims.chinaunicom.cn

if-sip attribute basic primary-proxy-ip1 {area[0]} primary-proxy-port 5060

if-sip attribute basic secondary-proxy-ip1 {area[1]} secondary-proxy-port 5060 sipprofile-index 0

if-sip attribute basic srvlogic-index 2

if-sip attribute optional conference-factory-uri *28#

if-sip attribute optional sub-reg-state enable sub-mwi enable proxy-check-mode register

fax-modem parameters vbd-attribute-type chinatelecom

sipprofile delete codec-pri all

sipprofile add codec-pri 0 8 20

sipprofile add codec-pri 1 0 20

sipprofile modify syspara 46 1

sipprofile modify syspara 72 2

sipprofile modify syspara 134 1

sipprofile modify syspara 135 1

sipprofile modify syspara 152 1

sipprofile modify syspara 159 1

sipprofile modify syspara 174 1

sipprofile modify syspara 186 3

sipprofile modify srv-pri 1 2

digitmap-timer short 3

mg-software parameter 13 1

mg-software parameter 28 1

mg-software strpara 15 *33#

mg-software strpara 32 *12#

mg-software strpara 33 *12*(x.)

mg-software strpara 38 *77*

reset
y
quit

save
"""

            content = ""
            content += TXT

        put_text(content)
        put_file(f"{name}.txt", content.encode(), ">> 点击下载脚本 <<")


if __name__ == "__main__":
    Ngn2IMS()
