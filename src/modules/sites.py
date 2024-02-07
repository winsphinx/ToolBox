#!/usr/bin/env python
# -*- coding: utf-8 -*-


import pandas as pd
from pywebio.input import file_upload
from pywebio.output import put_datatable, put_file, put_markdown


def format_file(file):
    d = file["content"].decode().replace('"', "").split("\n")
    n = len(d)
    data = []
    for m in range(1, n - 1):
        data.append({k: v for k, v in zip(d[0].split(","), d[m].split(","))})

    return data


def format_data(data):
    df = pd.DataFrame(data)  # data is list, convert to pd
    df = deal_data(df)
    header = df.columns
    li = df.values.tolist()
    n = len(li)
    data = []
    for m in range(n):
        data.append({k: v for k, v in zip(header, li[m])})

    return data


def deal_data(data):
    data = data.head(10)

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
            instance_id="sites",
        )

        put_markdown("### 转换后预览")
        new_data = format_data(data)
        put_datatable(
            new_data,
            instance_id="sites_v",
        )

        content = convert_to_csv(new_data)
        put_file(
            "result.csv",
            content.encode(),
            ">> 点击下载生成后的文件 <<",
        )


if __name__ == "__main__":
    Sites()
