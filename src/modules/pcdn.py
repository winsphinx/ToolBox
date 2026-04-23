#!/usr/bin/env python
# -*- coding: utf-8 -*-

from io import BytesIO

import pandas as pd
from pywebio.output import put_button, put_file, put_loading, put_markdown, put_scope, put_text, use_scope
from pywebio.pin import pin, put_file_upload

from utils import display_random_pet


class Pcdn:
    def __init__(self):
        display_random_pet()

        put_markdown("# PCDN 统计")

        put_file_upload(
            name="pcdn_file",
            label="上传 PCDN文件",
            accept=".xlsx",
            placeholder="excel 格式的文件",
        )
        put_button(
            label="开始匹配文件",
            onclick=self.match_file,
        )

        put_markdown("----")
        put_scope("output")

    @use_scope("output", clear=True)
    def match_file(self):
        with use_scope("output", clear=True):
            try:
                with put_loading():
                    put_text("开始吭哧吭哧生成结果......")

                    upload_info = pin.pcdn_file
                    if upload_info is None:
                        put_text("请先上传文件")
                        return

                    file_content = upload_info["content"]
                    file = BytesIO(file_content)
                    df = pd.read_excel(file)

                    df["日期"] = pd.to_datetime(df["日期"], errors="coerce")
                    df = df.dropna(subset=["日期", "账号"])
                    df = df.sort_values(by=["账号", "日期"], ascending=[True, True])
                    df_final = df.drop_duplicates(subset=["账号"], keep="last")

                    output_buffer = BytesIO()
                    df_final.to_excel(output_buffer, sheet_name="Sheet1", index=False)
                    output_buffer.seek(0)
                    content = output_buffer.getvalue()
                put_file("output.xlsx", content, ">> 点击下载生成后的文件 <<")

            except KeyError as e:
                put_text(f"文件缺少必要列: {e}")
            except Exception as e:
                put_text(f"输入不规范，输出两行泪。\n\n{e}")


if __name__ == "__main__":
    Pcdn()
