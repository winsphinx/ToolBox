#!/usr/bin/env python
from math import ceil
from random import choice

from pywebio.output import put_button, put_file, put_loading, put_markdown, put_scope, put_text, use_scope
from pywebio.pin import pin, put_input, put_radio, put_textarea

from utils import display_random_pet

ISBC_CONFIGS = {
    "ISBC-3": {"isbc_ip": "10.0.1.139", "mgcf_ip": "10.108.209.174"},
    "ISBC-4": {"isbc_ip": "10.0.1.144", "mgcf_ip": "10.108.209.179"},
}

MODE_CONFIGS = {
    "对等方式": {"tpdas": 52, "callritid": 19},
    "签约方式": {"tpdas": 250, "callritid": 200},
}

TPDNAL_ENTR_RANGE = [25, 115, 215, 315, 415, 515, 615, 715, 815, 915, 1015, 1115]

AUTH_DIGITS = "0123456789"

SIP_ATTR = '"SIP 100REL"&"NOCHARGE"&"DTMF4733"&"NOSENDSDP"&"200SNDRCV"&"SINGLEFRAME"&"FCPL"&"GENERICNUM"&"URI-STARSHARP"&"SIPCALL"'
URI_METHOD = '"INVITE"&"PRACK"&"ACK"&"UPDATE"&"CANCEL"&"BYE"&"OPTIONS"&"INFO"&"REGISTER"&"SUBSCRIBE"&"REFER"&"NOTIFY"&"MESSAGE"&"PUBLISH"'
TPDNAL_OPT = '"NCEL"&"TCUG"&"HDRTT"&"BODYTT"&"SEND_CCL"'
CTG_FTG_ADD = 'CALBLOCK"&"REJCAL"&"REJFWDCAL"&"CHKZERO"&"PBXACCESS'
CTG_FTG_DEL = "CHARGE"
CTG_DTG_DEL = "LOCPFX"
CTG_CTG_ADD = 'SETUPACK"&"ANNOUNCEMENT'


def build_summary(mode, name, ip, pool, nexthop, ra1, ra2, cac, max, mgcf, isbc, adj, node, br1, br2, link, tg, auth, sub_numbers):
    lines = [
        f"名称：{name}",
        f"组网模式：{mode}",
        f"IP地址：{ip}",
        f"POOL：{pool}",
        f"NH：{nexthop}",
        f"RA：{ra1}, {ra2}",
        f"cac：{cac}",
        f"并发数：{max}",
        f"MGCF：{mgcf}",
        f"ISBC：{isbc}",
        f"ADJOFC：{adj}",
        f"NODE：{node}",
        f"链接：{br1}, {br2}",
        f"信令链路号：{link}",
        f"信令路由号：{adj}",
        f"信令路由集号：{adj}",
        f"中继组号：{tg}",
        f"路由号：{tg}",
        f"路由集号：{tg}",
        f"路由链号：{tg}",
        f"用户鉴权选择子：{auth}",
        f"号码：{sub_numbers}",
    ]
    return "\n".join(lines)


def build_hss(sub_numbers):
    lines = []
    for n in sub_numbers:
        lines.extend(
            [
                f"ADD NEWPVI:PVITYPE=0,PVI=+86575{n}@zj.ims.chinaunicom.cn,IREGFLAG=1,IDENTITYTYPE=0,PECFN=ccf01.zj.ims.chinaunicom.cn,SECFN=ccf02.zj.ims.chinaunicom.cn,PCCFN=ccf01.zj.ims.chinaunicom.cn,SCCFN=ccf02.zj.ims.chinaunicom.cn,SecVer=30,UserName=+86575{n}@zj.ims.chinaunicom.cn,PassWord=123456,Realm=zj.ims.chinaunicom.cn,ACCTypeList=*,ACCInfoList=*,ACCValueList=*;",
                f"ADD NEWPUI:IDENTITYTYPE=0,PUI=sip:+86575{n}@zj.ims.chinaunicom.cn,BARFLAG=0,REGAUTHFG=1,ROAMSCHEMEID=1,SPID=5,SPDesc=绍兴SP,PVIList=+86575{n}@zj.ims.chinaunicom.cn,CapsIDList=575,CapsTypeList=0,LOOSEROUTEIND=0;",
                f"MOD PUIINFO:PUI=tel:+86575{n},LOCALINFO=,LOOSEROUTEIND=0,DISPLAYNAME=*,MAXSESS=0,PHONECONTEXT=,MAXSIMULTREGS=0,SIFCIDList=5030$5600$5910,NATEMPLATEID=0;",
                f"MOD PUIINFO:PUI=sip:+86575{n}@zj.ims.chinaunicom.cn,LOCALINFO=,LOOSEROUTEIND=0,DISPLAYNAME=*,MAXSESS=0,PHONECONTEXT=,MAXSIMULTREGS=0,SIFCIDList=5030$5600$5910,NATEMPLATEID=0;",
                f"SET IMPREGSET:PUIList=sip:+86575{n}@zj.ims.chinaunicom.cn$tel:+86575{n},DefaultPUI=sip:+86575{n}@zj.ims.chinaunicom.cn;",
                f"SET ALIASEGROUP:PUIList=sip:+86575{n}@zj.ims.chinaunicom.cn$tel:+86575{n},AliasGroupID=+86575{n}@zj.ims.chinaunicom.cn;",
            ]
        )
    return "\n".join(lines)


def build_slf(sub_numbers):
    lines = []
    for n in sub_numbers:
        lines.extend(
            [
                f"ADD SLFUSER:USERIDTYPE=1,USERID=tel:+86575{n},HSSID=1;",
                f"ADD SLFUSER:USERIDTYPE=1,USERID=sip:+86575{n}@zj.ims.chinaunicom.cn,HSSID=1;",
            ]
        )
    return "\n".join(lines)


def build_sss(sub_numbers):
    lines = []
    for n in sub_numbers:
        lines.extend(
            [
                f'ADD OSU SBR:PUI="tel:+86575{n}",NETTYPE=1,CC=86,LATA=575,TYPE="CS",ONLCHG="OFF",OFFLCHG="ON",NOTOPEN="OFF",OWE="OFF",IRCFS="ON",IRACFSC="OFF",NSOUTG="OFF",NSICO="OFF",CARDUSER="OFF",FORCEOL="ON",OVLAP="OFF",CFFT="OFF",CORHT="LC"&"DDD"&"IDD"&"SPCS"&"HF"&"HKMACAOTW"&"LT",CIRHT="LC"&"DDD"&"IDD"&"SPCS"&"HF"&"HKMACAOTW"&"LT",OWECIRHT="LC"&"DDD"&"IDD"&"SPCS"&"HF"&"HKMACAOTW"&"LT",CTXOUTRHT="GRPIN"&"GRPOUT"&"GRPOUTNUM",CTXINRHT="GRPIN"&"GRPOUT"&"GRPOUTNUM",OWECTXOUTRHT="GRPIN"&"GRPOUT"&"GRPOUTNUM",OWECTXINRHT="GRPIN"&"GRPOUT"&"GRPOUTNUM",ACOFAD="57501",COMCODE=0,CUSTYPE="B2C",LANGTYPE=0,SPELINE="NO",CALLERAS=0,CALLEDAS=0,CHARGCATEGORY="FREE",CPC=0,PREPAIDTYPE="0",MAXCOMNUM=65535,IMSUSERTYPE="NMIMS",OUTGOINGBLACK="NO";',
                f'SET OSU OIP:PUI="tel:+86575{n}";',
            ]
        )
    return "\n".join(lines)


def build_sdc(sub_numbers):
    lines = []
    for n in sub_numbers:
        lines.append(f'ADD USR:DN="{n}",LRN="116448{n}",USRTYPE=NGN,LOCZCIDX=5,AREAIDX=5;')
    return "\n".join(lines)


def build_isbc(nexthop, name, ip, cac, max, pool, mgcf, nexthop_val, ra1, ra2, isbc_ip, mgcf_ip, isbc_number):
    lines = [
        "//增加下一跳地址",
        f'ADD NH BASIC:NHID={nexthop},DESC="{name}",IPADDRESS="{ip}";',
        f'ADD NH RADDR:NHID={nexthop},IPADDR="{ip}",PREFIX=32;',
        f'SET NH SUB:NHID={nexthop},SIPTR="ENABLE";',
        "//最大并发数配置",
        f'ADD CAC PROFILE:CACPROFILEID={cac},CPDESC="{name}并发数",UGCALLTIME=10,UGCALLNUM={ceil(max / 100 * 15)},UGMAXCALLNUM={max};',
        f'ADD INST CACRULE:INSTID={cac},CACRULEID={cac},DESC="{name}";',
        f'ADD POLICY GROUP:PLGID={cac},FSTLISTID=1,DSCP="{name}";',
        f'ADD POLICY LIST:PLGID={cac},LISTID=1,DSCP="{name}";',
        f'ADD POLICY ITEM:PLGID={cac},LISTID=1,ITEMID=0,DSCP="{name}",SRVID={cac};',
        "//增加信令池配置",
        f"ADD POOLBASICCONFIG:SGID=15,POOLID={mgcf};",
        f"ADD POOLBASICCONFIG:SGID=15,POOLID={pool},INGRESSPOLICYID={nexthop};",
        f'ADD POLICY ATTACH:POLICYDIR="INGRESS",POLICYPOINT="SIGNAL_POOL",SGID=15,POOLID={pool},SERVICEID={cac},INSTANCETYPE="CAC",INSTANCEID={cac};',
        "//增加路由分析",
        f'ADD RA:ANALYSERID={ra1},FSTLISTID=1,DSCP="{name}-MGCF-SX";',
        f'ADD RA:ANALYSERID={ra2},FSTLISTID=1,DSCP="MGCF-{name}-SX";',
        f'ADD RAL:ANALYSERID={ra1},LISTID=1,DSCP="{name}-MGCF-SX";',
        f'ADD RAL:ANALYSERID={ra2},LISTID=1,DSCP="MGCF-{name}-SX";',
        f"ADD RAI:RAID={ra1},ALID=1,ITEMID=0,SGID=15,POOLID={mgcf};",
        f"ADD RAI:RAID={ra2},ALID=1,ITEMID=0,SGID=15,POOLID={pool};",
        "//增加到MGCF的信令池下一条基本配置。MGCF的下一跳固定为1和2，同一个 pool 下可以增加多个下一跳，可以设置主备方式或者负荷分担",
        f'ADD POOLNH BASIC:SGID=15,POOLID={mgcf},NHID=1,IGRROUT={ra2},EGRROUT=200,TRSTDOM="ENABLE";',
        f'ADD SIP NEXTHOP LINK:SGID=15,POOLID={mgcf},NHID=1,LINKID=1,LOCALIPADDR="{mgcf_ip}",LOCALPORT={nexthop_val},REMOTEPORTTYPE="UDP",REMOTEPORT=5060;',
        f'ADD POOLNH BASIC:SGID=15,POOLID={mgcf},NHID=2,IGRROUT={ra2},EGRROUT=200,TRSTDOM="ENABLE",TRACKID=1;',
        f'ADD SIP NEXTHOP LINK:SGID=15,POOLID={mgcf},NHID=2,LINKID=1,LOCALIPADDR="{mgcf_ip}",LOCALPORT={nexthop_val},REMOTEPORTTYPE="UDP",REMOTEPORT=5060;',
        f"ADD POOL MEDIA:SGID=15,POOLID={mgcf},MEDIA_ID=1,ML=21,MR=2103;",
        f"ADD POOL MEDIA:SGID=15,POOLID={mgcf},MEDIA_ID=2,ML=21,MR=2104;",
        f"ADD POOL MEDIA:SGID=15,POOLID={mgcf},MEDIA_ID=3,ML=22,MR=2203;",
        f"ADD POOL MEDIA:SGID=15,POOLID={mgcf},MEDIA_ID=4,ML=22,MR=2204;",
        f"SET POOLBASICCONFIG:SGID=15,POOLID={mgcf},NEXTHOPFAILOVERRULE=1;",
    ]

    pool_lines = [
        f"ADD POOLNH BASIC:SGID=15,POOLID={pool},NHID={nexthop},IGRROUT={ra1},INPL={nexthop};",
        f'ADD SIP NEXTHOP LINK:SGID=15,POOLID={pool},NHID={nexthop},LINKID=1,LOCALIPADDR="{isbc_ip}",LOCALPORT=5060,REMOTEPORTTYPE="UDP",REMOTEPORT=5060;',
        f"ADD POOL MEDIA:SGID=15,POOLID={pool},MEDIA_ID=1,ML=21,MR=2101;",
        f"ADD POOL MEDIA:SGID=15,POOLID={pool},MEDIA_ID=2,ML=21,MR=2102;",
        f"ADD POOL MEDIA:SGID=15,POOLID={pool},MEDIA_ID=3,ML=22,MR=2201;",
        f"ADD POOL MEDIA:SGID=15,POOLID={pool},MEDIA_ID=4,ML=22,MR=2202;",
        f"SET POOLBASICCONFIG:SGID=15,POOLID={pool},NEXTHOPFAILOVERRULE=1;",
        f"SHOW SIGNALPOOL STATUS:SGID=15,POOLID={pool};",
    ]

    lines.extend(pool_lines)
    lines.append("SAVE CFGFILE")
    return "\n".join(lines)


def build_mgcf(name, adj, node, mgcf_ip, isbc, br1, br2, link, tg, rt, rts, chain, auth, mode, sub_numbers):
    mode_cfg = MODE_CONFIGS.get(mode, MODE_CONFIGS["对等方式"])
    tpdas = mode_cfg["tpdas"]
    callritid = mode_cfg["callritid"]

    conn = choice(["3001&1&2&3", "4&5&6&7", "8&9&10&11", "12&13&14&15"])

    lines = [
        "//邻接局配置",
        f'ADD ADJOFC:ID={adj},NAME="{name}-绍兴",MODULE=1,NET=1,OFCTYPE="PSTN",SPCFMT="HEX",SPCTYPE="24",DPC="{adj}",RC="575",SPTYPE="SEP",SSF="NATIONAL",PRTCTYPE="CHINA";',
        f"SET OFCAPP:ID={adj},DOMAININDEX=1;",
        "//拓扑配置",
        f'ADD TOPOLY:NODEID={node},OFCID={adj},DEVTYP="OTHSWT",PROTYP="SIP",CODEC=40,DTMFTSM="IN",IPNET=2,NAME="{name}-绍兴";',
        "//SIP局配置",
        f'ADD SIPOFC:OFC={adj},URLT="TEL",ATTR={SIP_ATTR},DTMFT="IN",INCODECID=0,OUTCODECID=40;',
        "//邻接主机配置",
        f'ADD ADJHOST:ID={adj},HOSTNAME="ibac{adj}.zj.ims.chinaunicom.cn",REALM="zj.ims.chinaunicom.cn";',
        "//UDP承载配置",
        f'ADD UDPBR:ID={br1},NAME="{name}-绍兴_1",ADDRTYPE="IPV4",IPMODE="REMOTE_VALID",IPV4ADDR="{mgcf_ip}",PORT=0,MODULE=0,ADJHOST={adj};',
        f'ADD UDPBR:ID={br2},NAME="{name}-绍兴_2",ADDRTYPE="IPV4",IPMODE="REMOTE_VALID",IPV4ADDR="{mgcf_ip}",PORT={isbc},MODULE=0,ADJHOST={adj};',
        "//按链路分发",
        f'ADD ULDPLC:PROTOCOL="UDP",DSTCONN={br2},UPLC="LOADSHARE",UDPCONN={conn},NAME="{name}-绍兴";',
        "//SIP信令链路配置",
        f'ADD SIPLNK:ID={link},CONNID={br2},PROTOCOL="UDP",NAME="{name}-绍兴";',
        "//SIP信令路由配置",
        f'ADD SIPRT:ID={adj},NAME="{name}-绍兴",SPLC="RR",LNK={link};',
        "//SIP信令路由集配置",
        f'ADD SIPRTS:ID={adj},NAME="{name}-绍兴",RTPLC="AS",SIPRT={adj}-0;',
        "//URI分析配置",
        f'ADD URI:RTSEL=1,URI="ibac{adj}.zj.ims.chinaunicom.cn",METHOD={URI_METHOD},SIPRTS={adj};',
        "//中继组配置",
        f'ADD TG RTP:TG={tg},OFC={adj},MODULE=0,LINE="SIP",NAME="{name}-绍兴",KIND="BIDIR",TPDAS={tpdas},ROAMDAS=0,SIPROUTESET={adj};',
        f'SET TG:TG={tg},IOI="zj.ims.chinaunicom.cn";',
        "//设置对等中继标签",
        f'SET TGFLG:TG={tg},FTGADD="{CTG_FTG_ADD}",FTGDEL="{CTG_FTG_DEL}",DTGDEL="{CTG_DTG_DEL}",CTGADD="{CTG_CTG_ADD}";',
        "//路由配置",
        f'ADD RT:RT={rt},TG={tg},NAME="{name}-绍兴";',
        "//路由组配置",
        f'ADD RTS:RTS={rts},NAME="{name}-绍兴",RTINFO=1-{tg}-0-0-255,RTFLG="PEAR",CTLFLG="PRIO";',
        "//路由链配置",
        f'ADD CHAIN:CHAIN={chain},RTS1={rts},NAME="{name}-绍兴";',
        "//用户鉴权选择子配置",
        f'ADD AUTHDAS:DAS={auth},DESNAME="{name}-绍兴";',
        "//中继黑白名单鉴权配置",
        f"ADD TGAUTH:TG={tg},AUTHDAS={auth};",
        f'ADD SIPCOMBNUMTRANS:MSGTYPE="RCINVITE",NUMTYPE="FRF",ORGTYPE="TG",CALLORG={tg},TRFAS=507;',
        "//用户鉴权号码配置",
    ]

    for i in range(10):
        lines.append(f'ADD AUTH:DAS={auth},DIGIT="{i}",CALLRITID=999,NAME="{name}-绍兴";')

    for n in sub_numbers:
        num_len = len(n)
        lines.append(f'ADD AUTH:DAS={auth},DIGIT="{n}",CALLRITID={callritid},VALIDLEN={num_len},NAME="{name}-绍兴";')
        lines.append(f'ADD AUTH:DAS={auth},DIGIT="0086575{n}",CALLRITID={callritid},VALIDLEN={num_len + 7},NAME="{name}-绍兴";')

    lines.append("//落地数据配置")

    for n in sub_numbers:
        for entr in TPDNAL_ENTR_RANGE:
            lines.append(f'ADD TPDNAL:ENTR={entr},DIGIT=0086575{n},CAT="LOL",RST1={chain},MINLEN=15,MAXLEN=15,TPDDI=3,ENOPT={TPDNAL_OPT},CALLINGOPTDAS=502;')

    lines.append("//平时用不上，万一要删除时用这段")

    for n in sub_numbers:
        for entr in TPDNAL_ENTR_RANGE:
            lines.append(f'//DEL DNAL:ENTR={entr},NANNAT="ALL",DIGIT="0086575{n}";')

    lines.append('\n//重要提醒：两个 MGCF 都要加一遍，勿忘传表（SYN:DATABASE="ALL";）')
    return "\n".join(lines)


class Sipcall:
    def __init__(self):
        display_random_pet()

        put_markdown("# SIP 数字中继脚本生成器")
        put_radio(
            "mode",
            label="组网模式",
            options=["对等方式", "签约方式"],
            inline=True,
        )
        put_radio(
            "isbc_number",
            label="选择ISBC",
            options=["ISBC-3", "ISBC-4"],
            inline=True,
        )
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
            placeholder="18xx",
            help_text="绍兴原有编号 250-299 已用完，现在从 1800-1899 编号。",
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
            mode = pin["mode"]
            isbc_number = pin["isbc_number"]
            name = str(pin["name"]).strip()
            ip = str(pin["IP"]).strip()
            pool = str(pin["pool"]).strip()
            nexthop = str(pin["nexthop"]).strip()
            ra1, ra2 = str(pin["routes"]).strip().split("/")
            cac = str(pin["cac"]).strip()
            max = int(str(pin["max"]).strip())
            mgcf = str(pin["mgcf"]).strip()
            isbc = str(pin["isbc"]).strip()
            adj = str(pin["adj"]).strip()
            node = str(pin["node"]).strip()
            br1, br2 = str(pin["brs"]).strip().split("/")
            link = str(pin["link"]).strip()
            tg = str(pin["tg"]).strip()
            auth = str(pin["auth"]).strip()
            sub_numbers = [s.strip() for s in str(pin["sub_numbers"]).strip().split("\n") if s.strip()]

            isbc_config = ISBC_CONFIGS.get(isbc_number, ISBC_CONFIGS["ISBC-3"])
            isbc_ip = isbc_config["isbc_ip"]
            mgcf_ip = isbc_config["mgcf_ip"]

            parts = []

            parts.append(f"{'*' * 20}\n\t摘要\n{'*' * 20}")
            parts.append(build_summary(mode, name, ip, pool, nexthop, ra1, ra2, cac, max, mgcf, isbc, adj, node, br1, br2, link, tg, auth, sub_numbers))

            if mode == "签约方式":
                parts.append(f"\n\n{'*' * 20}\n\tHSS\n{'*' * 20}")
                parts.append(build_hss(sub_numbers))

                parts.append(f"\n\n{'*' * 20}\n\tSLF\n{'*' * 20}")
                parts.append(build_slf(sub_numbers))

                parts.append(f"\n\n{'*' * 20}\n\tSSS\n{'*' * 20}")
                parts.append(build_sss(sub_numbers))

            parts.append(f"\n\n{'*' * 20}\n\tSDC\n{'*' * 20}")
            parts.append(build_sdc(sub_numbers))

            parts.append(f"\n\n{'*' * 20}\n\t{isbc_number}\n{'*' * 20}")
            parts.append(build_isbc(nexthop, name, ip, cac, max, pool, mgcf, isbc, ra1, ra2, isbc_ip, mgcf_ip, isbc_number))

            parts.append(f"\n\n{'*' * 20}\n\tMGCF\n{'*' * 20}")
            parts.append(build_mgcf(name, adj, node, mgcf_ip, isbc, br1, br2, link, tg, tg, tg, tg, auth, mode, sub_numbers))

            content = "\n".join(parts)

        put_text(content)
        put_file(f"{name}.txt", content.encode(), ">> 点击下载脚本 <<")


if __name__ == "__main__":
    Sipcall()
