#!/usr/bin/env python
# -*- coding: utf-8 -*-

from g4f.client import Client
from pywebio.output import put_button, put_loading, put_markdown, put_scope, put_text, use_scope
from pywebio.pin import pin, put_textarea


class Chat:
    def __init__(self):
        put_markdown("# AI 小助手")
        put_textarea(
            "chat",
            label="AI 小助手",
            rows=4,
            placeholder="",
            help_text="输入要询问的问题。",
        )
        put_button(
            label="点击开始",
            onclick=self.update,
        )
        put_markdown("----")
        put_scope("output")

    @use_scope("output", clear=True)
    def update(self):
        with put_loading():
            put_text("思考中......")
            content = "请提问。"
            client = Client()

            if pin["chat"]:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "ai", "content": pin["chat"]}],
                )
                content = response.choices[0].message.content
        put_markdown(content)


if __name__ == "__main__":
    Chat()
