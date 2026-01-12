#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time

from pywebio.output import put_button, put_file, put_markdown, put_scope, put_text, use_scope
from pywebio.pin import pin, put_textarea

from utils import display_random_pet


class Reversepolarity:
    def __init__(self):
        display_random_pet()

        put_markdown("# 反极性脚本生成器")
        put_textarea(
            "numbers",
            label="号码",
            placeholder="sippstnuser add 0/2/1 0 telno 8657588111111\nsippstnuser add 0/2/4 0 telno 8657588222222\n...",
            help_text="从 GPON 复制的数据（进 esl user，运行 disp cu），每行一个号码。",
        )
        put_button(
            label="点击生成脚本",
            onclick=self.update,
        )
        put_markdown("----")
        put_scope("output")

    @use_scope("output", clear=True)
    def update(self):
        try:
            numbers = [s.strip() for s in str(pin["numbers"]).strip().split("\n")]
            data = [(x.split()[5], x.split()[2]) for x in numbers]

            content = "## PON\n```"
            content += "esl user\n\n"

            for num, port in data:
                content += f"sippstnuser rightflag set {port} telno {num} auto-reverse-polarity enable\n\n"
            content += "\n"

            for _, port in data:
                content += f"sippstnuser attribute set {port} potslinetype PayPhone\n\n"
            content += "\nquit\n\npstnport\n\n"

            for _, port in data:
                content += f"pstnport attribute set {port} clip-reverse-pole-pulse enable\n\n"
            content += "\nquit\n\nsave\n\n"

            content += "```\n\n## SSS\n```\n"
            for num, _ in data:
                content += f'SET OSU SBR:PUI="tel:+{num}",USERTYPE="RVSPOL",CHARGCATEGORY="NORMAL";\n\n'

            content += "```\n"

            put_markdown(content)

            day = time.strftime("%Y-%m-%d", time.localtime(time.time()))
            put_file(f"{day}.txt", content.encode(), ">> 点击下载脚本 <<")

        except IndexError:
            put_text("你得按照提示里的格式输入。")


if __name__ == "__main__":
    Reversepolarity()
