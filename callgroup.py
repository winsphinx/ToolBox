#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

from pywebio.output import put_button, put_file, put_markdown, put_scope, put_text, use_scope
from pywebio.pin import pin, put_input, put_textarea


class Callgroup:
    def __init__(self):
        put_markdown("# 轮选组脚本生成器")
        put_input("name", label="名称")
        put_input("code", label="编号", placeholder="绍兴从50000开始编号。")
        put_input("main_number", label="引示号", placeholder="填写8位号码。")
        put_textarea("sub_numbers", label="小号", placeholder="每行一个号码，回车分割。\n如果引示号本身也参与轮选，则也要将其加入。")
        put_button(label="点击生成脚本", onclick=self.update)
        put_markdown("----")
        put_scope("output")

    def check_5xxxx(self, n):
        return bool(re.match(r"^5\d{4}$", n))

    def check_8num(self, n):
        return bool(re.match(r"^\d{8}$", n))

    @use_scope("output", clear=True)
    def update(self):
        code = pin["code"].strip()
        name = pin["name"].strip()
        main_number = pin["main_number"].strip()
        sub_numbers = [s.strip() for s in pin["sub_numbers"].strip().split("\n")]

        if not self.check_5xxxx(code):
            put_text("错误：请输入5开头的5位编号！")
            return

        if not self.check_8num(main_number):
            put_text("错误：请输入8位引示号！")
            return

        content = f'ADD CALLGROUP:GRPNO="{code}",NAME="{name}";\n'
        content += f'ADD CALLGRPPSI:PSI="tel:+86575{main_number}",GRPNO="{code}";\n'
        content += f'ADD CALLGRPPSI:PSI="sip:+86575{main_number}@zj.ims.chinaunicom.cn",GRPNO="{code}";\n'
        for n in sub_numbers:
            if not self.check_8num(n):
                put_text("错误：请输入8位号码！中间不要有空行。")
                return

            content += (
                f'SET OSU FA:PUI="tel:+86575{n}",PILOT="tel:+86575{main_number}",DISPILOT="YES",CHARGPILOT="YES";\n'
            )
        content += f'SHOW CALLGROUPPUI:PSI="tel:+86575{main_number}";\n'

        put_text(content)
        put_file(f"{code}-{name}.txt", content.encode(), ">> 点击下载脚本 <<")
        put_markdown("**重要提醒：两个 SSS 都要加一遍。**")


if __name__ == "__main__":
    Callgroup()
