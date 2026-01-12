#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import time
from io import BytesIO

import pandas as pd
from pywebio.input import file_upload
from pywebio.output import put_datatable, put_file, put_loading, put_markdown

from utils import display_random_pet


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
    df_5G = pd.merge(df_5GAAU, df_5Gsites, left_on="小区名", right_on="Cell_Name", how="left").filter(["频段", "铁塔站址编号及产权"]).rename(columns={"铁塔站址编号及产权": "站址编码"})
    df_4G = pd.merge(df_4GRRU, df_4Gsites, left_on="关联4G小区名称", right_on="小区网管名称", how="left").filter(["频段", "铁塔站址编号"]).rename(columns={"铁塔站址编号": "站址编码"})

    # 合并基本信息表
    result = pd.concat([df_5G, df_4G], ignore_index=True)

    # 按频段分类、求和
    dummy_freq = pd.get_dummies(result["频段"], prefix="频段")
    result = pd.concat([result, dummy_freq], axis=1).drop("频段", axis=1)
    result = result.groupby("站址编码").sum().reset_index()

    # 整理费用表
    df_fee["站址编码"] = df_fee["站址编码"].apply(lambda x: "T" + str(x))
    df_fee["成本合计"] = df_fee["小计"].str.replace(",", "").astype(float)

    # 对费用表的金额分类求和，合并到结果表
    df_fee = df_fee.groupby("站址编码")["成本合计"].sum().reset_index()
    result = pd.merge(result, df_fee, left_on="站址编码", right_on="站址编码", how="left")

    # 整理资源表
    df_db["站址编码"] = df_db["站址编码"].apply(lambda x: "T" + str(x))
    df_db["产品单元总数"] = df_db["产品单元数1"] + df_db["产品单元数2"] + df_db["产品单元数3"]

    # 对资源表的单元数分类求和，合并到结果表
    df_db_units = df_db.groupby("站址编码")["产品单元总数"].sum().reset_index()
    df_db_units = pd.merge(df_db_units, df_db[["站址编码", "铁塔种类"]], left_on="站址编码", right_on="站址编码", how="left")

    result = pd.merge(result, df_db_units, left_on="站址编码", right_on="站址编码", how="left")

    # 对资源表的客户数分类平均，合并到结果表
    df_db_users = df_db.groupby("站址编码")["维护费共享客户数"].mean().reset_index()
    result = pd.merge(result, df_db_users, left_on="站址编码", right_on="站址编码", how="left")

    # 在结果表增加一列：对本行内非零频段计数
    result["非零频段数"] = result.apply(lambda row: (row.iloc[1:7] != 0).sum(), axis=1)

    # 在结果表增加一列：
    # 1. 铁塔种类为普通地面塔时:
    # 	 非零频段数为2时，产品单元总数大于1.0时输出结果false，其余为ture；
    # 	 非零频段数为3时，产品单元总数大于1.3时输出结果false，其余为ture；
    # 	 非零频段数为4时，产品单元总数大于1.6时输出结果false，其余为ture；
    # 	 非零频段数为5时，产品单元总数大于1.9时输出结果false，其余为ture；
    # 2. 铁塔种类为剩余四种时:
    # 	 非零频段数为2时，产品单元总数大于1.3时输出结果false，其余为ture；
    # 	 非零频段数为3时，产品单元总数大于1.6时输出结果false，其余为ture；
    # 	 非零频段数为4时，产品单元总数大于1.9时输出结果false，其余为ture；

    # 实现公式计算逻辑
    def calculate_result(row):
        tower_type = row["铁塔种类"]
        freq_count = row["非零频段数"]
        unit_total = row["产品单元总数"]

        if tower_type == "普通地面塔":
            if freq_count == 2:
                return not (unit_total > 1.0)
            elif freq_count == 3:
                return not (unit_total > 1.3)
            elif freq_count == 4:
                return not (unit_total > 1.6)
            elif freq_count == 5:
                return not (unit_total > 1.9)
            else:
                return True
        else:  # 剩余四种铁塔种类
            if freq_count == 2:
                return not (unit_total > 1.3)
            elif freq_count == 3:
                return not (unit_total > 1.6)
            elif freq_count == 4:
                return not (unit_total > 1.9)
            else:
                return True

    # 在结果表增加公式计算列
    result["计算结果"] = result.apply(calculate_result, axis=1)

    return result.fillna(0)


class Sites:
    def __init__(self):
        display_random_pet()

        put_markdown("# 基站稽核")

        file = file_upload(
            "上传文件",
            accept=".xlsx",
            placeholder="在这里上传一个表格。",
            help_text="必须包括 6 个子表，其表名为：5G AAU、4G RRU、5G物理基站表、4G物理基站表、塔租费用表、塔租数据库。",
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
