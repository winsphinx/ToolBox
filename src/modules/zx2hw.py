#!/usr/bin/env python
# -*- coding: utf-8 -*-

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


class Zx2Hw:
    def __init__(self):
        display_random_pet()

        put_markdown("# ZX 转 HW 专线脚本生成器")
        put_textarea(
            name="code",
            label="在下面文本框中粘贴 ZX 脚本内容。",
            placeholder="...\n.....\n.....\n.....",
        )
        put_file_upload(
            name="code_file",
            label="或者，直接上传 ZX 脚本",
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

        if pin["code"]:
            code = pin["code"]
        elif pin["code_file"]:
            code = smart_decode(pin["code_file"]["content"])
        else:
            return

        code = code.replace("\r\n", "\n").replace("\xa0", " ")

        content = code

        put_markdown(content)

        day = time.strftime("%Y-%m-%d", time.localtime(time.time()))
        put_file(f"{day}.txt", content.encode(), ">> 点击下载脚本 <<")


if __name__ == "__main__":
    Zx2Hw()
