#!/usr/bin/env python
# -*- coding: utf-8 -*-


import zipfile
from io import BytesIO

from pywebio.output import put_button, put_file, put_markdown, put_row, put_scope, use_scope
from pywebio.pin import pin, put_input, put_select

from utils import display_random_pet

base64_table = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="
base64_dict = {i: base64_table[i] for i in range(len(base64_table))}


def base64_encode(bs: bytes):
    result = b""
    blocks_count, left_bytes = divmod(len(bs), 3)

    for i in range(blocks_count):
        bias = int.from_bytes(bs[3 * i : 3 * i + 3], "little")
        block = base64_dict[bias & 0x3F]
        block += base64_dict[(bias >> 6) & 0x3F]
        block += base64_dict[(bias >> 12) & 0x3F]
        block += base64_dict[(bias >> 18) & 0x3F]
        result += block.encode()

    if left_bytes == 0:
        return result
    elif left_bytes == 1:
        bias = int.from_bytes(bs[3 * blocks_count :], "little")
        block = base64_dict[bias & 0x3F]
        block += base64_dict[(bias >> 6) & 0x3F]
        result += block.encode()
        return result
    else:
        bias = int.from_bytes(bs[3 * blocks_count :], "little")
        block = base64_dict[bias & 0x3F]
        block += base64_dict[(bias >> 6) & 0x3F]
        block += base64_dict[(bias >> 12) & 0x3F]
        result += block.encode()
        return result


def encrypt_bytes(key: int, bs: bytes):
    result = bytearray()
    for i in range(len(bs)):
        result.append(bs[i] ^ ((key >> 8) & 0xFF))
        key = result[-1] & key | 0x482D
    return bytes(result)


class Mobaxterm:
    def __init__(self):
        display_random_pet()

        put_markdown("# MobaXterm 注册工具")
        put_row(
            [
                put_select(
                    "selector",
                    options=[
                        ("Professional", 1, True),
                        ("Educational", 3),
                        ("Persional", 4),
                    ],
                    label="版本",
                ),
                None,
                put_input(
                    "username",
                    label="用户名",
                    placeholder="USERNAME",
                ),
                None,
                put_input(
                    "version",
                    label="版本号",
                    placeholder="23.4",
                ),
                None,
                put_input(
                    "count",
                    label="授权数量",
                    placeholder="1",
                ),
            ]
        )
        put_button(
            label="点击生成注册码",
            onclick=self.update,
        )
        put_markdown("----")
        put_scope("output")

    @use_scope("output", clear=True)
    def update(self):
        license_type = pin["selector"]
        username = str(pin["username"]).strip()
        version = str(pin["version"]).strip().split(".")
        major_version = int(version[0])
        minor_version = int(version[1])
        count = int(str(pin["count"]).strip())

        license_string = f"{license_type}#{username}|{major_version}{minor_version}#{count}#{major_version}3{minor_version}6{minor_version}#0#0#0#"
        encoded_license_string = base64_encode(encrypt_bytes(0x787, license_string.encode())).decode()
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_STORED) as f:
            f.writestr("Pro.key", data=encoded_license_string)
        zip_buffer.seek(0)

        put_file(
            "Custom.mxtpro",
            zip_buffer.getvalue(),
            ">> 点击下载生成后的文件，并放到 MobaXterm.exe 同级目录。<<",
        )


if __name__ == "__main__":
    Mobaxterm()
