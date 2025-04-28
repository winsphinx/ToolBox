#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

from pywebio.output import put_button, put_file, put_html, put_markdown, put_scope, use_scope
from pywebio.pin import pin, put_input, put_textarea
from pywebio.session import run_js


def add_copy_button_to_code_blocks():
    # 添加 CSS 样式，用于定位和美化复制按钮
    put_html(
        """
<style>
pre {
    position: relative; /* 设定 pre 元素为相对定位，作为按钮绝对定位的参照 */
    padding-top: 2.5em; /* 在 pre 顶部留出空间给按钮，避免遮挡代码 */
}
.copy-code-button {
    position: absolute; /* 绝对定位，相对于父元素 pre */
    top: 0.5em;        /* 距离 pre 顶部 0.5em */
    right: 0.5em;       /* 距离 pre 右侧 0.5em */
    padding: 0.3em 0.6em; /* 按钮内边距 */
    border: 1px solid #ccc; /* 边框 */
    border-radius: 4px;   /* 圆角 */
    background-color: #f0f0f0; /* 背景色 */
    color: #333;          /* 文字颜色 */
    cursor: pointer;       /* 鼠标悬停时显示手型光标 */
    font-size: 0.9em;      /* 字体大小 */
    opacity: 0.7;          /* 默认透明度，使其不那么显眼 */
    transition: opacity 0.2s, background-color 0.2s; /* 过渡效果 */
    z-index: 1;            /* 确保按钮在代码之上 */
}
.copy-code-button:hover {
    opacity: 1;            /* 鼠标悬停时不透明 */
    background-color: #e0e0e0; /* 悬停时改变背景色 */
}
.copy-code-button.copied {
    background-color: #d4edda; /* 复制成功后的背景色 (淡绿色) */
    color: #155724;          /* 复制成功后的文字颜色 */
    border-color: #c3e6cb;   /* 复制成功后的边框颜色 */
}
</style>
"""
    )

    # 注入 JavaScript 以查找所有代码块并添加复制按钮
    run_js(
        """
(function() {
    // 查找页面上所有由 Markdown 生成的代码块（通常是 pre > code 标签）
    const codeBlocks = document.querySelectorAll('pre > code');
    codeBlocks.forEach((codeBlock) => {
        const preElement = codeBlock.parentElement;
        // 确保 pre 元素存在，并且还没有添加过按钮 (防止重复添加)
        if (!preElement || preElement.querySelector('.copy-code-button')) {
            return;
        }

        // 创建按钮元素
        const button = document.createElement('button');
        button.className = 'copy-code-button'; // 应用 CSS 类
        button.textContent = '复制';           // 按钮默认文字
        button.title = '复制数据';             // 鼠标悬停提示文字

        // 为按钮添加点击事件监听器
        button.addEventListener('click', (event) => {
            event.stopPropagation(); // 阻止事件冒泡，以防触发 pre 元素的其他事件

            // 获取代码块的纯文本内容
            const codeToCopy = codeBlock.innerText || codeBlock.textContent;

            // 使用 navigator.clipboard API 异步复制文本
            navigator.clipboard.writeText(codeToCopy).then(() => {
                // 复制成功后的操作
                button.textContent = '已复制!'; // 更新按钮文字
                button.classList.add('copied');   // 添加 'copied' 类以改变样式
                // console.log('Code copied to clipboard!'); // 可选：在控制台输出日志

                // 设置一个延时，1秒后恢复按钮的原始状态
                setTimeout(() => {
                    button.textContent = '复制';     // 恢复文字
                    button.classList.remove('copied'); // 移除 'copied' 类
                }, 1000);
            }).catch(err => {
                // 复制失败后的操作
                button.textContent = '失败'; // 提示用户复制失败
                console.error('Failed to copy code: ', err); // 在控制台打印错误信息

                // 同样设置延时恢复按钮状态
                 setTimeout(() => {
                    button.textContent = '复制';
                }, 1000);
            });
        });

        // 将创建的按钮添加到 pre 元素的内部，使其定位在右上角
        preElement.appendChild(button);
    });
})();
    """
    )


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
            content = f"# 错误\n{str(e)}"
            put_markdown(content)
        else:
            str_HSS = "## HSS\n```"
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
            str_SLF = "```\n\n## SLF\n```"
            for telno in telnos:
                str_SLF += f"""
ADD SLFUSER:USERIDTYPE=1,USERID=tel:+86575{telno},HSSID=1;
ADD SLFUSER:USERIDTYPE=1,USERID=sip:+86575{telno}@zj.ims.chinaunicom.cn,HSSID=1;
"""
            str_SSS = "```\n\n## SSS\n```"
            for telno in telnos:
                str_SSS += f"""
ADD OSU SBR:PUI="tel:+86575{telno}",NETTYPE=1,CC=86,LATA=575,TYPE="IMS",ONLCHG="OFF",OFFLCHG="ON",NOTOPEN="OFF",OWE="OFF",TSS="TSS_OFF",IRCFS="ON",IRACFSC="OFF",NSOUTG="OFF",NSICO="OFF",CARDUSER="OFF",FORCEOL="OFF",OVLAP="OFF",CFFT="OFF",CORHT="LC"&"DDD"&"SPCS"&"HF"&"LT",CIRHT="LC"&"DDD"&"IDD"&"SPCS"&"HF"&"HKMACAOTW"&"LT",OWECIRHT="LC"&"DDD"&"IDD"&"SPCS"&"HF"&"HKMACAOTW"&"LT",CTXOUTRHT="GRPIN"&"GRPOUT"&"GRPOUTNUM",CTXINRHT="GRPIN"&"GRPOUT"&"GRPOUTNUM",OWECTXOUTRHT="GRPIN"&"GRPOUT"&"GRPOUTNUM",OWECTXINRHT="GRPIN"&"GRPOUT"&"GRPOUTNUM",ACOFAD="57501",COMCODE=0,CUSTYPE="B2C",LANGTYPE=0,SPELINE="NO",CALLERAS=0,CALLEDAS=0,CHARGCATEGORY="FREE",CPC=0,PREPAIDTYPE="0",MAXCOMNUM=1,MEDIACAPNO=0,ZONEINDEX=65535,IMSUSERTYPE="NMIMS",OUTGOINGBLACK="NO",NOANSWERTIMER=0,OPSMSININDEX=0;
SET OSU OIP:PUI="tel:+86575{telno}";
"""
            str_EDS = "```\n\n## EDS\n```"
            for telno in telnos:
                str_EDS += f"""
Add NAPTRRec:E164NUM=575{telno},ZONENAME=6.8.e164.arpa,ORDER=10,PREFERENCE=100,FLAGS=U,SERVICE=E2U+SIP,REGEXP=!%5E.*%24!sip:+86575{telno}@zj.ims.chinaunicom.cn!,TTL=3600000;
"""
            str_SDC = "```\n\n## SDC\n```"
            for telno in telnos:
                str_SDC += f"""
MOD USR:MODE=BYDN,DN="{telno}",NEWLRN="116448{telno}",INCALLINGPREFIX=IN_1-0, INCALLEDPREFIX=IN_1-0;
"""
            str_PON = "```\n\n## PON\n```\nesl user\n"
            content = str_HSS + str_SLF + str_SSS + str_EDS + str_SDC + str_PON

            for index, telno in enumerate(telnos):
                content += f"""
sippstnuser add {ports[index]} 0 telno 86575{telno}

sippstnuser auth set {ports[index]} telno 86575{telno} password-mode password
+86575{telno}@zj.ims.chinaunicom.cn
{passwd}
"""
            content += "```\n"

            put_markdown(content)

            # 调用函数添加按钮
            add_copy_button_to_code_blocks()

            put_file(f"{'-'.join(telnos)}.md", content.encode(), ">> 点击下载脚本 <<")


if __name__ == "__main__":
    ADDIMS()
