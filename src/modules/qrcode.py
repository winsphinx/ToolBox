#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import zipfile
from io import BytesIO

from PIL import Image
from pywebio.output import put_button, put_file, put_loading, put_markdown, put_scope, use_scope
from pywebio.pin import pin, put_file_upload


def read_inputs(dir):
    filelist = []
    for filename in os.listdir(dir):
        if os.path.splitext(filename)[1] == ".png":
            filelist.append(filename)
    return filelist


def put_picture(filelist):
    # 创建整体图层大小为 A4 纸
    dpi = 300
    w, h = 210, 297
    w = int(w * dpi / 25.4)
    h = int(h * dpi / 25.4)

    # 调整每个二维码尺寸为 m x n
    m, n = 27, 27
    m = int(m * dpi / 25.4)
    n = int(n * dpi / 25.4)

    for f in range(0, len(filelist), 45):
        image = Image.new("RGB", (w, h), "white")

        chunk = filelist[f:f + 45]
        for i in range(len(chunk)):
            # 左上角坐标 (x, y)
            col = i % 5
            row = i // 5
            x, y = 50 + col * 500, 70 + row * 383
            overlay = Image.open(os.path.join("inputs", chunk[i])).resize((m, n))
            image.paste(overlay, (x, y))

        image.save(os.path.join("outputs", f"qrcode_{f//45}.png"))


class QRCode:
    def __init__(self):
        put_markdown("# 码化之二维码生成工具")

        put_file_upload(
            name="zip_file",
            label="上传二维码打包文件",
            accept=".zip",
            placeholder="将多个 png 格式的二维码文件，打包成一个 zip 文件。",
        )

        put_button(
            label="开始生成文件",
            onclick=self.make_file,
        )

        put_markdown("----")
        put_scope("output")

    @use_scope("output", clear=True)
    def make_file(self):
        with put_loading():
            os.makedirs("inputs", exist_ok=True)
            os.makedirs("outputs", exist_ok=True)

            zip_file = BytesIO(pin["zip_file"]["content"])
            zipfile.ZipFile(zip_file, "r").extractall("inputs")
            files = read_inputs("inputs")

            put_picture(files)

            with zipfile.ZipFile("qrcodes.zip", "w", zipfile.ZIP_DEFLATED) as f:
                for file in os.listdir("outputs"):
                    if os.path.splitext(file)[1] == ".png":
                        f.write(os.path.join("outputs", file), file)

            os.system("rd /s /q inputs")
            os.system("rd /s /q outputs")

        put_file(
            f"QRCode-{time.strftime('%Y%m%d%H%M', time.localtime(time.time()))}.zip",
            open("qrcodes.zip", "rb").read(),
            ">> 点击下载生成后的文件 <<",
        )


if __name__ == "__main__":
    QRCode()
