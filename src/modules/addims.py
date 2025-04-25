#!/usr/bin/env python
# -*- coding: utf-8 -*-


from pywebio.output import put_button, put_file, put_markdown, put_scope, put_text, use_scope
from pywebio.pin import pin, put_input, put_textarea


class ADDIMS:
    def __init__(self):
        put_markdown("# 手工IMS加号码脚本生成器")
        put_textarea(
            "telnos",
            label="号码",
            placeholder="88881234\n88885678\n...",
            help_text="8位号码。有多个一行一个。",
        )
        put_input(
            "passwd",
            label="密码",
            placeholder="Fxxxxx",
            help_text="SIP的注册密码，在工单上有。",
        )
        put_textarea(
            "ports",
            label="端口",
            placeholder="0/1/2\n0/1/3\n...",
            help_text="GPON的端口号，在工单上有。顺序和号码一一对应。",
        )
        put_button(
            label="点击生成脚本",
            onclick=self.update,
        )
        put_markdown("----")
        put_scope("output")

    @use_scope("output", clear=True)
    def update(self):
        def validate_input():
            import re

            telnos = [s.strip() for s in pin["telnos"].strip().split("\n") if s.strip()]
            passwd = pin["passwd"].strip()
            ports = [s.strip() for s in pin["ports"].strip().split("\n") if s.strip()]

            if not all([telnos, passwd, ports]):
                raise ValueError("号码、密码和端口为必填项。")

            if any(not re.match(r"^\d{8}$", tel) for tel in telnos):
                raise ValueError("号码必须为8位纯数字。")

            if any(not re.match(r"^\d+/\d+/\d+$", p) for p in ports):
                raise ValueError("端口格式应为 0/1/2 结构。")

            if len(ports) != len(telnos):
                raise ValueError("端口数量与号码数量不一致。")

            return telnos, passwd, ports

        try:
            telnos, passwd, ports = validate_input()
        except ValueError as e:
            content = f"错误: {str(e)}"
            put_text(content)
        else:
            str_HSS = """
*****************
****   HSS   ****
*****************
"""
            for telno in telnos:
                str_HSS += f"""
ADD NEWPVI:PVITYPE=0,PVI=+86575{telno}@zj.ims.chinaunicom.cn,IREGFLAG=1,IDENTITYTYPE=0,PECFN=ccf01.zj.ims.chinaunicom.cn,SECFN=ccf02.zj.ims.chinaunicom.cn,PCCFN=ccf01.zj.ims.chinaunicom.cn,SCCFN=ccf02.zj.ims.chinaunicom.cn,SecVer=30,UserName=+86575{telno}@zj.ims.chinaunicom.cn,PassWord={passwd},Realm=zj.ims.chinaunicom.cn,ACCTypeList=*,ACCInfoList=*,ACCValueList=*;
ADD NEWPUI:IDENTITYTYPE=0,PUI=tel:+86575{telno},BARFLAG=0,REGAUTHFG=1,ROAMSCHEMEID=1,SPID=8,SPDesc=绍兴SP,PVIList=+86575{telno}@zj.ims.chinaunicom.cn,CapsIDList=575,CapsTypeList=0,LOOSEROUTEIND=0;
ADD NEWPUI:IDENTITYTYPE=0,PUI=sip:+86575{telno}@zj.ims.chinaunicom.cn,BARFLAG=0,REGAUTHFG=1,ROAMSCHEMEID=1,SPID=8,SPDesc=绍兴SP,PVIList=+86575{telno}@zj.ims.chinaunicom.cn,CapsIDList=575,CapsTypeList=0,LOOSEROUTEIND=0;
MOD PUIINFO:PUI=tel:+86575{telno},LOCALINFO=,LOOSEROUTEIND=0,DISPLAYNAME=*,MAXSESS=0,PHONECONTEXT=,MAXSIMULTREGS=0,SIFCIDList=5030$5600$5910,NATEMPLATEID=0;
MOD PUIINFO:PUI=sip:+86575{telno}@zj.ims.chinaunicom.cn,LOCALINFO=,LOOSEROUTEIND=0,DISPLAYNAME=*,MAXSESS=0,PHONECONTEXT=,MAXSIMULTREGS=0,SIFCIDList=5030$5600$5910,NATEMPLATEID=0;
SET IMPREGSET:PUIList=sip:+86575{telno}@zj.ims.chinaunicom.cn$tel:+86575{telno},DefaultPUI=sip:+86575{telno}@zj.ims.chinaunicom.cn;
SET ALIASEGROUP:PUIList=sip:+86575{telno}@zj.ims.chinaunicom.cn$tel:+86575{telno},AliasGroupID=+86575{telno}@zj.ims.chinaunicom.cn;
"""
            str_SLF = """
*****************
****   SLF   ****
*****************
"""
            for telno in telnos:
                str_SLF += f"""
ADD SLFUSER:USERIDTYPE=1,USERID=tel:+86575{telno},HSSID=1;
ADD SLFUSER:USERIDTYPE=1,USERID=sip:+86575{telno}@zj.ims.chinaunicom.cn,HSSID=1;
"""
            str_SSS = """
*****************
****   SSS   ****
*****************
"""
            for telno in telnos:
                str_SSS += f"""
ADD OSU SBR:PUI="tel:+86575{telno}",NETTYPE=1,CC=86,LATA=575,TYPE="IMS",ONLCHG="OFF",OFFLCHG="ON",NOTOPEN="OFF",OWE="OFF",TSS="TSS_OFF",IRCFS="ON",IRACFSC="OFF",NSOUTG="OFF",NSICO="OFF",CARDUSER="OFF",FORCEOL="OFF",OVLAP="OFF",CFFT="OFF",CORHT="LC"&"DDD"&"SPCS"&"HF"&"LT",CIRHT="LC"&"DDD"&"IDD"&"SPCS"&"HF"&"HKMACAOTW"&"LT",OWECIRHT="LC"&"DDD"&"IDD"&"SPCS"&"HF"&"HKMACAOTW"&"LT",CTXOUTRHT="GRPIN"&"GRPOUT"&"GRPOUTNUM",CTXINRHT="GRPIN"&"GRPOUT"&"GRPOUTNUM",OWECTXOUTRHT="GRPIN"&"GRPOUT"&"GRPOUTNUM",OWECTXINRHT="GRPIN"&"GRPOUT"&"GRPOUTNUM",ACOFAD="57501",COMCODE=0,CUSTYPE="B2C",LANGTYPE=0,SPELINE="NO",CALLERAS=0,CALLEDAS=0,CHARGCATEGORY="FREE",CPC=0,PREPAIDTYPE="0",MAXCOMNUM=1,MEDIACAPNO=0,ZONEINDEX=65535,IMSUSERTYPE="NMIMS",OUTGOINGBLACK="NO",NOANSWERTIMER=0,OPSMSININDEX=0;
SET OSU OIP:PUI="tel:+86575{telno}";
"""
            str_EDS = """
*****************
****   EDS   ****
*****************
"""
            for telno in telnos:
                str_EDS += f"""
优先级：10
次优先级：100
标识：URI
名称：E2U+SIP
正则表达式：!^.*$!sip:+86575{telno}@zj.ims.chinaunicom.cn!
替换：留空
周期：3600000
"""
            str_SDC = """
*****************
****   SDC   ****
*****************
"""
            for telno in telnos:
                str_SDC += f"""
MOD USR:MODE=BYDN,DN="{telno}",NEWLRN="116448{telno}",INCALLINGPREFIX=IN_1-0, INCALLEDPREFIX=IN_1-0;
"""
            str_PON = """
*****************
****   PON   ****
*****************

esl user
"""
            content = str_HSS + str_SLF + str_SSS + str_EDS + str_SDC + str_PON

            for index, telno in enumerate(telnos):
                content += f"""
sippstnuser add {ports[index]} 0 telno 86575{telno}

sippstnuser auth set {ports[index]} telno 86575{telno} password-mode password
+86575{telno}@zj.ims.chinaunicom.cn
{passwd}
"""

            put_text(content)
            put_file(f"{'-'.join(telnos)}.txt", content.encode(), ">> 点击下载脚本 <<")


if __name__ == "__main__":
    ADDIMS()
