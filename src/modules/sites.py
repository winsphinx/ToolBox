#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from io import StringIO

import pandas as pd
from pywebio.input import file_upload
from pywebio.output import put_datatable, put_file, put_markdown


def format_file(file):
    return pd.read_csv(StringIO(file["content"].decode("utf-8-sig")))


def format_data(data):
    df = pd.DataFrame(data)
    #    df = deal_data(df)
    string_df = df.to_json(force_ascii=False, orient="records")
    data = json.loads(string_df)

    return data


def deal_data(data):
    data = data.head(10)

    return data


def convert_to_csv(data):
    return data.to_csv(index=False)


class Sites:
    def __init__(self):
        put_markdown("# 基站稽核")

        file = file_upload(
            "上传文件",
            accept="text/csv",
            placeholder="上传一个 *.CSV 文件",
        )

        data = format_file(file)
        put_markdown("### 原始表预览")
        put_datatable(
            format_data(data),
            instance_id="sites_0",
        )

        put_markdown("### 转换后预览")
        new_data = deal_data(data)
        put_datatable(
            format_data(new_data),
            instance_id="sites_n",
        )

        content = convert_to_csv(new_data)
        put_file(
            "result.csv",
            content.encode("utf-8-sig"),
            ">> 点击下载生成后的文件 <<",
        )


if __name__ == "__main__":
    Sites()
