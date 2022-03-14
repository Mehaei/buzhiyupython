# -*- coding: utf-8 -*-
# @Author: 不止于python
# @Date:   2022-03-13 12:51:53
# @Last Modified by:   不止于python
# @Last Modified time: 2022-03-14 11:59:39
import re
import os
import requests
import ddddocr
from lxml import etree
from fontTools.ttLib import TTFont
from PIL import ImageFont, Image, ImageDraw
from io import BytesIO


class NotFoundFontFileUrl(Exception):
    pass


class CarHomeFont(object):
    # 某车之家论坛字体反爬
    def __init__(self, url, *args, **kwargs):
        self.local_ttf_name = "font.ttf"
        self.page_html = self.download(url)
        self.make_unicode_map(self.local_ttf_name, self.page_html)
        font_manger = FontManger(self.local_ttf_name, save_path=kwargs.get("save_path", None))
        self.new_unicode_map = font_manger.get_unicode_map()

    def make_unicode_map(self, ttf_name, page_html):
        # 获取字体的连接文件
        font_file_name = (re.findall(r",url\('(//.*\.ttf)?'\) format", page_html) or [""])[0]
        if not font_file_name:
            raise NotFoundFontFileUrl("Not found font file name")
        if not os.path.exists(ttf_name):
            # 下载字体文件
            file_content = self.download("https:%s" % font_file_name, content=True)
            # 将字体文件保存到本地
            with open(ttf_name, 'wb+') as f:
                f.write(file_content)
            print("Font file download success")

    def repalce_source_code(self, replaced_html):
        #  转为 编码 比如: \uec8e
        replaced_html = replaced_html.encode("latin-1", "backslashreplace").decode("utf-8")
        for utf_code, word in self.new_unicode_map.items():
            replaced_html = replaced_html.replace("\\u%s" % utf_code.lower(), word)
        # 再次将替换后的字符转为正常unicode
        replaced_html = replaced_html.encode("latin-1", "backslashreplace").decode("utf-8")
        # 转为中文
        replaced_html = replaced_html.encode("utf-8").decode("unicode_escape")
        return replaced_html

    def get_subject_content(self):
        page_html = self.repalce_source_code(self.page_html)
        xp_html = etree.HTML(page_html)
        subject_text = ''.join(xp_html.xpath('//div[@class="tz-paragraph"]//text()'))
        return subject_text

    def download(self, url, *args, try_time=5, method="GET", content=False, **kwargs):
        kwargs.setdefault("headers", {})
        kwargs["headers"].update({"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36"})
        while try_time:
            try:
                response = requests.request(method.upper(), url, *args, **kwargs)
                if response.ok:
                    if content:
                        return response.content
                    return response.text
                else:
                    continue
            except Exception as e:
                try_time -= 1
                print("download error: %s" % e)


class FontManger(object):
    img_size = 128
    def __init__(self, ttf_pname, save_path=None):
        # 用于识别ttf文件
        self._font = TTFont(ttf_pname)
        self._img_font = ImageFont.truetype(ttf_pname, int(FontManger.img_size * 0.7))
        self._ocr = ddddocr.DdddOcr(show_ad=False)
        self.save_path = save_path
        if self.save_path and not os.path.exists(self.save_path):
            os.makedirs(self.save_path)
        self.font_map = {}
        self.fg_color = 0
        self.bg_color = 255

    def font_to_img(self, txt):
        # 字体转为图片
        # 创建一个为1024像素的白底图片对象
        img = Image.new('1', (self.img_size, self.img_size), self.bg_color)
        # 为图片创建一个画布对象
        draw = ImageDraw.Draw(img)
        x, y = draw.textsize(txt, font=self._img_font)
        draw.text(
            ((self.img_size - x) // 2, (self.img_size - y) // 2),
            txt,
            font=self._img_font,
            fill=self.fg_color)

        return img

    def read_img_res(self, fname, txt):
        # 识别图片文字
        pil = self.font_to_img(txt)
        bytes_io = BytesIO()
        pil.save(bytes_io, format="PNG")
        bytes_str = bytes_io.getvalue()
        if self.save_path:
            with open("%s/%s.png" % (self.save_path, fname), "wb+") as f:
                f.write(bytes_str)
        return self._ocr.classification(bytes_str)

    def get_unicode_map(self):
        # 构建unicode mapping
        for ascii_value, glyphname in self._font.getBestCmap().items():
            if not ascii_value:
                continue
            ascii_value = chr(ascii_value)
            glyphname = glyphname[3:].lower()
            self.font_map[glyphname] = self.read_img_res(glyphname, ascii_value)
        return self.font_map


if __name__ == "__main__":
    url = "https://club.autohome.com.cn/bbs/thread/34d6bcc159b717a9/85794510-1.html#pvareaid=6830286"
    car = CarHomeFont(url, save_path="images")
    text = car.get_subject_content()
    print(text)

