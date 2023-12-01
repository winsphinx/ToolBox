#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import pandas as pd
import time
import urllib.request

from pywebio.output import put_button, put_file, put_markdown, put_scope, put_text, use_scope, put_datatable, toast
from pywebio.pin import pin, put_textarea
from pywebio.input import file_upload


def format_file(file):
    d = file["content"].decode().replace('"', "").split("\n")
    n = len(d)
    data = []
    for m in range(1, n - 1):
        data.append({k: v for k, v in zip(d[0].split(","), d[m].split(","))})

    return data


def deal_data(data):
    df = pd.DataFrame(data)  # data is list, to pd
    df = df.head(100)
    head = df.columns
    l = df.values.tolist()
    n = len(l)
    data = []
    for m in range(n):
        data.append({k: v for k, v in zip(head, l[m])})

    return data


def convert_to_csv(data):
    content = ",".join(data[0].keys())
    for i in range(len(data)):
        content += ",".join(data[i].values())

    return content


class Sites:
    def __init__(self):
        put_markdown("# 基站稽核")

        f = file_upload(
            "上传文件",
            accept="text/csv",
            placeholder="上传一个 *.CSV 文件",
        )

        data = format_file(f)
        put_markdown("### 原始表预览")
        put_datatable(
            data,
            #            actions=[
            #                ("Edit Email", lambda row_id: datatable_update("user", input("Email"), row_id, "email")),
            #                ("Insert a Row", lambda row_id: datatable_insert("user", data[0], row_id)),
            #                None,  # separator
            #                ("Delete", lambda row_id: datatable_remove("user", row_id)),
            #            ],
            #            onselect=lambda row_id: toast(f"Selected row: {row_id}"),
            instance_id="sites",
        )

        put_markdown("### 转换后预览")
        new_data = deal_data(data)
        put_datatable(
            new_data,
            #            actions=[
            #                ("Edit Email", lambda row_id: datatable_update("user", input("Email"), row_id, "email")),
            #                ("Insert a Row", lambda row_id: datatable_insert("user", data[0], row_id)),
            #                None,  # separator
            #                ("Delete", lambda row_id: datatable_remove("user", row_id)),
            #            ],
            #            onselect=lambda row_id: toast(f"Selected row: {row_id}"),
            instance_id="sites_v",
        )
        #        put_scope("output")

        content = convert_to_csv(new_data)
        put_file("result.csv", content.encode(), ">> 点击下载生成后的文件 <<")


if __name__ == "__main__":
    Sites()
