#!/usr/bin/env python
# -*- coding: utf-8 -*-

import base64
import glob
import os
from random import choice

from pywebio.output import put_html
from pywebio.session import run_js


def add_copy_button_to_code_blocks():
    """
    添加 CSS 样式，用于定位和美化复制按钮
    """
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
        (function () {
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
                button.textContent = '复制'; // 按钮默认文字
                button.title = '复制数据'; // 鼠标悬停提示文字

                // 为按钮添加点击事件监听器
                button.addEventListener('click', (event) => {
                    event.stopPropagation(); // 阻止事件冒泡，以防触发 pre 元素的其他事件

                    // 获取代码块的纯文本内容
                    const codeToCopy = codeBlock.innerText || codeBlock.textContent;

                    // 使用 navigator.clipboard API 异步复制文本
                    navigator.clipboard.writeText(codeToCopy).then(() => {
                        // 复制成功后的操作
                        button.textContent = '已复制!'; // 更新按钮文字
                        button.classList.add('copied'); // 添加 'copied' 类以改变样式

                        // 延时1秒后恢复按钮的原始状态
                        setTimeout(() => {
                            button.textContent = '复制'; // 恢复文字
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


def display_random_pet():
    """
    在页面右下方显示一个随机图片
    """
    pets_dir = os.path.join(os.path.dirname(__file__), "resources")
    pets = glob.glob(os.path.join(pets_dir, "*"))

    if pets:
        selected_pet = choice(pets)
        with open(selected_pet, "rb") as f:
            base64_image = base64.b64encode(f.read()).decode("utf-8")
            put_html(
                f"""
                <img src="data:image/gif;base64,{base64_image}"
                    onmouseover="moveImage(this)"
                    style="
                        position: fixed;
                        bottom: 250px;
                        right: 25px;
                        z-index: 100;
                        width: 250px;
                        transition: all 0.3s ease-in-out; // 让移动更丝滑
                        cursor: pointer;
                        background: transparent;
                    ">

                <script>
                function moveImage(img) {{
                    const step = 500;
                    const padding = 25;
                    const rect = img.getBoundingClientRect();

                    let newLeft = rect.left + (Math.random() - 0.5) * 2 * step;
                    let newTop = rect.top + (Math.random() - 0.5) * 2 * step;

                    newLeft = Math.max(padding, Math.min(window.innerWidth - rect.width - padding, newLeft));
                    newTop = Math.max(padding, Math.min(window.innerHeight - rect.height - padding, newTop));

                    img.style.bottom = 'auto';
                    img.style.right = 'auto';
                    img.style.top = newTop + 'px';
                    img.style.left = newLeft + 'px';
                }}
                </script>
                """
            )
