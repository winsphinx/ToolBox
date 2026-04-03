#!/usr/bin/env python
# -*- coding: utf-8 -*-

import base64
from pathlib import Path
from random import choice

from pywebio.output import put_html
from pywebio.session import run_js

_css_injected = False
_pet_cache = {}


def add_copy_button_to_code_blocks():
    global _css_injected
    if _css_injected:
        return

    _css_injected = True
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
    在页面显示一个随机宠物图片，点击出现爆炸粒子特效
    """
    pets_dir = Path(__file__).parent / "resources"

    if not _pet_cache:
        _pet_cache["pets"] = list(pets_dir.glob("*"))

    pets = _pet_cache.get("pets", [])
    if not pets:
        return

    selected_pet = choice(pets)

    if selected_pet not in _pet_cache:
        with open(selected_pet, "rb") as f:
            _pet_cache[selected_pet] = base64.b64encode(f.read()).decode("utf-8")

    base64_image = _pet_cache[selected_pet]

    put_html(f"""
        <img id="petImage"
             src="data:image/gif;base64,{base64_image}"
             onmouseover="moveImage(this)"
             onclick="explodePet(this)"
             style="
                position: fixed;
                bottom: 250px;
                right: 25px;
                z-index: 100;
                width: 250px;
                transition: all 0.3s ease-in-out;
                cursor: pointer;
                background: transparent;
             ">

        <canvas id="explosionCanvas"
                style="position: fixed; top: 0; left: 0; z-index: 101; pointer-events: none; display: none;">
        </canvas>

        <script>
        // 移动函数
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

        // 粒子爆炸
        let canvas = document.getElementById('explosionCanvas');
        let ctx = canvas.getContext('2d');
        let particles = [];
        let animationFrame = null;

        class Particle {{
            constructor(x, y) {{
                this.x = x;
                this.y = y;
                this.size = Math.random() * 8 + 4;            // 粒子大小
                this.speedX = (Math.random() - 0.5) * 18;     // 横向速度
                this.speedY = (Math.random() - 0.5) * 18 - 3; // 纵向速度（略向上偏）
                this.gravity = 0.25;
                this.life = 55 + Math.random() * 25;          // 存活帧数
                this.alpha = 1;
                this.color = 'hsl(' + (Math.random() * 360 | 0) + ', 90%, 65%)';
            }}

            update() {{
                this.speedY += this.gravity;
                this.x += this.speedX;
                this.y += this.speedY;
                this.life -= 1;
                this.alpha = this.life / 70;
                this.size *= 0.98;   // 逐渐缩小
            }}

            draw() {{
                ctx.save();
                ctx.globalAlpha = this.alpha;
                ctx.fillStyle = this.color;
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                ctx.fill();
                ctx.restore();
            }}
        }}

        function createExplosion(x, y, count = 65) {{
            particles = [];
            for (let i = 0; i < count; i++) {{
                particles.push(new Particle(x, y));
            }}
        }}

        function animateExplosion() {{
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            for (let i = particles.length - 1; i >= 0; i--) {{
                particles[i].update();
                particles[i].draw();

                if (particles[i].life <= 0 || particles[i].alpha <= 0.05) {{
                    particles.splice(i, 1);
                }}
            }}

            if (particles.length > 0) {{
                animationFrame = requestAnimationFrame(animateExplosion);
            }} else {{
                canvas.style.display = 'none';
            }}
        }}

        // 点击图片触发爆炸
        window.explodePet = function(img) {{
            // 先让图片快速淡出
            img.style.transition = 'opacity 0.25s ease-out';
            img.style.opacity = '0';

            // 获取图片在视口中的位置（用于爆炸中心点）
            const rect = img.getBoundingClientRect();
            const centerX = rect.left + rect.width / 2;
            const centerY = rect.top + rect.height / 2;

            // 设置 canvas 大小为全屏并显示
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
            canvas.style.display = 'block';

            // 创建爆炸
            createExplosion(centerX, centerY, 65);

            // 开始动画
            if (animationFrame) cancelAnimationFrame(animationFrame);
            animateExplosion();

            // 移除旧图片防止重复点击
            setTimeout(() => {{
                if (img && img.parentNode) {{
                    img.remove();
                }}
            }}, 300);
        }};

        // 窗口大小变化时同步
        window.addEventListener('resize', () => {{
            if (canvas.style.display === 'block') {{
                canvas.width = window.innerWidth;
                canvas.height = window.innerHeight;
            }}
        }});
        </script>
        """)
