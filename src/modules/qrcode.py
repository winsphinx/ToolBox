#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import zipfile
from io import BytesIO
from typing import List

from PIL import Image
from pywebio.output import put_button, put_file, put_loading, put_markdown, put_scope, use_scope
from pywebio.pin import pin, put_file_upload

from utils import display_random_pet

DPI = 300
A4_WIDTH_MM, A4_HEIGHT_MM = 210, 297
QR_WIDTH_MM, QR_HEIGHT_MM = 27, 27
IMAGES_PER_PAGE = 45
GRID_COLS, GRID_ROWS = 5, 9
MARGIN_X, MARGIN_Y = 50, 70
SPACING_X, SPACING_Y = 500, 383


def put_picture(png_data_list: List[BytesIO]) -> List[BytesIO]:
    output_buffers: List[BytesIO] = []
    w = int(A4_WIDTH_MM * DPI / 25.4)
    h = int(A4_HEIGHT_MM * DPI / 25.4)
    qr_w = int(QR_WIDTH_MM * DPI / 25.4)
    qr_h = int(QR_HEIGHT_MM * DPI / 25.4)

    for f in range(0, len(png_data_list), IMAGES_PER_PAGE):
        image = Image.new("RGB", (w, h), "white")
        chunk = png_data_list[f : f + IMAGES_PER_PAGE]

        for i, png_io in enumerate(chunk):
            col = i % GRID_COLS
            row = i // GRID_COLS
            x = MARGIN_X + col * SPACING_X
            y = MARGIN_Y + row * SPACING_Y
            png_io.seek(0)
            overlay = Image.open(png_io).convert("RGBA").resize((qr_w, qr_h))
            image.paste(overlay, (x, y))

        output_image_buffer = BytesIO()
        image.save(output_image_buffer, format="PNG")
        output_image_buffer.seek(0)
        output_buffers.append(output_image_buffer)

    return output_buffers


class QRCode:
    def __init__(self) -> None:
        display_random_pet()
        put_markdown("# 码化之二维码生成工具")
        put_file_upload(
            name="zip_file",
            label="上传二维码打包文件",
            accept=".zip",
            placeholder="将多个 png 格式的二维码文件，打包成一个 zip 文件。",
        )
        put_button(label="开始生成文件", onclick=self.make_file)
        put_markdown("----")
        put_scope("output")

    @use_scope("output", clear=True)
    def make_file(self) -> None:
        output_zip_buffer: BytesIO | None = None
        content: str = ""

        with put_loading():
            try:
                input_zip_content = pin["zip_file"]["content"]
                input_zip_buffer = BytesIO(input_zip_content)
                png_data_list: List[BytesIO] = []

                with zipfile.ZipFile(input_zip_buffer, "r") as zf:
                    for filename in zf.namelist():
                        if filename.lower().endswith(".png"):
                            png_data = zf.read(filename)
                            png_data_list.append(BytesIO(png_data))

                if png_data_list:
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

        if output_zip_buffer:
            filename = f"QRCode-{time.strftime('%Y%m%d%H%M', time.localtime())}.zip"
            put_file(filename, output_zip_buffer.getvalue(), ">> 点击下载生成后的文件 <<")
        else:
            put_markdown(content)


if __name__ == "__main__":
    QRCode()
