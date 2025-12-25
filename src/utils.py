#!/usr/bin/env python
# -*- coding: utf-8 -*-

import base64
import glob
import os
from random import choice

from pywebio.output import put_html


def display_random_image():
    """
    在页面右下方显示一个随机图片
    """
    pets_dir = os.path.join(os.path.dirname(__file__), "resources")
    pet_images = glob.glob(os.path.join(pets_dir, "*"))

    if pet_images:
        selected_image = choice(pet_images)
        with open(selected_image, "rb") as f:
            base64_image = base64.b64encode(f.read()).decode("utf-8")
            put_html(f"""
            <img src="data:image/gif;base64,{base64_image}"
                style="
                    position: fixed;
                    bottom: 250px;
                    right: 25px;
                    z-index: 100;
                    width: 250px;
                    pointer-events: none;
                    background: transparent;
                    border: none;
                    box-shadow: none;
                ">
            """)
