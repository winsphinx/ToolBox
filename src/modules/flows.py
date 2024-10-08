#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ipaddress
from io import BytesIO

import pandas as pd
from pywebio.input import checkbox, radio
from pywebio.output import put_button, put_file, put_html, put_loading, put_markdown, put_scope, use_scope
from pywebio.pin import pin, put_file_upload


def calculate_network(df):
    try:
        if df["起始IP"].startswith("2408"):  # for ipv6
            return ipaddress.ip_network(df["起始IP"])
        else:  # for ipv4
            for host in ipaddress.summarize_address_range(ipaddress.ip_address(df["起始IP"]), ipaddress.ip_address(df["终止IP"])):
                return host
    except ValueError:
        pass


class Flows:
    def __init__(self):
        self.networks = None
        self.host = None

        put_markdown("# 省际流量分析")

        put_file_upload(
            name="data_file",
            label="上传地址清单",
            accept=".xlsx",
            placeholder="上传 IP 地址数据库文件",
        )
        put_button(
            label="检查文件正确性",
            onclick=self.check_file,
        )

        put_file_upload(
            name="host_file",
            label="上传主机清单",
            accept=".xlsx",
            placeholder="上传要匹配的主机清单文件",
        )
        put_button(
            label="开始匹配文件",
            onclick=self.match_file,
        )

        put_markdown("----")
        put_scope("output")

    @use_scope("output", clear=True)
    def check_file(self):
        with put_loading():
            file = BytesIO(pin["data_file"]["content"])
            df_net = pd.read_excel(file)
            df_net = df_net[["工程名称", "带宽", "所属节点", "起始IP", "终止IP", "BSS号码", "安装地址"]]
            df_net["网络"] = df_net.apply(calculate_network, axis=1)

        err = df_net[df_net["网络"].isnull()]
        if err.empty:
            put_markdown("### 原始地址文件很完美，请上传要匹配的文件。")
        else:
            put_markdown("### 原始地址文件中有以下不规范地址格式，请处理后重新上传。")
            put_markdown("不要带有括号，也不要用逗号、破折号带多个地址。")
            put_html(df_net[df_net["网络"].isnull()].to_html(border=0))
        self.networks = df_net

    @use_scope("output", clear=True)
    def match_file(self):
        with put_loading():
            file = BytesIO(pin["host_file"]["content"])
            df_host = pd.read_excel(file)
            cols = df_host.columns.to_list()

            group_key = radio("选择作为分组依据的列名（单选）", cols, value=cols[2], required=True)
            cols.remove(group_key)
            sum_keys = checkbox("选择要求和的列名（可多选）", cols)
            df_host = df_host.groupby(by=[group_key]).agg({key: "sum" for key in sum_keys}).reset_index()

            content = f"{group_key},{','.join(sum_keys)},所属网络,工程名称,BSS号码\n"
            for _, row in df_host.iterrows():
                selected_row = ",".join([str(row[key]) for key in sum_keys if key in row])
                for net in self.networks["网络"]:
                    ip = ipaddress.ip_address(row[group_key])
                    if ip in net:
                        res = self.networks.loc[self.networks["网络"] == net, ["工程名称", "BSS号码"]].values[0]
                        content += f"{row[group_key]},{selected_row},{str(net)},{res[0]},{str(res[1])}\n"
                        break
                else:
                    content += f"{row[group_key]},{selected_row},,我不是专线,\n"

        put_file(
            "导出结果.csv",
            content.encode("utf-8-sig"),
            ">> 点击下载生成后的文件 <<",
        )


if __name__ == "__main__":
    Flows()
