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
            df_net = df_net[["工程名称", "带宽", "所属节点", "起始IPv4", "终止IPv4", "起始IPv6", "终止IPv6", "业务号码", "装机地址"]]
            df_net["起始IP"] = df_net["起始IPv4"].fillna(df_net["起始IPv6"])
            df_net["终止IP"] = df_net["终止IPv4"].fillna(df_net["终止IPv6"])
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
            df_all = pd.read_excel(file, sheet_name=None)
            sum_sheet = checkbox("选择要汇总的子表（对于城域网选1+3，对于IDC选2+4）", [k for k in df_all.keys()])
            df_host = pd.concat([df_all[x] for x in sum_sheet])

            cols = df_host.columns.to_list()
            group_key = radio("选择作为分组依据的列名（单选）", cols, value=cols[2], required=True)
            cols.remove(group_key)
            sort_keys = radio("选择要排序汇总的列名（单选）", cols, value=cols[-2], required=True)
            df_host = df_host.groupby(by=[group_key]).sum().sort_values(by=[sort_keys]).reset_index().head(100)

            content = f"{group_key},{sort_keys},所属网络,名称,业务号码,装机地址\n"
            for _, row in df_host.iterrows():
                for net in self.networks["网络"]:
                    ip = ipaddress.ip_address(row[group_key])
                    if ip in net:
                        res = self.networks.loc[self.networks["网络"] == net, ["工程名称", "业务号码", "装机地址"]].values[0]
                        content += f"{row[group_key]},{row[sort_keys]},{str(net)},{res[0]},{str(res[1])},{res[2]}\n"
                        break
                else:
                    content += f"{row[group_key]},{row[sort_keys]},,,,\n"

        put_file(
            "导出结果.csv",
            content.encode("utf-8-sig"),
            ">> 点击下载生成后的文件 <<",
        )


if __name__ == "__main__":
    Flows()
