#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time

from pywebio.output import put_button, put_file, put_markdown, put_scope, put_text, use_scope
from pywebio.pin import pin, put_textarea


class Reversepolarity:
    def __init__(self):
        put_markdown("# 反极性脚本生成器")
        put_textarea(
            "numbers",
            label="号码",
            placeholder="sippstnuser add 0/2/1 0 telno 8657588111111\nsippstnuser add 0/2/4 0 telno 8657588222222\n...",
            help_text="从GPON复制的数据，每行一个号码。",
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
            numbers = [s.strip() for s in pin["numbers"].strip().split("\n")]
            data = [(x.split()[5], x.split()[2]) for x in numbers]

            content = "=" * 20 + "\n\tPON\n" + "=" * 20 + "\n"
            content += "esl user\n\n"

            for num, port in data:
                content += f"sippstnuser rightflag set {port} telno {num} auto-reverse-polarity enable\n"
            content += "\n"

            for _, port in data:
                content += f"sippstnuser attribute set {port} potslinetype PayPhone\n"
            content += "\nquit\n\npstnport\n\n"

            for _, port in data:
                content += f"pstnport attribute set {port} clip-reverse-pole-pulse enable\n"
            content += "\nquit\n\nsave\n\n"

            content += "=" * 20 + "\n\tSSS\n" + "=" * 20 + "\n"
            for num, _ in data:
                content += f'SET OSU SBR:PUI="tel:+{num}",USERTYPE="RVSPOL",CHARGCATEGORY="NORMAL";\n'

            put_text(content)

            day = time.strftime("%Y-%m-%d", time.localtime(time.time()))
            put_file(f"{day}.txt", content.encode(), ">> 点击下载脚本 <<")

        except IndexError:
            put_text("你得按照提示里的格式输入。")


if __name__ == "__main__":
    Reversepolarity()
