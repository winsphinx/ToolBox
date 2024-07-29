#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import time
from io import BytesIO

import pandas as pd
from pywebio.input import file_upload
from pywebio.output import put_datatable, put_file, put_loading, put_markdown


def read_file(file):
    return pd.read_excel(BytesIO(file["content"]), sheet_name=None)


def format_data(data):
    return json.loads(data.to_json(force_ascii=False, orient="records"))


def convert_to_csv(data):
    return data.to_csv(index=False)


def deal_data(data):
    # 按sheet读取
    df_5GAAU = data["5G AAU"].fillna(0)
    df_4GRRU = data["4G RRU"].fillna(0)
    df_5Gsites = data["5G物理基站表"].fillna(0)
    df_4Gsites = data["4G物理基站表"].fillna(0)
    df_fee = data["塔租费用表"].fillna(0)
    df_db = data["塔租数据库"].fillna(0)

    # 预处理：如果5G 4G相同ID，删除4G表中对应共有的行
    common_rows_index = df_4GRRU[df_4GRRU["设备序列号"].isin(df_5GAAU["设备序列号"])].index
    df_4GRRU = df_4GRRU.drop(common_rows_index)

    # 匹配基本信息表
    df_5G = pd.merge(df_5GAAU, df_5Gsites, left_on="小区名", right_on="Cell_Name", how="left").filter(["频段", "铁塔站址编号及产权"]).rename(columns={"频段": "Freq", "铁塔站址编号及产权": "Code"})
    df_4G = pd.merge(df_4GRRU, df_4Gsites, left_on="关联4G小区名称", right_on="小区网管名称", how="left").filter(["频段", "铁塔站址编号"]).rename(columns={"频段": "Freq", "铁塔站址编号": "Code"})

    # 合并基本信息表
    result = pd.concat([df_5G, df_4G], ignore_index=True)

    # 按频段分类、求和
    dummy_freq = pd.get_dummies(result["Freq"], prefix="Freq")
    result = pd.concat([result, dummy_freq], axis=1).drop("Freq", axis=1)
    result = result.groupby("Code").sum().reset_index()

    # 整理费用表
    df_fee["站址编码"] = df_fee["站址编码"].apply(lambda x: "T" + str(x))
    df_fee["Money"] = df_fee["小计"].str.replace(",", "").astype(float)

    # 对费用表的金额分类求和，合并到结果表
    df_fee = df_fee.groupby("站址编码")["Money"].sum().reset_index()
    result = pd.merge(result, df_fee, left_on="Code", right_on="站址编码", how="left").drop("站址编码", axis=1)

    # 整理资源表
    df_db["站址编码"] = df_db["站址编码"].apply(lambda x: "T" + str(x))
    df_db["Units"] = df_db["产品单元数1"] + df_db["产品单元数2"] + df_db["产品单元数3"]

    # 对资源表的单元数分类求和，合并到结果表
    df_db_units = df_db.groupby("站址编码")["Units"].sum().reset_index()
    result = pd.merge(result, df_db_units, left_on="Code", right_on="站址编码", how="left").drop("站址编码", axis=1)

    # 对资源表的客户数分类平均，合并到结果表
    df_db_users = df_db.groupby("站址编码")["维护费共享客户数"].mean().reset_index()
    result = pd.merge(result, df_db_users, left_on="Code", right_on="站址编码", how="left").drop("站址编码", axis=1).rename(columns={"维护费共享客户数": "Users"})

    return result.fillna(0)


class Sites:
    def __init__(self):
        put_markdown("# 基站稽核")

        file = file_upload(
            "上传文件",
            accept=".xlsx",
            placeholder="在这里上传一个表格。",
            help_text="必须包括 6 个子表：5G AAU、4G RRU、5G物理基站表、4G物理基站表、塔租费用表、塔租数据库。"
        )

        with put_loading():
            put_markdown("### 开始处理，请稍候...")
            data = read_file(file)
            data = deal_data(data)
            content = convert_to_csv(data)

        put_markdown("### 处理后的数据预览")
        put_datatable(
            format_data(data),
            instance_id="sites",
        )

        put_file(
            f"{time.strftime('%Y-%m-%d', time.localtime(time.time()))}.csv",
            content.encode("utf-8-sig"),
            ">> 点击下载生成后的文件 <<",
        )


if __name__ == "__main__":
    Sites()
