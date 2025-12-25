#!/usr/bin/env python
# -*- coding: utf-8 -*-

from io import BytesIO

import pandas as pd
from pywebio.output import put_button, put_file, put_loading, put_markdown, put_scope, put_text, use_scope
from pywebio.pin import pin, put_file_upload

from utils import display_random_image

dic1 = {
    "浙江": "浙江省",
    "北京": "北京市",
    "天津": "天津市",
    "上海": "上海市",
    "重庆": "重庆市",
    "黑龙江": "黑龙江省",
    "吉林": "吉林省",
    "辽宁": "辽宁省",
    "河北": "河北省",
    "山西": "山西省",
    "江苏": "江苏省",
    "安徽": "安徽省",
    "福建": "福建省",
    "江西": "江西省",
    "山东": "山东省",
    "河南": "河南省",
    "湖北": "湖北省",
    "湖南": "湖南省",
    "广东": "广东省",
    "海南": "海南省",
    "四川": "四川省",
    "贵州": "贵州省",
    "云南": "云南省",
    "陕西": "陕西省",
    "甘肃": "甘肃省",
    "青海": "青海省",
    "内蒙古": "内蒙古自治区",
    "广西": "广西壮族自治区",
    "西藏": "西藏自治区",
    "宁夏": "宁夏回族自治区",
    "新疆": "新疆维吾尔自治区",
    "香港": "香港特别行政区",
    "澳门": "澳门特别行政区",
}
dic2 = {
    "绍兴": "绍兴市",
    "杭州": "杭州市",
    "嘉兴": "嘉兴市",
    "金华": "金华市",
    "丽水": "丽水市",
    "宁波": "宁波市",
    "衢州": "衢州市",
    "台州": "台州市",
    "温州": "温州市",
    "舟山": "舟山市",
    "湖州": "湖州市",
}


class Roamusers:
    def __init__(self):
        display_random_image()

        self.networks = None
        self.host = None

        put_markdown("# 漫游用户统计")

        put_file_upload(
            name="rsj_file",
            label="上传人社局文件",
            accept=".xlsx",
            placeholder="excel 格式的文件",
        )
        put_file_upload(
            name="sgs_file",
            label="上传省公司文件",
            accept=".csv",
            placeholder="csv 格式的文件",
        )
        put_button(
            label="开始匹配文件",
            onclick=self.match_file,
        )

        put_markdown("----")
        put_scope("output")

    @use_scope("output", clear=True)
    def match_file(self):
        try:
            with put_loading():
                put_text("开始吭哧吭哧生成结果......")

                file1 = BytesIO(pin["rsj_file"]["content"])
                rsj = pd.read_excel(file1)

                file2 = BytesIO(pin["sgs_file"]["content"])
                sgs = pd.read_csv(file2, encoding="gb18030")
                sgs["PROV_ID_NAME"] = sgs["PROV_ID_NAME"].replace(dic1)
                sgs["AREA_DESC"] = sgs["AREA_DESC"].replace(dic2).where(sgs["AREA_DESC"].isin(dic2.keys()), "")

                res = pd.merge(rsj, sgs, right_on="svc_num", left_on="手机号码", how="left")
                res = res.drop(columns=["手机号码", "运营商", "svc_num"])
                res = res.rename(columns={"PROV_ID_NAME": "目前省份", "AREA_DESC": "目前地市"})

                output_buffer = BytesIO()
                res.to_excel(output_buffer, sheet_name="Sheet1", index=False)
                content = output_buffer.getvalue()
                put_file("output.xlsx", content, ">> 点击下载生成后的文件 <<")

        except Exception as e:
            put_text(f"输入不规范，输出两行泪。\n\n{e}")


if __name__ == "__main__":
    Roamusers()
