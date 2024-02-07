#!/usr/bin/env python
# -*- coding: utf-8 -*-

from math import ceil
from random import choice

from pywebio.output import put_button, put_file, put_loading, put_markdown, put_scope, put_text, use_scope
from pywebio.pin import pin, put_input, put_textarea


class Sipcall:
    def __init__(self):
        put_markdown("# SIP 数字中继脚本生成器")
        put_input(
            "name",
            label="名称",
            placeholder="某某公司",
            help_text="中继组的名称，不要超过 32 字符。",
        )
        put_input(
            "IP",
            label="地址",
            placeholder="10.33.x.x",
            help_text="分配的 IP 地址。",
        )
        put_input(
            "nexthop",
            label="signal nexthop",
            placeholder="5xxx",
            help_text="绍兴从 5000 开始编号。",
        )
        put_input(
            "pool",
            label="pool ID",
            placeholder="5xxx",
            help_text="绍兴从 5000 开始编号。",
        )
        put_input(
            "routes",
            label="route analyser",
            placeholder="5xxx/5xxx",
            help_text="绍兴从 5000 开始编号。两个值，中间用 / 隔开。",
        )
        put_input(
            "cac",
            label="呼叫能力 cac perfile",
            placeholder="5xxx",
            help_text="绍兴从 5000 开始编号。",
        )
        put_input(
            "max",
            label="并发数",
            placeholder="100",
            help_text="按需要填。",
        )
        put_input(
            "mgcf",
            label="MGCF pool ID",
            placeholder="1xx",
            help_text="绍兴从 100 开始编号。",
        )
        put_input(
            "isbc",
            label="与MGCF对接的 ISBC 端口",
            placeholder="5xxx",
            help_text="绍兴从 5140-5159 编号。",
        )
        put_input(
            "adj",
            label="邻接局编号",
            placeholder="35xx",
            help_text="绍兴从 3500-3599 编号。",
        )
        put_input(
            "node",
            label="节点号",
            placeholder="6xx",
            help_text="绍兴从 650-699 开始编号。",
        )
        put_input(
            "brs",
            label="连接编号",
            placeholder="23xx/23xx",
            help_text="绍兴从 2300-2399 编号。两个值，中间用 / 隔开。",
        )
        put_input(
            "link",
            label="信令链路号",
            placeholder="23xx",
            help_text="绍兴从 2300-2399 编号。",
        )
        put_input(
            "tg",
            label="中继组号",
            placeholder="23xx",
            help_text="绍兴从 2300-2399 编号。",
        )
        put_input(
            "auth",
            label="用户鉴权选择子",
            placeholder="2xx",
            help_text="绍兴从 250-299 编号。",
        )
        put_textarea(
            "sub_numbers",
            label="引示号",
            placeholder="88888888\n77777777\n66666666\n96xxxx\n...",
            help_text="每行一个号码，回车分割。",
        )
        put_button(
            label="点击生成脚本",
            onclick=self.update,
        )
        put_markdown("----")
        put_scope("output")

    @use_scope("output", clear=True)
    def update(self):
        with put_loading():
            put_text("开始生成脚本...")
            name = pin["name"].strip()
            ip = pin["IP"].strip()
            pool = pin["pool"].strip()
            nexthop = pin["nexthop"].strip()
            ra1, ra2 = pin["routes"].strip().split("/")
            cac = pin["cac"].strip()
            max = int(pin["max"].strip())
            mgcf = pin["mgcf"].strip()
            isbc = pin["isbc"].strip()
            adj = pin["adj"].strip()
            node = pin["node"].strip()
            br1, br2 = pin["brs"].strip().split("/")
            link = pin["link"].strip()
            tg = pin["tg"].strip()
            rt = pin["tg"].strip()
            rts = pin["tg"].strip()
            chain = pin["tg"].strip()
            auth = pin["auth"].strip()
            sub_numbers = [s.strip() for s in pin["sub_numbers"].strip().split("\n")]

            content = "*" * 20 + "\n\t摘要\n" + "*" * 20 + "\n"
            content += f"名称：{name}\n"
            content += f"IP地址：{ip}\n"
            content += f"POOL：{pool}\n"
            content += f"NH：{nexthop}\n"
            content += f"RA：{ra1}, {ra2}\n"
            content += f"cac：{cac}\n"
            content += f"并发数：{max}\n"
            content += f"MGCF：{mgcf}\n"
            content += f"ISBC：{isbc}\n"
            content += f"ADJOFC：{adj}\n"
            content += f"NODE：{node}\n"
            content += f"链接：{br1}, {br2}\n"
            content += f"信令链路号：{link}\n"
            content += f"信令路由号：{adj}\n"
            content += f"信令路由集号：{adj}\n"
            content += f"中继组号：{tg}\n"
            content += f"路由号：{rt}\n"
            content += f"路由集号：{rts}\n"
            content += f"路由链号：{chain}\n"
            content += f"用户鉴权选择子：{auth}\n"
            content += f"号码：{sub_numbers}\n"

            content += "\n\n" + "*" * 20 + "\n\tSDC\n" + "*" * 20 + "\n"
            for n in sub_numbers:
                content += f'ADD USR:DN="{n}",LRN="116448{n}",USRTYPE=NGN,LOCZCIDX=5,AREAIDX=5;\n'

            content += "\n\n" + "*" * 20 + "\n\tISBC03\n" + "*" * 20 + "\n"
            content += "//增加下一跳地址\n"
            content += f'ADD NH BASIC:NHID={nexthop},DESC="{name}",IPADDRESS="{ip}";\n'
            content += f'ADD NH RADDR:NHID={nexthop},IPADDR="{ip}",PREFIX=32;\n'
            content += f'SET NH SUB:NHID={nexthop},SIPTR="ENABLE";\n'
            content += "//最大并发数配置\n"
            content += f'ADD CAC PROFILE:CACPROFILEID={cac},CPDESC="{name}并发数",UGCALLTIME=10,UGCALLNUM={ceil(max/100*15)},UGMAXCALLNUM={max};\n'
            content += f'ADD INST CACRULE:INSTID={cac},CACRULEID={cac},DESC="{name}";\n'
            content += f'ADD POLICY GROUP:PLGID={cac},FSTLISTID=1,DSCP="{name}";\n'
            content += f'ADD POLICY LIST:PLGID={cac},LISTID=1,DSCP="{name}";\n'
            content += f'ADD POLICY ITEM:PLGID={cac},LISTID=1,ITEMID=0,DSCP="{name}",SRVID={cac};\n'
            content += "//增加信令池配置\n"
            content += f"ADD POOLBASICCONFIG:SGID=15,POOLID={mgcf};\n"
            content += f"ADD POOLBASICCONFIG:SGID=15,POOLID={pool},INGRESSPOLICYID={nexthop};\n"
            content += f'ADD POLICY ATTACH:POLICYDIR="INGRESS",POLICYPOINT="SIGNAL_POOL",SGID=15,POOLID={pool},SERVICEID={cac},INSTANCETYPE="CAC",INSTANCEID={cac};\n'
            content += "//增加路由分析\n"
            content += f'ADD RA:ANALYSERID={ra1},FSTLISTID=1,DSCP="{name}-MGCF-SX";\n'
            content += f'ADD RA:ANALYSERID={ra2},FSTLISTID=1,DSCP="MGCF-{name}-SX";\n'
            content += f'ADD RAL:ANALYSERID={ra1},LISTID=1,DSCP="{name}-MGCF-SX";\n'
            content += f'ADD RAL:ANALYSERID={ra2},LISTID=1,DSCP="MGCF-{name}-SX";\n'
            content += f"ADD RAI:RAID={ra1},ALID=1,ITEMID=0,SGID=15,POOLID={mgcf};\n"
            content += f"ADD RAI:RAID={ra2},ALID=1,ITEMID=0,SGID=15,POOLID={pool};\n"
            content += "//增加到MGCF的信令池下一条基本配置。MGCF的下一跳固定为1和2，同一个 pool 下可以增加多个下一跳，可以设置主备方式或者负荷分担\n"
            content += f'ADD POOLNH BASIC:SGID=15,POOLID={mgcf},NHID=1,IGRROUT={ra2},EGRROUT=200,TRSTDOM="ENABLE";\n'
            content += f'ADD SIP NEXTHOP LINK:SGID=15,POOLID={mgcf},NHID=1,LINKID=1,LOCALIPADDR="10.108.209.174",LOCALPORT={isbc},REMOTEPORTTYPE="UDP",REMOTEPORT=5060;\n'
            content += f'ADD POOLNH BASIC:SGID=15,POOLID={mgcf},NHID=2,IGRROUT={ra2},EGRROUT=200,TRSTDOM="ENABLE",TRACKID=1;\n'
            content += f'ADD SIP NEXTHOP LINK:SGID=15,POOLID={mgcf},NHID=2,LINKID=1,LOCALIPADDR="10.108.209.174",LOCALPORT={isbc},REMOTEPORTTYPE="UDP",REMOTEPORT=5060;\n'
            content += f"ADD POOL MEDIA:SGID=15,POOLID={mgcf},MEDIA_ID=1,ML=21,MR=2103;\n"
            content += f"ADD POOL MEDIA:SGID=15,POOLID={mgcf},MEDIA_ID=2,ML=21,MR=2104;\n"
            content += f"ADD POOL MEDIA:SGID=15,POOLID={mgcf},MEDIA_ID=3,ML=22,MR=2203;\n"
            content += f"ADD POOL MEDIA:SGID=15,POOLID={mgcf},MEDIA_ID=4,ML=22,MR=2204;\n"
            content += f"SET POOLBASICCONFIG:SGID=15,POOLID={mgcf},NEXTHOPFAILOVERRULE=1;\n"
            content += f"ADD POOLNH BASIC:SGID=15,POOLID={pool},NHID={nexthop},IGRROUT={ra1},INPL={nexthop};\n"
            content += f'ADD SIP NEXTHOP LINK:SGID=15,POOLID={pool},NHID={nexthop},LINKID=1,LOCALIPADDR="10.0.1.139",LOCALPORT=5060,REMOTEPORTTYPE="UDP",REMOTEPORT=5060;\n'
            content += f"ADD POOL MEDIA:SGID=15,POOLID={pool},MEDIA_ID=1,ML=21,MR=2101;\n"
            content += f"ADD POOL MEDIA:SGID=15,POOLID={pool},MEDIA_ID=2,ML=21,MR=2102;\n"
            content += f"ADD POOL MEDIA:SGID=15,POOLID={pool},MEDIA_ID=3,ML=22,MR=2201;\n"
            content += f"ADD POOL MEDIA:SGID=15,POOLID={pool},MEDIA_ID=4,ML=22,MR=2202;\n"
            content += f"SET POOLBASICCONFIG:SGID=15,POOLID={pool},NEXTHOPFAILOVERRULE=1;\n"
            content += f"SHOW SIGNALPOOL STATUS:SGID=15,POOLID={pool};\n"
            content += "SAVE CFGFILE\n"

            content += "\n\n" + "*" * 20 + "\n\tMGCF\n" + "*" * 20 + "\n"
            content += "//邻接局配置\n"
            content += f'ADD ADJOFC:ID={adj},NAME="{name}-绍兴",MODULE=1,NET=1,OFCTYPE="PSTN",SPCFMT="HEX",SPCTYPE="24",'
            content += f'DPC="{adj}",RC="575",SPTYPE="SEP",SSF="NATIONAL",PRTCTYPE="CHINA";\n'
            content += f"SET OFCAPP:ID={adj},DOMAININDEX=1;\n"
            content += "//拓扑配置\n"
            content += f'ADD TOPOLY:NODEID={node},OFCID={adj},DEVTYP="OTHSWT",PROTYP="SIP",CODEC=40,DTMFTSM="IN",IPNET=2,NAME="{name}-绍兴";\n'
            content += "//SIP局配置\n"
            ATTR = '"SIP 100REL"&"NOCHARGE"&"DTMF4733"&"NOSENDSDP"&"200SNDRCV"&"SINGLEFRAME"&"FCPL"&"GENERICNUM"&"URI-STARSHARP"&"SIPCALL"'
            content += f'ADD SIPOFC:OFC={adj},URLT="TEL",ATTR={ATTR},DTMFT="IN",INCODECID=0,OUTCODECID=40;\n'
            content += "//邻接主机配置\n"
            content += f'ADD ADJHOST:ID={adj},HOSTNAME="ibac{adj}.zj.ims.chinaunicom.cn",REALM="zj.ims.chinaunicom.cn";\n'
            content += "//UDP承载配置\n"
            content += f'ADD UDPBR:ID={br1},NAME="{name}-绍兴_1",ADDRTYPE="IPV4",IPMODE="REMOTE_VALID",IPV4ADDR="10.108.209.174",PORT=0,MODULE=0,ADJHOST={adj};\n'
            content += f'ADD UDPBR:ID={br2},NAME="{name}-绍兴_2",ADDRTYPE="IPV4",IPMODE="REMOTE_VALID",IPV4ADDR="10.108.209.174",PORT={isbc},MODULE=0,ADJHOST={adj};\n'
            content += "//按链路分发\n"
            conn = choice(["3001&1&2&3", "4&5&6&7", "8&9&10&11", "12&13&14&15"])
            content += f'ADD ULDPLC:PROTOCOL="UDP",DSTCONN={br2},UPLC="LOADSHARE",UDPCONN={conn},NAME="{name}-绍兴";\n'
            content += "//SIP信令链路配置\n"
            content += f'ADD SIPLNK:ID={link},CONNID={br2},PROTOCOL="UDP",NAME="{name}-绍兴";\n'
            content += "//SIP信令路由配置\n"
            content += f'ADD SIPRT:ID={adj},NAME="{name}-绍兴",SPLC="RR",LNK={link};\n'
            content += "//SIP信令路由集配置\n"
            content += f'ADD SIPRTS:ID={adj},NAME="{name}-绍兴",RTPLC="AS",SIPRT={adj}-0;\n'
            content += "//URI分析配置\n"
            METHOD = '"INVITE"&"PRACK"&"ACK"&"UPDATE"&"CANCEL"&"BYE"&"OPTIONS"&"INFO"&"REGISTER"&"SUBSCRIBE"&"REFER"&"NOTIFY"&"MESSAGE"&"PUBLISH"'
            content += f'ADD URI:RTSEL=1,URI="ibac{adj}.zj.ims.chinaunicom.cn",METHOD={METHOD},SIPRTS={adj};\n'
            content += "//中继组配置\n"
            content += f'ADD TG RTP:TG={tg},OFC={adj},MODULE=0,LINE="SIP",NAME="{name}-绍兴",KIND="BIDIR",TPDAS=52,ROAMDAS=0,SIPROUTESET={adj};\n'
            content += f'SET TG:TG={tg},IOI="zj.ims.chinaunicom.cn";\n'
            content += "//设置对等中继标签\n"
            content += f'SET TGFLG:TG={tg},FTGADD="CALBLOCK"&"REJCAL"&"REJFWDCAL"&"CHKZERO"&"PBXACCESS",FTGDEL="CHARGE",DTGDEL="LOCPFX",CTGADD="SETUPACK"&"ANNOUNCEMENT";\n'
            content += "//路由配置\n"
            content += f'ADD RT:RT={rt},TG={tg},NAME="{name}-绍兴";\n'
            content += "//路由组配置\n"
            content += f'ADD RTS:RTS={rts},NAME="{name}-绍兴",RTINFO=1-{tg}-0-0-255,RTFLG="PEAR",CTLFLG="PRIO";\n'
            content += "//路由链配置\n"
            content += f'ADD CHAIN:CHAIN={chain},RTS1={rts},NAME="{name}-绍兴";\n'
            content += "//用户鉴权选择子配置\n"
            content += f'ADD AUTHDAS:DAS={auth},DESNAME="{name}-绍兴";\n'
            content += "//中继黑白名单鉴权配置\n"
            content += f"ADD TGAUTH:TG={tg},AUTHDAS={auth};\n"
            content += f'ADD SIPCOMBNUMTRANS:MSGTYPE="RCINVITE",NUMTYPE="FRF",ORGTYPE="TG",CALLORG={tg},TRFAS=507;\n'
            content += "//用户鉴权号码配置\n"
            for i in range(10):
                content += f'ADD AUTH:DAS={auth},DIGIT="{i}",CALLRITID=999,NAME="{name}-绍兴";\n'
            for n in sub_numbers:
                content += f'ADD AUTH:DAS={auth},DIGIT="{n}",CALLRITID=19,VALIDLEN={len(n)},NAME="{name}-绍兴";\n'
                content += f'ADD AUTH:DAS={auth},DIGIT="0086575{n}",CALLRITID=19,VALIDLEN={len(n)+7},NAME="{name}-绍兴";\n'
            content += "//落地数据配置\n"
            OPT = '"NCEL"&"TCUG"&"HDRTT"&"BODYTT"&"SEND_CCL"'
            for n in sub_numbers:
                content += f'ADD TPDNAL:ENTR=25,DIGIT=0086575{n},CAT="LOL",RST1={chain},MINLEN=15,MAXLEN=15,TPDDI=3,ENOPT={OPT},CALLINGOPTDAS=502;\n'
                content += f'ADD TPDNAL:ENTR=115,DIGIT=0086575{n},CAT="LOL",RST1={chain},MINLEN=15,MAXLEN=15,TPDDI=3,ENOPT={OPT},CALLINGOPTDAS=502;\n'
                content += f'ADD TPDNAL:ENTR=215,DIGIT=0086575{n},CAT="LOL",RST1={chain},MINLEN=15,MAXLEN=15,TPDDI=3,ENOPT={OPT},CALLINGOPTDAS=502;\n'
                content += f'ADD TPDNAL:ENTR=315,DIGIT=0086575{n},CAT="LOL",RST1={chain},MINLEN=15,MAXLEN=15,TPDDI=3,ENOPT={OPT},CALLINGOPTDAS=502;\n'
                content += f'ADD TPDNAL:ENTR=415,DIGIT=0086575{n},CAT="LOL",RST1={chain},MINLEN=15,MAXLEN=15,TPDDI=3,ENOPT={OPT},CALLINGOPTDAS=502;\n'
                content += f'ADD TPDNAL:ENTR=515,DIGIT=0086575{n},CAT="LOL",RST1={chain},MINLEN=15,MAXLEN=15,TPDDI=3,ENOPT={OPT},CALLINGOPTDAS=502;\n'
                content += f'ADD TPDNAL:ENTR=615,DIGIT=0086575{n},CAT="LOL",RST1={chain},MINLEN=15,MAXLEN=15,TPDDI=3,ENOPT={OPT},CALLINGOPTDAS=502;\n'
                content += f'ADD TPDNAL:ENTR=715,DIGIT=0086575{n},CAT="LOL",RST1={chain},MINLEN=15,MAXLEN=15,TPDDI=3,ENOPT={OPT},CALLINGOPTDAS=502;\n'
                content += f'ADD TPDNAL:ENTR=815,DIGIT=0086575{n},CAT="LOL",RST1={chain},MINLEN=15,MAXLEN=15,TPDDI=3,ENOPT={OPT},CALLINGOPTDAS=502;\n'
                content += f'ADD TPDNAL:ENTR=915,DIGIT=0086575{n},CAT="LOL",RST1={chain},MINLEN=15,MAXLEN=15,TPDDI=3,ENOPT={OPT},CALLINGOPTDAS=502;\n'
                content += f'ADD TPDNAL:ENTR=1015,DIGIT=0086575{n},CAT="LOL",RST1={chain},MINLEN=15,MAXLEN=15,TPDDI=3,ENOPT={OPT},CALLINGOPTDAS=502;\n'
                content += f'ADD TPDNAL:ENTR=1115,DIGIT=0086575{n},CAT="LOL",RST1={chain},MINLEN=15,MAXLEN=15,TPDDI=3,ENOPT={OPT},CALLINGOPTDAS=502;\n'
            for n in sub_numbers:
                content += "//平时用不上，万一要删除时用这段\n"
                content += f'//DEL DNAL:ENTR=25,NANNAT="ALL",DIGIT="0086575{n}";\n'
                content += f'//DEL DNAL:ENTR=115,NANNAT="ALL",DIGIT="0086575{n}";\n'
                content += f'//DEL DNAL:ENTR=215,NANNAT="ALL",DIGIT="0086575{n}";\n'
                content += f'//DEL DNAL:ENTR=315,NANNAT="ALL",DIGIT="0086575{n}";\n'
                content += f'//DEL DNAL:ENTR=415,NANNAT="ALL",DIGIT="0086575{n}";\n'
                content += f'//DEL DNAL:ENTR=515,NANNAT="ALL",DIGIT="0086575{n}";\n'
                content += f'//DEL DNAL:ENTR=615,NANNAT="ALL",DIGIT="0086575{n}";\n'
                content += f'//DEL DNAL:ENTR=715,NANNAT="ALL",DIGIT="0086575{n}";\n'
                content += f'//DEL DNAL:ENTR=815,NANNAT="ALL",DIGIT="0086575{n}";\n'
                content += f'//DEL DNAL:ENTR=915,NANNAT="ALL",DIGIT="0086575{n}";\n'
                content += f'//DEL DNAL:ENTR=1015,NANNAT="ALL",DIGIT="0086575{n}";\n'
                content += f'//DEL DNAL:ENTR=1115,NANNAT="ALL",DIGIT="0086575{n}";\n'

            content += '\n//重要提醒：两个 MGCF 都要加一遍，勿忘传表（SYN:DATABASE="ALL";）\n'

        put_text(content)
        put_file(f"{name}.txt", content.encode(), ">> 点击下载脚本 <<")


if __name__ == "__main__":
    Sipcall()
