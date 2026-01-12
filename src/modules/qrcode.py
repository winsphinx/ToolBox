#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import zipfile
from io import BytesIO

from PIL import Image
from pywebio.output import put_button, put_file, put_loading, put_markdown, put_scope, use_scope
from pywebio.pin import pin, put_file_upload

from utils import display_random_pet


def put_picture(png_data_list):
    output_buffers = []
    # 创建整体图层大小为 A4 纸
    dpi = 300
    w, h = 210, 297
    w = int(w * dpi / 25.4)
    h = int(h * dpi / 25.4)

    # 调整每个二维码尺寸为 m x n
    m, n = 27, 27
    m = int(m * dpi / 25.4)
    n = int(n * dpi / 25.4)

    for f in range(0, len(png_data_list), 45):
        image = Image.new("RGB", (w, h), "white")

        chunk = png_data_list[f : f + 45]
        for i in range(len(chunk)):
            # 左上角坐标 (x, y)
            col = i % 5
            row = i // 5
            x, y = 50 + col * 500, 70 + row * 383
            try:
                chunk[i].seek(0)
                overlay = Image.open(chunk[i]).convert("RGBA").resize((m, n))
                image.paste(overlay, (x, y))
            except Exception:
                pass

        output_image_buffer = BytesIO()
        image.save(output_image_buffer, format="PNG")
        output_image_buffer.seek(0)
        output_buffers.append(output_image_buffer)

    return output_buffers


class QRCode:
    def __init__(self):
        display_random_pet()

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
            try:
                input_zip_content = pin["zip_file"]["content"]
                input_zip_buffer = BytesIO(input_zip_content)
                png_data_list = []

                with zipfile.ZipFile(input_zip_buffer, "r") as zf:
                    for filename in zf.namelist():
                        if filename.lower().endswith(".png"):
                            png_data = zf.read(filename)
                            png_data_list.append(BytesIO(png_data))

                if len(png_data_list):
                    output_zip_buffer = BytesIO()
                    output_image_buffers = put_picture(png_data_list)

                    with zipfile.ZipFile(output_zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf_out:
                        for i, img_buffer in enumerate(output_image_buffers):
                            img_buffer.seek(0)
                            zf_out.writestr(f"qrcode_{i}.png", img_buffer.read())

                    output_zip_buffer.seek(0)

                else:
                    content = "压缩包内没有图片文件，请检查文件格式！"

            except TypeError:
                content = "没有找到文件！请上传！"

        try:
            put_file(
                f"QRCode-{time.strftime('%Y%m%d%H%M', time.localtime(time.time()))}.zip",
                output_zip_buffer.getvalue(),
                ">> 点击下载生成后的文件 <<",
            )
        except UnboundLocalError:
            put_markdown(content)


if __name__ == "__main__":
    QRCode()
