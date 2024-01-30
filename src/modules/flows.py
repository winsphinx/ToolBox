#!/usr/bin/env python
# -*- coding: utf-8 -*-


import ipaddress

import pandas as pd
from pywebio.output import put_button, put_file, put_html, put_loading, put_markdown, put_scope, use_scope
from pywebio.pin import pin, put_file_upload


def calculate_network(df):
    try:
        if not df["起始IP"].startswith("2408"):  # for ipv4
            for host in ipaddress.summarize_address_range(ipaddress.ip_address(df["起始IP"]), ipaddress.ip_address(df["终止IP"])):
                return host
        else:  # for ipv6
            return ipaddress.ip_network(df["起始IP"])
    except ValueError:
        pass


class Flows:
    def __init__(self):
        self.networks = None
        self.host = None

        put_markdown("# 省际流量汇总")

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
        file = pin["data_file"]
        df_net = pd.read_excel(file["content"])
        df_net = df_net[["工程名称", "带宽", "所属节点", "起始IP", "终止IP", "BSS号码", "安装地址"]]
        df_net["网络"] = df_net.apply(calculate_network, axis=1)
        err = df_net[df_net["网络"].isnull()]
        if err.empty:
            put_markdown("### 原始地址文件很完美，请上传要匹配的文件。")
        else:
            put_markdown("### 原始地址文件中有以下不规范地址格式，请处理后重新上传。")
            put_html(df_net[df_net["网络"].isnull()].to_html(border=0))
        self.networks = df_net

    @use_scope("output", clear=True)
    def match_file(self):
        with put_loading():
            file = pin["host_file"]
            df_host = pd.read_excel(file["content"])
            df_host = df_host.groupby(by=["本端IP"], as_index=False)["本端ip流入-流出差值均值流量bps"].sum()

            content = "主机地址,流量合计,网络地址,名称\n"
            for _, row in df_host.iterrows():
                for net in self.networks["网络"]:
                    ip = ipaddress.ip_address(row["本端IP"])
                    if ip in net:
                        content += (
                            row["本端IP"]
                            + ","
                            + str(row["本端ip流入-流出差值均值流量bps"])
                            + ","
                            + str(net)
                            + ","
                            + self.networks.loc[self.networks["网络"] == net, "工程名称"].values[0]
                            + "\n"
                        )
                        break
                else:
                    content += row["本端IP"] + "," + str(row["本端ip流入-流出差值均值流量bps"]) + ",,我是普通宽带\n"

        put_file(
            "export.txt",
            content.encode(),
            ">> 点击下载生成后的文件 <<",
        )


if __name__ == "__main__":
    Flows()
