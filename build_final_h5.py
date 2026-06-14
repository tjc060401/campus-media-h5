#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the final campus-media-h5.html with all fixes."""

import json
import os
import sys
import base64
import io as _io
from PIL import Image as _PILImage

# Force UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

BASE = r'C:\Users\17418\WorkBuddy\2026-06-13-09-00-12'

# ===== Load processed images =====
with open(os.path.join(BASE, 'images_b64_v2.json'), 'r', encoding='utf-8') as f:
    data = json.load(f)

# Safety: ensure all b64 images have data:image prefix
for cat in ('awards', 'studio', 'sub_studio', 'homepage', 'lion_head', 'sub_depts', 'studio_imgs'):
    if cat not in data: continue
    for item in data[cat]:
        b = item.get('b64', '')
        if b and not b.startswith('data:'):
            fmt = 'image/jpeg'
            if len(b) > 4:
                if b[0] == 'i': fmt = 'image/png'       # iVBOR → png
                elif b[0] == 'R': fmt = 'image/gif'     # R0lG → gif
                elif b[0] == 'U': fmt = 'image/webp'    # UklG → webp
            item['b64'] = 'data:' + fmt + ';base64,' + b

hp_b64 = data['homepage'][0]['b64'] if data.get('homepage') else ''
lion_b64 = data['lion_head'][0]['b64'] if data.get('lion_head') else ''

# ===== Nav Logo (青春川师) =====
with open(os.path.join(BASE, 'nav_logo_b64.txt'), 'r', encoding='utf-8') as f:
    nav_logo_b64 = 'data:image/png;base64,' + f.read().strip()

# ===== 杂志图片处理（纸媒深度板块）=====
MAGAZINE_FOLDER = r'D:\17418\OneDrive—gikbjj\OneDrive - gjkbjj\桌面\新建文件夹\狮山青年杂志'
magazine_groups = []  # list of (group_label, [filenames])

def _make_img_html(_img, max_w=380):
    _img = _img.resize((max_w, int(max_w * _img.height / _img.width)), _PILImage.LANCZOS) if _img.width > max_w else _img
    if _img.mode in ('RGBA', 'P'):
        _img = _img.convert('RGB')
    _buf = _io.BytesIO()
    _img.save(_buf, format='JPEG', quality=92)
    _b64 = base64.b64encode(_buf.getvalue()).decode()
    return '<div class="mag-item" onclick="openLightbox(this.querySelector(\'img\').src)"><img src="data:image/jpeg;base64,' + _b64 + '" alt="狮山青年杂志" loading="lazy"></div>'

# Image groups: (label, [filenames])
_mag_groups_defs = [
    ('(一) 深度专题', ['258caf455573018d616d428f9f99456d.png', 'b1bffe4a426d2e1fe2004fd9ef136bf2.jpg']),
    ('(二) 文艺阵地', ['1.png', '50f7fab916a0dbcd4467cf95e716774c.jpg', 'aae496e88d5ad07b7643c7ec1e3db90e.jpg', '33905f71189b382f98bb0dcc65289634.jpg']),
    ('(三) 校园观察', ['5b65c68da99ebd4b061ba9e741cf4d3e.png', '5605158e12b30a11381ae26cef70ff75.png', '2486725249ce91998ca2c53094194c70.png', 'fb57eb32a4b3184227c03191cff668c9.png']),
]

# ===== 合作交流 docx 图片 =====
DOCX_IMG_DIR = r'C:\Users\17418\WorkBuddy\2026-06-13-09-00-12\docx_images'
_team_imgs = {}
for _fn in ['image1.jpeg', 'image2.jpeg', 'image3.jpeg']:
    _fp = os.path.join(DOCX_IMG_DIR, _fn)
    if os.path.isfile(_fp):
        _img = _PILImage.open(_fp)
        if _img.mode in ('RGBA', 'P'):
            _img = _img.convert('RGB')
        _buf = _io.BytesIO()
        _img.save(_buf, format='JPEG', quality=90)
        _b64 = base64.b64encode(_buf.getvalue()).decode()
        _team_imgs[_fn] = 'data:image/jpeg;base64,' + _b64
    else:
        _team_imgs[_fn] = ''
        print(f'WARNING: {_fn} not found in {DOCX_IMG_DIR}')

# ===== 天府新青年公众号推文截图 =====
_TFQN_DIR = r'D:\17418\OneDrive—gikbjj\OneDrive - gjkbjj\桌面\天府新青年\天府新青年'
_tfqn_imgs = []  # list of (url, b64_src)
for _fn in sorted(os.listdir(_TFQN_DIR)):
    _fp = os.path.join(_TFQN_DIR, _fn)
    if os.path.isfile(_fp) and _fn.lower().endswith(('.jpg','.jpeg','.png','.webp')):
        # Reconstruct URL: httpsmp.weixin.qq.comsXXXX.jpg -> https://mp.weixin.qq.com/s/XXXX
        _name_no_ext = _fn.rsplit('.', 1)[0]
        _url = _name_no_ext.replace('httpsmp.weixin.qq.coms', 'https://mp.weixin.qq.com/s/')
        _img = _PILImage.open(_fp)
        if _img.mode in ('RGBA', 'P'):
            _img = _img.convert('RGB')
        _buf = _io.BytesIO()
        _img.save(_buf, format='JPEG', quality=88)
        _b64 = base64.b64encode(_buf.getvalue()).decode()
        _tfqn_imgs.append((_url, 'data:image/jpeg;base64,' + _b64))

for _label, _fns in _mag_groups_defs:
    _items = []
    for _fn in _fns:
        _fp = os.path.join(MAGAZINE_FOLDER, _fn)
        if os.path.isfile(_fp):
            _img = _PILImage.open(_fp)
            _items.append(_make_img_html(_img))
    magazine_groups.append((_label, ''.join(_items)))

# Build paper cards HTML
_paper_descs = {
    '(一) 深度专题': '聚焦"电子消亡""厌蠢症"等青年热点，用超十万字报告还原真实的青年生态。',
    '(二) 文艺阵地': '"文艺精神""十二楼"栏目，收录小说、散文、诗歌，守护文字的纯粹与浪漫。',
    '(三) 校园观察': '联合青年研究中心开展调研，《大学生社交空心病》《大学生恋爱观》报告影响超1w人。',
}
_paper_cards = ''
for _label, _gallery_html in magazine_groups:
    _desc = _paper_descs.get(_label, '')
    _gallery_section = ''
    if _gallery_html:
        _gallery_section = '<div class="mag-gallery">' + _gallery_html + '</div>'
    _paper_cards += '<div class="content-card"><h4>' + _label + '</h4><p>' + _desc + '</p>' + _gallery_section + '</div>\n'

# ===== 关注我们 — 二维码处理 =====
QR_BASE = r'D:\17418\OneDrive—gikbjj\OneDrive - gjkbjj\桌面\新建文件夹\部门二维码'
follow_html_wechat = ''
follow_html_weibo = ''
_qr_groups = [
    # (显示标签, 展示平台类型, 实际文件夹, 匹配关键词)
    ('青春川师',           '公众号', '公众号', '青春川师'),
    ('狮山青年', '公众号', '公众号', '杂志社'),
    ('师大之声',   '公众号', '公众号', '广播'),
    ('青春川师',           '微博',   '微博',   '青春川师'),
    ('狮山青年', '微博',   '微博',   '杂志社'),
    ('师大之声（狮山）', '微博', '微博',   '狮山'),
    ('师大之声（成龙）', '微博', '微博',   '成龙'),
]
# Track used files per folder to avoid dupes
_used = {}
_follow_cards_wechat = []
_follow_cards_weibo = []
for _label, _disp_type, _folder, _kw in _qr_groups:
    _dir = os.path.join(QR_BASE, _folder)
    if not os.path.isdir(_dir):
        continue
    _found = None
    _key = _dir
    if _key not in _used:
        _used[_key] = set()
    for _fn in sorted(os.listdir(_dir)):
        if _kw in _fn and _fn not in _used[_key]:
            _found = os.path.join(_dir, _fn)
            _used[_key].add(_fn)
            break
    if _found is None:
        continue
    _img = _PILImage.open(_found)
    _img = _img.resize((220, 220), _PILImage.LANCZOS) if _img.width > 220 else _img
    if _img.mode in ('RGBA', 'P'):
        _img = _img.convert('RGB')
    _buf = _io.BytesIO()
    _img.save(_buf, format='JPEG', quality=90)
    _b64 = base64.b64encode(_buf.getvalue()).decode()
    if _disp_type == '公众号':
        _card = '<div class="follow-card"><p class="follow-label" style="font-size:0.82rem;">' + _label + '</p><img src="data:image/jpeg;base64,' + _b64 + '" alt="' + _label + '" style="width:140px;height:140px;object-fit:contain;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,0.08);"></div>'
        _follow_cards_wechat.append(_card)
    else:
        _card = '<div class="follow-card"><p class="follow-label" style="font-size:0.82rem;">' + _label + '</p><img src="data:image/jpeg;base64,' + _b64 + '" alt="' + _label + '" style="width:120px;height:120px;object-fit:contain;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,0.08);"></div>'
        _follow_cards_weibo.append(_card)
if _follow_cards_wechat:
    follow_html_wechat = '<div class="follow-subsection"><h3 class="follow-category">微信公众号</h3><div class="follow-grid" style="grid-template-columns:repeat(3, 1fr)">' + ''.join(_follow_cards_wechat) + '</div></div>'
if _follow_cards_weibo:
    follow_html_weibo = '<div class="follow-subsection"><h3 class="follow-category">微博</h3><div class="follow-grid" style="grid-template-columns:repeat(2, 1fr)">' + ''.join(_follow_cards_weibo) + '</div></div>'
follow_html = follow_html_wechat + follow_html_weibo

# ===== 日常节目音频图片（广播声量-日常栏目）=====
DAILY_AUDIO_FOLDER = r'D:\17418\OneDrive—gikbjj\OneDrive - gjkbjj\桌面\日常节目(1)\日常节目'
daily_audio_html = ''
if os.path.isdir(DAILY_AUDIO_FOLDER):
    _da_items = []
    for _fn in sorted(os.listdir(DAILY_AUDIO_FOLDER)):
        _fp = os.path.join(DAILY_AUDIO_FOLDER, _fn)
        _ext = os.path.splitext(_fn)[1].lower()
        if _ext not in ('.png', '.jpg', '.jpeg'):
            continue
        # Reconstruct URL: httpswww.lizhi.fm1680356321XXXXXu=XXX.jpg -> https://www.lizhi.fm/1680356321/XXXXX?u=XXX
        _stem = os.path.splitext(_fn)[0]
        # httpswww.lizhi.fm1680356321...
        _url = _stem.replace('https', 'https://', 1)  # https://www.lizhi.fm...
        # www.lizhi.fm -> www.lizhi.fm/
        _url = _url.replace('www.lizhi.fm', 'www.lizhi.fm/', 1)
        # After .fm/, next 10 digits are user ID. Insert / after them.
        _pos = _url.find('www.lizhi.fm/') + len('www.lizhi.fm/')
        _url = _url[:_pos+7] + '/' + _url[_pos+7:]
        # u= -> ?u=
        _url = _url.replace('u=', '?u=', 1)
        # Process image
        _img = _PILImage.open(_fp)
        _max_w = 600
        if _img.width > _max_w:
            _img = _img.resize((_max_w, int(_max_w * _img.height / _img.width)), _PILImage.LANCZOS)
        if _img.mode in ('RGBA', 'P'):
            _img = _img.convert('RGB')
        _buf = _io.BytesIO()
        _img.save(_buf, format='JPEG', quality=90)
        _b64 = base64.b64encode(_buf.getvalue()).decode()
        _da_items.append((_url, 'data:image/jpeg;base64,' + _b64))
    _da_parts = []
    _da_parts.append('<div class="daily-audio-grid" style="margin-top:16px; display:grid; grid-template-columns:repeat(4,1fr); gap:10px;">')
    for _url, _b64 in _da_items:
        _da_parts.append(f'<div class="audio-card-item"><a href="{_url}" target="_blank" rel="noopener"><img src="{_b64}" alt="荔枝FM节目" loading="lazy" style="width:100%;height:auto;border-radius:8px;box-shadow:0 1px 6px rgba(0,0,0,0.08);display:block;transition:transform 0.3s ease,box-shadow 0.3s ease;" onmouseover="this.style.transform=\'scale(1.05)\';this.style.boxShadow=\'0 4px 16px rgba(0,0,0,0.18)\'" onmouseout="this.style.transform=\'scale(1)\';this.style.boxShadow=\'0 1px 6px rgba(0,0,0,0.08)\'"></a></div>')
    _da_parts.append('</div>')
    daily_audio_html = ''.join(_da_parts)

# ===== 站庆节目音频图片（广播声量-站庆栏目）=====
STATION_AUDIO_FOLDER = r'D:\17418\OneDrive—gikbjj\OneDrive - gjkbjj\桌面\站庆节目音频'
station_audio_html = ''
if os.path.isdir(STATION_AUDIO_FOLDER):
    _sa_parts = []
    _sa_parts.append('<div class="station-audio-grid" style="margin-top:16px; gap:10px;">')
    for _fn in sorted(os.listdir(STATION_AUDIO_FOLDER)):
        _fp = os.path.join(STATION_AUDIO_FOLDER, _fn)
        if os.path.splitext(_fn)[1].lower() not in ('.png', '.jpg', '.jpeg'):
            continue
        _img = _PILImage.open(_fp)
        _img = _img.resize((160, 160), _PILImage.LANCZOS) if _img.width > 160 else _img
        if _img.mode in ('RGBA', 'P'): _img = _img.convert('RGB')
        _buf = _io.BytesIO()
        _img.save(_buf, format='JPEG', quality=90)
        _b64 = base64.b64encode(_buf.getvalue()).decode()
        _url = os.path.splitext(_fn)[0]
        _url = _url.replace('https', 'https://', 1)
        _url = _url.replace('www.lizhi.fm', 'www.lizhi.fm/')
        _idx = _url.find('1680356')
        if _idx > 0: _url = _url[:_idx+7] + '/' + _url[_idx+7:]
        # Strip session tracking parameter (same for all files)
        if 'u=' in _url: _url = _url[:_url.index('u=')]
        _sa_parts.append('<a href="' + _url + '" target="_blank" style="display:block;border-radius:8px;overflow:hidden;box-shadow:0 2px 6px rgba(0,0,0,0.1);transition:transform 0.3s ease,box-shadow 0.3s ease;" onmouseover="this.style.transform=\'scale(1.04)\';this.style.boxShadow=\'0 4px 16px rgba(0,0,0,0.18)\'" onmouseout="this.style.transform=\'scale(1)\';this.style.boxShadow=\'0 2px 6px rgba(0,0,0,0.1)\'"><img src="data:image/jpeg;base64,' + _b64 + '" alt="站庆栏目" loading="lazy" style="width:100%;height:auto;display:block;"></a>')
    _sa_parts.append('</div>')
    station_audio_html = ''.join(_sa_parts)

# ===== 片花音频图片（广播声量-节点策划）=====
JINGLE_AUDIO_FOLDER = r'D:\17418\OneDrive—gikbjj\OneDrive - gjkbjj\桌面\片花音频'
jingle_audio_html = ''
if os.path.isdir(JINGLE_AUDIO_FOLDER):
    _ja_parts = []
    _ja_parts.append('<div class="jingle-audio-grid" style="margin-top:16px; gap:10px;">')
    for _fn in sorted(os.listdir(JINGLE_AUDIO_FOLDER)):
        _fp = os.path.join(JINGLE_AUDIO_FOLDER, _fn)
        if os.path.splitext(_fn)[1].lower() not in ('.png', '.jpg', '.jpeg'):
            continue
        _img = _PILImage.open(_fp)
        _img = _img.resize((160, 160), _PILImage.LANCZOS) if _img.width > 160 else _img
        if _img.mode in ('RGBA', 'P'): _img = _img.convert('RGB')
        _buf = _io.BytesIO()
        _img.save(_buf, format='JPEG', quality=90)
        _b64 = base64.b64encode(_buf.getvalue()).decode()
        _url = os.path.splitext(_fn)[0]
        _url = _url.replace('https', 'https://', 1)
        _url = _url.replace('mp3tourl.comaudio', 'mp3tourl.com/audio/')
        _ja_parts.append('<a href="' + _url + '" target="_blank" style="display:block;border-radius:8px;overflow:hidden;box-shadow:0 2px 6px rgba(0,0,0,0.1);transition:transform 0.3s ease,box-shadow 0.3s ease;" onmouseover="this.style.transform=\'scale(1.04)\';this.style.boxShadow=\'0 4px 16px rgba(0,0,0,0.18)\'" onmouseout="this.style.transform=\'scale(1)\';this.style.boxShadow=\'0 2px 6px rgba(0,0,0,0.1)\'"><img src="data:image/jpeg;base64,' + _b64 + '" alt="片花" loading="lazy" style="width:100%;height:auto;display:block;"></a>')
    _ja_parts.append('</div>')
    jingle_audio_html = ''.join(_ja_parts)

# ===== 微信推文截图 (五四表彰) =====
wx_screenshot_b64 = ''
wx_screenshot_path = os.path.join(BASE, 'screenshot_wx_b64.txt')
if os.path.exists(wx_screenshot_path):
    with open(wx_screenshot_path, 'r', encoding='utf-8') as _f:
        wx_screenshot_b64 = _f.read().strip()
else:
    # Fallback: process directly
    _img_path = r'D:\17418\OneDrive—gikbjj\OneDrive - gjkbjj\图片\屏幕截图\屏幕截图 2026-06-13 164619.png'
    if os.path.exists(_img_path):
        _img = _PILImage.open(_img_path)
        _img = _img.resize((800, int(800 * _img.height / _img.width)), _PILImage.LANCZOS)
        if _img.mode in ('RGBA', 'P'): _img = _img.convert('RGB')
        _buf = _io.BytesIO()
        _img.save(_buf, format='JPEG', quality=90)
        wx_screenshot_b64 = base64.b64encode(_buf.getvalue()).decode()
wx_article_url = 'https://mp.weixin.qq.com/s/MBgiDHgozAlGjgCv1KQZYQ'

# ===== 微信公众号各板块图片处理 =====
def _trim_whitespace(pil_img, margin=4):
    """Crop whitespace around content in a PIL image."""
    import numpy as np
    arr = np.array(pil_img)
    if arr.ndim == 3:
        gray = np.mean(arr, axis=2)
    else:
        gray = arr.astype(float)
    mask = gray < 245  # non-white pixels (lower threshold = more aggressive crop)
    rows = np.any(mask, axis=1)
    cols = np.any(mask, axis=0)
    if not rows.any() or not cols.any():
        return pil_img  # all white, don't crop
    ymin, ymax = np.where(rows)[0][[0, -1]]
    xmin, xmax = np.where(cols)[0][[0, -1]]
    ymin = max(0, ymin - margin)
    ymax = min(pil_img.height, ymax + margin + 1)
    xmin = max(0, xmin - margin)
    xmax = min(pil_img.width, xmax + margin + 1)
    return pil_img.crop((xmin, ymin, xmax, ymax))

def _process_wx_folder(folder_path, resize_w=220):
    """Process images in a Wechat section folder. Returns HTML string."""
    if not os.path.isdir(folder_path):
        return ''
    parts = ['<div class="wx-imgs-grid">']
    _seen_urls = set()  # deduplicate by final URL
    for fn in sorted(os.listdir(folder_path)):
        ext = os.path.splitext(fn)[1].lower()
        if ext not in ('.png', '.jpg', '.jpeg', '.pdf'):
            continue
        fp = os.path.join(folder_path, fn)
        url = os.path.splitext(fn)[0]
        url = url.replace('https', 'https://', 1)
        # Strip variant suffixes for duplicate-file entries
        url = url.replace('_截图', '').replace('_screenshot', '').replace('_副本', '')
        idx = url.find('mp.weixin.qq.com')
        if idx > 0:
            after = url[idx + len('mp.weixin.qq.com'):]
            if after and after[0] != '/':
                url = url[:idx + len('mp.weixin.qq.com')] + '/' + after
        # Fix /s → /s/ for WeChat article URLs (mp.weixin.qq.com/s/ARTICLE_ID)
        idx2 = url.find('mp.weixin.qq.com/s')
        if idx2 > 0:
            after_s = url[idx2 + len('mp.weixin.qq.com/s'):]
            if after_s and after_s[0] != '/':
                url = url[:idx2 + len('mp.weixin.qq.com/s')] + '/' + after_s
        # Deduplicate: skip if same final URL already exists
        if url in _seen_urls:
            continue
        _seen_urls.add(url)
        if ext == '.pdf':
            # PDF: extract first page as preview image
            try:
                import fitz
                pdf_doc = fitz.open(fp)
                page = pdf_doc[0]
                pix = page.get_pixmap(dpi=150)
                img_data = pix.tobytes("png")
                pdf_doc.close()
                pdf_img = _PILImage.open(_io.BytesIO(img_data))
                # Trim whitespace before resize
                pdf_img = _trim_whitespace(pdf_img, margin=8)
                if pdf_img.width > resize_w:
                    pdf_img = pdf_img.resize((resize_w, int(resize_w * pdf_img.height / pdf_img.width)), _PILImage.LANCZOS)
                if pdf_img.mode in ('RGBA', 'P'):
                    pdf_img = pdf_img.convert('RGB')
                buf = _io.BytesIO()
                pdf_img.save(buf, format='JPEG', quality=90)
                b64 = base64.b64encode(buf.getvalue()).decode()
                parts.append(
                    '<a href="' + url + '" target="_blank" style="display:block;'
                    'border-radius:8px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.08);'
                    'transition:transform 0.2s;"'
                    ' onmouseover="this.style.transform=\'scale(1.03)\'"'
                    ' onmouseout="this.style.transform=\'scale(1)\'">'
                    '<img src="data:image/jpeg;base64,' + b64 + '" alt="推文"'
                    ' style="width:100%;height:auto;display:block;" loading="lazy">'
                    '</a>'
                )
            except Exception as _pdf_err:
                # Fallback: text-only link card
                parts.append(
                    '<a href="' + url + '" target="_blank" style="display:block;'
                    'border-radius:8px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.08);'
                    'transition:transform 0.2s;padding:24px 12px;text-align:center;'
                    'background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;'
                    'text-decoration:none;font-size:0.85rem;min-height:80px;'
                    'display:flex;align-items:center;justify-content:center;"'
                    ' onmouseover="this.style.transform=\'scale(1.03)\'"'
                    ' onmouseout="this.style.transform=\'scale(1)\'">'
                    '📄 点击查看原文</a>'
                )
            continue
        try:
            img = _PILImage.open(fp)
        except Exception:
            # On failure, show text link
            parts.append(
                '<a href="' + url + '" target="_blank" style="display:block;'
                'border-radius:8px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.08);'
                'transition:transform 0.2s;padding:24px 12px;text-align:center;'
                'background:#f5f5f5;color:#555;text-decoration:none;font-size:0.85rem;'
                'display:flex;align-items:center;justify-content:center;"'
                ' onmouseover="this.style.transform=\'scale(1.03)\'"'
                ' onmouseout="this.style.transform=\'scale(1)\'">'
                '🔗 点击查看原文</a>'
            )
            continue
        if img.width > resize_w:
            img = img.resize((resize_w, int(resize_w * img.height / img.width)), _PILImage.LANCZOS)
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        buf = _io.BytesIO()
        img.save(buf, format='JPEG', quality=90)
        b64 = base64.b64encode(buf.getvalue()).decode()
        parts.append(
            '<a href="' + url + '" target="_blank" style="display:block;'
            'border-radius:8px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.08);'
            'transition:transform 0.2s;"'
            ' onmouseover="this.style.transform=\'scale(1.03)\'"'
            ' onmouseout="this.style.transform=\'scale(1)\'">'
            '<img src="data:image/jpeg;base64,' + b64 + '" alt="推文"'
            ' style="width:100%;height:auto;display:block;" loading="lazy">'
            '</a>'
        )
    parts.append('</div>')
    return ''.join(parts)

WX_BASE = r'D:\17418\OneDrive—gikbjj\OneDrive - gjkbjj\桌面'
_wx_folders = [
    ('思想引领', '思想引领板块/思想引领'),
    ('实时资讯', '实时资讯/实时资讯'),
    ('校园热点', '新建文件夹 (2)'),
    ('人物访谈', '人物访谈板块'),
    ('年俗漫画', '年俗漫画板块'),
    ('特色专栏', '特色专栏板块'),
    ('创意推送', '创意推送/创意推送'),
]
wx_section_imgs = {}
for _name, _sub in _wx_folders:
    _full = os.path.join(WX_BASE, _sub)
    wx_section_imgs[_name] = _process_wx_folder(_full)

# Build wx_cards_html
_wx_cards_parts = []
_card_data = [
    ('01 思想引领', '筑牢思想根基，理论内容走深走实；深耕青年成长，主题活动见效见行。', '思想引领', False),
    ('02 实时资讯', '学业就业实践，一手信息全掌握；校园动态秒更新，川师新鲜事不迷路。', '实时资讯', True),
    ('03 校园热点', '重要会议、品牌活动、校园大事，全方位定格川师热点新闻时刻。', '校园热点', True),
    ('04 人物访谈', '打造"川师青年说"特别栏目，让榜样力量照亮青春。', '人物访谈', False),
    ('05 年俗漫画', '青小狮讲年俗，把春节过成"二次元"，传统文化也能很"燃"！', '年俗漫画', False),
    ('06 特色专栏', '打造"川师青年说"特别栏目，让榜样力量照亮青春。', '特色专栏', True),
    ('07 创意推送', '"爱你，最亲爱的自己""再见了冷空气，我宣布加入暖春这个更权威的圈子"，那些让你会心一笑的校园梗，我们比你更懂你。', '创意推送', True),
]
for _title, _desc, _key, _four_col in _card_data:
    _card = '<div class="content-card"><h4>' + _title + '</h4><p>' + _desc + '</p>'
    _imgs = wx_section_imgs.get(_key, '')
    if _imgs:
        if _four_col:
            _imgs = _imgs.replace('wx-imgs-grid"', 'wx-imgs-grid wx-imgs-grid-4"')
        _card += _imgs
    _card += '</div>'
    _wx_cards_parts.append(_card)

wx_cards_html = '\n            '.join(_wx_cards_parts)

# ===== CSS Template =====
css = r"""
/* ===== CSS Variables ===== */
:root {
    --primary: #f49e4e;
    --primary-dark: #7a4f27;
    --primary-light: #fbe1c9;
    --primary-vlight: #fdf5ed;
    --text-on-primary: #333333;
    --text-dark: #2c2c2c;
    --text-mid: #555;
    --text-light: #777;
    --bg-white: #ffffff;
    --bg-light: #fafafa;
    --bg-warm: #fef9f2;
    --shadow: 0 4px 20px rgba(0,0,0,0.08);
    --shadow-lg: 0 10px 40px rgba(0,0,0,0.12);
    --radius: 16px;
    --radius-sm: 10px;
    --transition: 0.35s cubic-bezier(0.4, 0, 0.2, 1);
}

* { margin:0; padding:0; box-sizing:border-box; }
html { scroll-behavior: smooth; }
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
    color: var(--text-dark);
    background: var(--bg-light);
    line-height: 1.7;
    overflow-x: hidden;
}

/* ===== Navigation ===== */
.nav {
    position: fixed; top:0; left:0; right:0; z-index: 1000;
    background: rgba(255,255,255,0.92);
    backdrop-filter: blur(16px) saturate(1.5);
    -webkit-backdrop-filter: blur(16px) saturate(1.5);
    border-bottom: 1px solid rgba(0,0,0,0.06);
    padding: 0 24px;
    display: flex; align-items: center; justify-content: space-between;
    height: 60px;
    transition: var(--transition);
}
.nav.scrolled { box-shadow: var(--shadow); }
.nav-logo {
    height: 48px;
    width: auto;
    display: block;
    object-fit: contain;
    flex-shrink: 0;
}
.nav-links { display: flex; gap: 6px; flex-wrap: wrap; justify-content: flex-end; }
.nav-links a {
    text-decoration: none; color: var(--text-mid); font-size: 0.85rem;
    padding: 6px 12px; border-radius: 8px; transition: var(--transition);
    white-space: nowrap;
}
.nav-links a:hover { background: var(--primary-vlight); color: var(--primary); }

/* ===== Hero Section ===== */
.hero {
    min-height: 100vh;
    display: flex; flex-direction: column; align-items: center; justify-content: center; gap: clamp(28px, 4vh, 48px);
    text-align: center;
    padding: 60px 24px;
    background: linear-gradient(180deg, var(--primary-vlight) 0%, #fff8f0 40%, var(--bg-warm) 100%);
    position: relative;
}
.hero-top-text {
    font-size: clamp(1.6rem, 3.5vw, 2.4rem);
    font-weight: 800;
    color: var(--primary-dark);
    letter-spacing: 6px;
    animation: fadeInUp 0.8s ease-out both;
}
.hero-img-wrap {
    max-width: 800px;
    width: 90%;
    border-radius: var(--radius);
    overflow: hidden;
    box-shadow: none;
    animation: fadeInScale 0.8s ease-out 0.1s both;
}
.hero-img-wrap img {
    width: 100%; height: auto; display: block;
}
.hero-subtitle {
    font-size: 1.6rem;
    font-weight: 700;
    color: var(--primary);
    letter-spacing: 6px;
    animation: fadeInUp 0.8s ease-out 0.4s both;
}
.hero-scroll {
    position: absolute; bottom: 32px;
    animation: bounce 2s infinite;
}
.hero-scroll span {
    display: block; width: 28px; height: 28px;
    border-right: 2px solid var(--primary);
    border-bottom: 2px solid var(--primary);
    transform: rotate(45deg);
    opacity: 0.5;
}

/* ===== Animations ===== */
@keyframes fadeInUp {
    from { opacity:0; transform: translateY(30px); }
    to { opacity:1; transform: translateY(0); }
}
@keyframes fadeInScale {
    from { opacity:0; transform: scale(0.92); }
    to { opacity:1; transform: scale(1); }
}
@keyframes bounce {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-10px); }
}

/* ===== Sections ===== */
.section {
    padding: 80px 24px;
    max-width: 1200px;
    margin: 0 auto;
}
.section-dark {
    background: var(--primary-vlight);
    padding: 80px 24px;
}
.section-dark .section-inner {
    max-width: 1200px;
    margin: 0 auto;
}
.section-title {
    font-size: clamp(1.6rem, 3vw, 2rem);
    font-weight: 800; color: var(--primary-dark);
    text-align: center; margin-bottom: 16px;
    position: relative;
}
.section-title::after {
    content: '';
    display: block;
    width: 60px; height: 3px;
    background: var(--primary);
    margin: 12px auto 0;
    border-radius: 2px;
}
.section-desc {
    text-align: center; color: var(--text-mid);
    max-width: 800px; margin: 0 auto 48px;
    font-size: 1rem; line-height: 1.8;
}

/* ===== About / Media Intro ===== */
.about-grid {
    display: grid; grid-template-columns: 1fr;
    gap: 20px; max-width: 900px; margin: 0 auto;
}
.about-card {
    background: #fff; border-radius: var(--radius);
    padding: 28px 28px; box-shadow: var(--shadow);
    transition: var(--transition);
    border-left: 4px solid var(--primary);
}
.about-card:hover { transform: translateX(4px); box-shadow: var(--shadow-lg); }
.about-card p { color: var(--text-mid); font-size: 0.95rem; line-height: 1.8; text-indent: 2em; }

/* ===== Department Grid (2×2 田字格) ===== */
.dept-grid {
    display: grid; grid-template-columns: repeat(4, 1fr);
    gap: 24px; max-width: 1000px; margin: 0 auto;
}
@media (max-width: 900px) {
    .dept-grid { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 600px) {
    .dept-grid { grid-template-columns: 1fr; }
}
.dept-card {
    background: #fff; border-radius: var(--radius);
    padding: 20px;
    box-shadow: var(--shadow);
    display: flex; flex-direction: column;
}
.dept-name {
    font-size: 1.05rem; font-weight: 700; color: var(--primary-dark);
    margin-bottom: 12px; padding-bottom: 8px;
    border-bottom: 2px solid var(--primary-vlight);
}
.dept-desc {
    color: var(--text-mid); font-size: 0.88rem; line-height: 1.7;
    margin-bottom: 14px; flex: 1;
    text-indent: 2em;
}
.dept-img-single {
    border-radius: var(--radius-sm);
    overflow: hidden;
    box-shadow: var(--shadow);
    cursor: pointer;
    transition: var(--transition);
}
.dept-img-single:hover { transform: translateY(-2px); box-shadow: var(--shadow-lg); }
.dept-img-single img {
    width: 100%; height: auto; display: block;
    aspect-ratio: 1/1; object-fit: cover;
}
@media (max-width: 768px) {
    .dept-grid { grid-template-columns: repeat(2, 1fr); }
    .dept-card { padding: 16px; }
    .dept-name { font-size: 0.95rem; }
    .dept-desc { font-size: 0.82rem; }
}
@media (max-width: 500px) {
    .dept-grid { grid-template-columns: 1fr; }
}

/* ===== Brand / IP ===== */
.brand-intro {
    text-align: left; max-width: 750px; margin: 0 auto 24px;
    color: var(--text-mid); font-size: 0.95rem; line-height: 1.8; text-indent: 2em;
    padding: 28px; background: #fff; border-radius: var(--radius);
    box-shadow: var(--shadow); border-left: 4px solid var(--primary);
}
.lion-icon {
    display: flex; justify-content: center; margin-bottom: 32px;
}
.lion-icon img {
    width: 140px; height: 140px; border-radius: 50%;
    object-fit: cover;
    box-shadow: var(--shadow-lg);
}
.brand-grid {
    display: grid; grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    max-width: 900px; margin: 0 auto;
}
@media (max-width: 768px) {
    .brand-grid { grid-template-columns: repeat(2, 1fr); }
}
.brand-img-box {
    border-radius: var(--radius);
    overflow: hidden;
    box-shadow: var(--shadow);
    transition: var(--transition);
    cursor: pointer;
}
.brand-img-box:hover { transform: translateY(-4px); box-shadow: var(--shadow-lg); }
.brand-img-box img {
    width: 100%; height: auto; display: block;
}

.badge-img-box {
    border-radius: 50%;
    overflow: hidden;
    box-shadow: 0 4px 16px rgba(0,0,0,0.15);
    transition: var(--transition);
    cursor: pointer;
    aspect-ratio: 1/1;
    display: block;
}
.badge-img-box:hover { transform: translateY(-4px); box-shadow: 0 8px 24px rgba(0,0,0,0.2); }
.badge-img-box img {
    width: 100%; height: 100%; display: block;
    border-radius: 50%;
    object-fit: cover;
}

/* ===== 新星小狮获奖作品 ===== */
.xinxiaoshi-grid {
    display: flex; justify-content: center; align-items: flex-start;
    gap: 12px; margin: 20px 0 8px; flex-wrap: wrap;
}
@media (max-width: 600px) {
    .xinxiaoshi-grid { gap: 8px; }
}
.xinxiaoshi-item {
    border-radius: var(--radius-sm);
    overflow: hidden;
    box-shadow: var(--shadow);
    cursor: pointer;
    transition: var(--transition);
    flex-shrink: 0;
}
.xinxiaoshi-item:hover { transform: translateY(-3px); box-shadow: var(--shadow-lg); }
.xinxiaoshi-item img {
    height: 240px; width: auto; display: block;
}
.xinxiaoshi-label {
    text-align: center; color: var(--primary); font-weight: 700;
    font-size: 1.05rem; margin: 4px 0 0 0;
    letter-spacing: 0.5px;
}
.xinxiaoshi-label::after {
    content: ' ▼';
    display: inline-block;
    animation: bounce-arrow 1.2s ease-in-out infinite;
    font-size: 0.85rem;
    margin-left: 4px;
}
@keyframes bounce-arrow {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(5px); }
}

/* ===== Studio Gallery with Tabs ===== */
.gallery-tabs {
    display: flex; justify-content: center; gap: 10px;
    margin-bottom: 32px; flex-wrap: wrap;
}
.gallery-tab {
    padding: 8px 20px; border-radius: 30px;
    border: 2px solid var(--primary-light);
    background: #fff; color: var(--primary);
    font-size: 0.9rem; cursor: pointer;
    transition: var(--transition); font-weight: 600;
}
.gallery-tab:hover, .gallery-tab.active {
    background: var(--primary); color: #fff;
    border-color: var(--primary);
}
.gallery-grid {
    display: grid; grid-template-columns: repeat(4, 1fr);
    gap: 10px;
}
@media (max-width: 900px) {
    .gallery-grid { grid-template-columns: repeat(3, 1fr); }
}
@media (max-width: 600px) {
    .gallery-grid { grid-template-columns: repeat(2, 1fr); }
}
.gallery-content { display: none; }
.gallery-content.active { display: block; }
.gallery-item {
    border-radius: var(--radius-sm);
    overflow: hidden;
    box-shadow: var(--shadow);
    transition: var(--transition);
    cursor: pointer;
    animation: fadeInUp 0.5s ease-out both;
}
.gallery-item.hidden { display: none; }
.gallery-item img {
    width: 100%; height: auto; display: block;
    object-fit: cover;
}
.gallery-more-wrap {
    text-align: center; margin-top: 20px;
}
.gallery-more-btn {
    padding: 10px 32px; border-radius: 30px;
    border: 2px solid var(--primary);
    background: #fff; color: var(--primary);
    font-size: 0.9rem; cursor: pointer;
    transition: var(--transition); font-weight: 600;
}
.gallery-more-btn:hover {
    background: var(--primary); color: #fff;
}
.gallery-item:hover { transform: scale(1.04); box-shadow: var(--shadow-lg); }
.gallery-item img {
    width: 100%; height: 100%; display: block;
    object-fit: cover;
}

/* ===== Awards ===== */
/* ===== Horizontal Timeline ===== */
.h-timeline-bar {
    overflow-x: auto; padding: 12px 0 20px;
    -webkit-overflow-scrolling: touch;
    scrollbar-width: none;
}
.h-timeline-bar::-webkit-scrollbar { display: none; }
.h-timeline-track {
    display: flex; align-items: center; gap: 0;
    min-width: fit-content; justify-content: center;
    position: relative; padding: 20px 40px;
}
.h-timeline-line {
    position: absolute; left: 40px; right: 40px; top: 50%;
    height: 3px; background: linear-gradient(90deg, var(--primary), #f9d2a0, var(--primary));
    border-radius: 2px; transform: translateY(-50%);
}
.h-tl-node {
    position: relative; z-index: 1; cursor: pointer;
    padding: 0 22px; text-align: center; flex-shrink: 0;
    transition: var(--transition);
}
.h-tl-dot {
    width: 24px; height: 24px; border-radius: 50%;
    background: #ddd; margin: 0 auto 8px;
    border: 3px solid #fff; box-shadow: 0 2px 6px rgba(0,0,0,0.1);
    transition: var(--transition);
}
.h-tl-node.active .h-tl-dot {
    background: var(--primary);
    box-shadow: 0 0 0 5px rgba(244,158,78,0.25);
    transform: scale(1.15);
}
.h-tl-node:hover .h-tl-dot { background: #f9b86c; transform: scale(1.1); }
.h-tl-label {
    font-size: 0.82rem; font-weight: 700; color: #999;
    transition: var(--transition);
}
.h-tl-node.active .h-tl-label { color: var(--primary); font-size: 0.9rem; }
/* Award Content Panel — always visible, text-only swap */
.award-panel {
    background: #fff; border-radius: var(--radius); padding: 20px 24px;
    box-shadow: 0 2px 16px rgba(0,0,0,0.06); border-left: 3px solid var(--primary);
    margin-bottom: 24px;
    min-height: 80px;
}
.award-panel .award-year-tag {
    display: inline-block; font-size: 0.85rem; font-weight: 800;
    color: var(--primary); margin-bottom: 8px;
    padding: 2px 12px; border-radius: 100px;
    background: rgba(244,158,78,0.1); border: 1px solid rgba(244,158,78,0.25);
    transition: all 0.25s ease;
}
.award-panel p { font-size: 0.92rem; line-height: 1.8; color: #444; margin: 0; }
.award-panel p strong { color: var(--primary); }
/* ===== Certs 3x3 Grid ===== */
.certs-grid {
    display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px;
}
.certs-grid .cert-item {
    border-radius: var(--radius-sm); overflow: hidden;
    box-shadow: var(--shadow); cursor: pointer;
    transition: var(--transition);
    aspect-ratio: 800 / 552;
    display: flex; align-items: center; justify-content: center;
}
.certs-grid .cert-item:hover { transform: translateY(-2px); box-shadow: var(--shadow-lg); }
.certs-grid .cert-item img {
    width: 100%; height: 100%; display: block;
    object-fit: cover; object-position: center;
}
@media (max-width: 600px) {
    .h-timeline-track { padding: 16px 20px; }
    .h-tl-node { padding: 0 14px; }
    .h-tl-dot { width: 18px; height: 18px; }
    .h-tl-label { font-size: 0.72rem; }
    .h-tl-node.active .h-tl-label { font-size: 0.78rem; }
    .h-timeline-line { left: 20px; right: 20px; }
    .award-panel { padding: 14px 16px; }
    .award-panel p { font-size: 0.85rem; }
    .certs-grid { grid-template-columns: repeat(3, 1fr); gap: 8px; }
}

/* ===== Content Tabs ===== */
.content-tabs {
    display: flex; justify-content: center; gap: 8px;
    margin-bottom: 32px; flex-wrap: wrap;
}
.content-tab {
    padding: 8px 18px; border-radius: 30px;
    border: 2px solid var(--primary-light);
    background: #fff; color: var(--primary);
    font-size: 0.88rem; cursor: pointer;
    transition: var(--transition); font-weight: 600;
}
.content-tab:hover, .content-tab.active {
    background: var(--primary); color: #fff;
    border-color: var(--primary);
}
.content-section { display: none; }
.content-section.active { display: block; }

/* ===== Weibo Sub-tabs ===== */
.weibo-sub-tabs {
    display: flex; justify-content: center; gap: 8px;
    margin-bottom: 20px; flex-wrap: wrap;
}
.weibo-sub-tab {
    padding: 6px 16px; border-radius: 20px;
    border: 1.5px solid var(--primary-light);
    background: #fff; color: var(--primary);
    font-size: 0.82rem; cursor: pointer;
    transition: var(--transition); font-weight: 600;
}
.weibo-sub-tab:hover, .weibo-sub-tab.active {
    background: var(--primary); color: #fff;
    border-color: var(--primary);
}
.weibo-sub-content { display: none; }
.weibo-sub-content.active { display: block; }

/* ===== Content Cards ===== */
.content-list {
    display: grid; gap: 16px; max-width: 880px; margin: 0 auto;
}
.content-card {
    background: #fff; border-radius: var(--radius-sm);
    padding: 20px 24px; box-shadow: var(--shadow);
    transition: var(--transition);
    border-left: 3px solid var(--primary-light);
}
.content-card:hover { border-left-color: var(--primary); transform: translateX(4px); }
.content-card h4 { color: var(--primary-dark); font-size: 0.95rem; margin-bottom: 6px; }
.content-card p { color: var(--text-mid); font-size: 0.88rem; line-height: 1.7; }

/* ===== Magazine Gallery (per-point) 2×2 ===== */
.mag-gallery {
    display: grid; grid-template-columns: repeat(2, 1fr);
    gap: 10px; margin-top: 14px;
}
.mag-item {
    cursor: pointer;
    border-radius: 8px; overflow: hidden;
    box-shadow: 0 2px 10px rgba(0,0,0,0.08);
    transition: var(--transition);
}
.mag-item:hover { transform: translateY(-2px); box-shadow: 0 4px 16px rgba(0,0,0,0.15); }
.mag-item img { width: 100%; height: 320px; object-fit: contain; display: block; background: #f5f5f5; }
@media (max-width: 600px) {
    .mag-item img { height: 240px; }
}

/* ===== WeChat Imgs Grid ===== */
.wx-imgs-grid {
    display: grid; grid-template-columns: repeat(3, 1fr);
    gap: 10px; margin-top: 14px;
}
.wx-imgs-grid-4 {
    grid-template-columns: repeat(4, 1fr);
}
@media (max-width: 768px) {
    .wx-imgs-grid { grid-template-columns: repeat(2, 1fr); }
    .wx-imgs-grid-4 { grid-template-columns: repeat(2, 1fr); }
}

/* ===== Media Gallery ===== */
.media-grid {
    display: grid; grid-template-columns: repeat(4, 1fr);
    gap: 14px;
}
@media (max-width: 900px) {
    .media-grid { grid-template-columns: repeat(3, 1fr); }
}
@media (max-width: 600px) {
    .media-grid { grid-template-columns: repeat(2, 1fr); }
}
.media-item {
    border-radius: var(--radius-sm);
    overflow: hidden;
    box-shadow: var(--shadow);
    transition: var(--transition);
    cursor: pointer;
}
.media-item:hover { transform: scale(1.03); box-shadow: var(--shadow-lg); }
.media-item img {
    width: 100%; height: auto; display: block;
    object-fit: cover;
    max-height: 380px; object-position: top;
}

/* ===== Activity List ===== */
.activity-list {
    display: grid; gap: 16px; max-width: 880px; margin: 0 auto;
}
.activity-card {
    background: #fff; border-radius: var(--radius);
    padding: 24px 28px; box-shadow: var(--shadow);
    transition: var(--transition);
}
.activity-card:hover { transform: translateY(-2px); box-shadow: var(--shadow-lg); }
.activity-card h4 { color: var(--primary-dark); font-size: 1.05rem; margin-bottom: 8px; }
.activity-card p { color: var(--text-mid); font-size: 0.9rem; line-height: 1.8; text-indent: 2em; }

/* ===== Team Section ===== */
.team-category {
    margin-bottom: 32px;
}
.team-category h3 {
    font-size: 1.2rem; font-weight: 700; color: var(--primary-dark);
    margin-bottom: 16px; padding-left: 12px;
    border-left: 4px solid var(--primary);
}
.team-img-row {
    display: flex; gap: 12px; margin-top: 14px;
}
.team-img-row img {
    flex: 1; min-width: 0;
    max-height: 150px; width: auto;
    border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.08);
    object-fit: cover; display: block;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    cursor: pointer;
}
.team-img-row img:hover {
    transform: scale(1.05);
    box-shadow: 0 4px 16px rgba(0,0,0,0.18);
}
@media (max-width: 600px) {
    .team-img-row { flex-direction: column; }
    .team-img-row img { max-height: 130px; }
}

#team .content-card {
    border: 2px solid var(--primary-light);
    border-left: 4px solid var(--primary);
    padding: 20px 24px;
    box-sizing: border-box;
    width: 100%;
    max-width: 880px;
    margin: 0 auto;
}

/* ===== 天府新青年推文网格 3×3 ===== */
.tfqn-grid {
    display: grid; grid-template-columns: repeat(3, 1fr);
    gap: 10px; margin-top: 14px;
}
.tfqn-item {
    display: block; border-radius: 6px; overflow: hidden;
    box-shadow: 0 1px 6px rgba(0,0,0,0.08);
    transition: var(--transition);
    aspect-ratio: 1080 / 283;
    background: #f5f5f5;
}
.tfqn-item:hover { transform: translateY(-2px); box-shadow: 0 3px 12px rgba(0,0,0,0.15); }
.tfqn-item img { width: 100%; height: 100%; object-fit: cover; display: block; }
@media (max-width: 600px) {
    .tfqn-grid { grid-template-columns: repeat(2, 1fr); }
}

/* ===== 关注我们 ===== */
.follow-subsection { margin-bottom: 28px; }
.follow-subsection:last-child { margin-bottom: 0; }
.follow-category {
    font-size: 1.1rem; font-weight: 700; color: var(--text-mid);
    margin-bottom: 14px;
    text-align: center;
}
.follow-grid {
    display: grid; gap: 16px;
    max-width: 860px; margin: 0 auto; padding: 0 16px;
}
.follow-card {
    text-align: center;
    background: #fff;
    border-radius: 12px;
    padding: 18px 14px 20px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.follow-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(0,0,0,0.15);
}
.follow-card img {
    border: 4px solid #fff;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.follow-card img:hover {
    transform: scale(1.1);
    box-shadow: 0 4px 16px rgba(0,0,0,0.18) !important;
}
.follow-label {
    font-weight: 600; font-size: 0.92rem;
    color: var(--text-mid); margin-bottom: 12px;
}
@media (max-width: 600px) {
    .follow-grid {
        grid-template-columns: 1fr 1fr !important;
        gap: 10px;
    }
}

/* ===== Audio Image Grids ===== */
.station-audio-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
}
@media (max-width: 600px) {
    .station-audio-grid { grid-template-columns: repeat(2, 1fr); }
}
.jingle-audio-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
}

/* ===== Footer ===== */
.footer {
    text-align: center;
    padding: 60px 24px;
    background: linear-gradient(180deg, var(--bg-warm), var(--primary-vlight));
    color: var(--text-mid);
}
.footer-lion { margin-bottom: 20px; }
.footer-lion img {
    width: 100px; height: auto; border-radius: 16px;
}
.footer h2 {
    font-size: 1.4rem; font-weight: 700; color: var(--primary-dark);
    margin-bottom: 12px;
}
.footer p {
    font-size: 0.95rem; line-height: 1.5; max-width: 600px; margin: 0 auto 8px;
}

/* ===== Lightbox ===== */
.lightbox {
    display: none; position: fixed; top:0; left:0; width:100%; height:100%;
    background: rgba(0,0,0,0.9); z-index: 9999;
    justify-content: center; align-items: center; cursor: pointer;
}
.lightbox.active { display: flex; }
.lightbox img {
    max-width: 92vw; max-height: 92vh;
    border-radius: 8px; box-shadow: 0 4px 40px rgba(0,0,0,0.4);
}
.lightbox-close {
    position: absolute; top: 20px; right: 30px;
    font-size: 36px; color: #fff; cursor: pointer;
    width: 44px; height: 44px; display: flex;
    align-items: center; justify-content: center;
    border-radius: 50%; background: rgba(255,255,255,0.15);
    transition: background 0.2s;
}
.lightbox-close:hover { background: rgba(255,255,255,0.3); }

/* ===== Scroll Animation ===== */
.fade-in {
    opacity: 0; transform: translateY(40px);
    transition: opacity 0.7s ease, transform 0.7s ease;
}
.fade-in.visible {
    opacity: 1; transform: translateY(0);
}

/* ===== 全局图片清晰度优化 ===== */
img {
    image-rendering: auto;
    -ms-interpolation-mode: bicubic;
}
video {
    image-rendering: auto;
}
@media (-webkit-min-device-pixel-ratio: 2), (min-resolution: 192dpi) {
    img { image-rendering: -webkit-optimize-contrast; }
}

@media (max-width: 768px) {
    .nav {
        flex-direction: column;
        align-items: stretch;
        height: auto;
        padding: 6px 10px 6px;
    }
    .nav-logo {
        height: 36px;
        margin: 0 auto;
    }
    .nav-links {
        width: 100%;
        gap: 3px;
        flex-wrap: nowrap;
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
        scrollbar-width: none;
        justify-content: flex-start;
    }
    .nav-links::-webkit-scrollbar { display: none; }
    .nav-links a {
        font-size: 0.75rem;
        padding: 5px 8px;
        flex-shrink: 0;
        white-space: nowrap;
    }
    .hero {
        padding: 40px 16px;
    }
    .hero-top-text {
        font-size: 1.3rem;
        letter-spacing: 4px;
    }
    .hero-subtitle {
        font-size: 1.3rem;
        letter-spacing: 3px;
    }
    .hero-img-wrap {
        width: 95%;
    }
    .section {
        padding: 50px 16px;
    }
    .section-dark {
        padding: 50px 16px;
    }
    .section-desc {
        font-size: 0.88rem;
        margin-bottom: 32px;
    }
    .about-card {
        padding: 20px 18px;
    }
    .about-card p {
        font-size: 0.88rem;
    }
    .gallery-tab {
        padding: 6px 13px;
        font-size: 0.8rem;
    }
    .gallery-tabs {
        gap: 6px;
        margin-bottom: 24px;
    }
    .weibo-sub-tab {
        padding: 5px 11px;
        font-size: 0.75rem;
    }
    .weibo-sub-tabs {
        gap: 4px;
    }
    .content-tab {
        padding: 6px 14px;
        font-size: 0.82rem;
    }
    .content-tabs {
        gap: 5px;
    }
    .content-card {
        padding: 16px 18px;
    }
    .content-card h4 {
        font-size: 0.9rem;
    }
    .content-card p {
        font-size: 0.82rem;
    }
    .activity-card {
        padding: 18px 20px;
    }
    .activity-card h4 {
        font-size: 0.95rem;
    }
    .jingle-audio-grid {
        grid-template-columns: 1fr;
    }
    .team-category h3 {
        font-size: 1.1rem;
    }
    .footer {
        padding: 40px 16px;
    }
    .footer h2 {
        font-size: 1.2rem;
    }
    .footer p {
        font-size: 0.88rem;
    }
    }
}

@media (max-width: 480px) {
    .hero {
        padding: 30px 12px 60px;
    }
    .hero-top-text {
        font-size: 1.05rem;
        letter-spacing: 3px;
    }
    .section-title {
        font-size: 1.35rem;
    }
    .section-desc {
        font-size: 0.82rem;
    }
    .gallery-tab {
        padding: 5px 9px;
        font-size: 0.72rem;
    }
    .wx-imgs-grid {
        grid-template-columns: 1fr;
    }
    .station-audio-grid {
        grid-template-columns: 1fr;
    }
    .content-tabs {
        gap: 3px;
    }
    .content-tab {
        padding: 5px 10px;
        font-size: 0.75rem;
    }
    .weibo-sub-tab {
        padding: 4px 9px;
        font-size: 0.7rem;
    }
    .lightbox-close {
        top: 10px;
        right: 16px;
        font-size: 28px;
        width: 36px;
        height: 36px;
    }
}
"""

# ===== Build Sub-department HTML =====
dept_names = ['融媒体中心', '青小狮工作室', '师大之声校园广播', '《狮山青年》杂志社']
dept_descs = [
    '校团委官方新媒体核心运营阵地，统筹运营"青春川师"微信、微博、QQ空间三大平台及校团委官网，是<span style="font-weight:bold;color:var(--primary);">整合全媒体中心创作资源的核心枢纽</span>。工作覆盖活动采编、人物专访、视频摄制等全链条内容生产，全平台粉丝超25万，总阅读量突破千万，是<span style="font-weight:bold;color:var(--primary);">校园青年思想引领与文化传播的核心主阵地</span>。',
    '"青小狮"诞生于2016年，青小狮工作室于2021年正式成立。团队以"青春川师"为核心品牌，<span style="font-weight:bold;color:var(--primary);">专注于校园IP视觉创作与衍生开发</span>，围绕青小狮形象打造表情包、主题文创、宣传海报、条漫、短视频等多元创意作品，<span style="font-weight:bold;color:var(--primary);">打造有温度、有辨识度的校园文化可视化载体</span>。',
    '狮子山校区广播站与成龙校区广播站分别于1978年与2008年组建成立，是<span style="font-weight:bold;color:var(--primary);">校园历史最悠久的有声宣传阵地</span>。通过打造资讯、访谈、文艺、音乐等多元栏目，串联起师大学子的校园生活日常。2025全年播出节目374期，荔枝FM累计收听量超6万次，是<span style="font-weight:bold;color:var(--primary);">陪伴师生成长的校园文化符号</span>。',
    '《狮山青年》创刊于1990年，2011年由报纸改版为杂志。团队分为专题、文化、美编、运营四组，每年出版发行5-6期正刊及主题特刊，累计发行超25000册。团队坚守<span style="font-weight:bold;color:var(--primary);">"立于山巅，发青年之声"</span>的初心，积极探索跨媒介融合，<span style="font-weight:bold;color:var(--primary);">记录校园文脉，传递青年思想</span>。'
]

# ===== 网络素养训练营图片 =====
XUNLIANY_FOLDER = r'D:\17418\OneDrive—gikbjj\OneDrive - gjkbjj\桌面\xunliany'
xunliany_html = ''
if os.path.isdir(XUNLIANY_FOLDER):
    _xl_parts = []
    _xl_das = []  # 大合照
    for _fn in sorted(os.listdir(XUNLIANY_FOLDER)):
        _ext = os.path.splitext(_fn)[1].lower()
        if _ext not in ('.png', '.jpg', '.jpeg'):
            continue
        _fp = os.path.join(XUNLIANY_FOLDER, _fn)
        _img = _PILImage.open(_fp)
        _max_w = 1000
        if _img.width > _max_w:
            _img = _img.resize((_max_w, int(_max_w * _img.height / _img.width)), _PILImage.LANCZOS)
        if _img.mode in ('RGBA', 'P'):
            _img = _img.convert('RGB')
        _buf = _io.BytesIO()
        _img.save(_buf, format='JPEG', quality=90)
        _b64 = 'data:image/jpeg;base64,' + base64.b64encode(_buf.getvalue()).decode()
        if '大合照' in _fn:
            _xl_das.append(_b64)
    # 大合照：每张单独一行
    for _i, _b in enumerate(_xl_das):
        _mt = 'margin-top:16px; ' if _i == 0 else ''
        _xl_parts.append('<div style="' + _mt + 'margin-bottom:10px; text-align:center;"><img src="' + _b + '" alt="大合照" style="width:80%; max-width:560px; border-radius:10px; box-shadow:0 2px 12px rgba(0,0,0,0.08);transition:transform 0.3s ease,box-shadow 0.3s ease;cursor:pointer;" loading="lazy" onclick="openLightbox(this.src)" onmouseover="this.style.transform=\'scale(1.04)\';this.style.boxShadow=\'0 4px 16px rgba(0,0,0,0.18)\'" onmouseout="this.style.transform=\'scale(1)\';this.style.boxShadow=\'0 2px 12px rgba(0,0,0,0.08)\'"></div>')
    xunliany_html = '\n'.join(_xl_parts)

# ===== 新星小狮获奖作品 (品牌活动 全民打造星小狮) =====
XINXIAOSHI_FOLDER = r'D:\17418\OneDrive—gikbjj\OneDrive - gjkbjj\桌面\xinxiaoshi'
xinxiaoshi_html = ''
if os.path.isdir(XINXIAOSHI_FOLDER):
    _xxs_parts = ['<div class="xinxiaoshi-grid">']
    for _fn in sorted(os.listdir(XINXIAOSHI_FOLDER)):
        _ext = os.path.splitext(_fn)[1].lower()
        if _ext not in ('.png', '.jpg', '.jpeg'):
            continue
        _fp = os.path.join(XINXIAOSHI_FOLDER, _fn)
        _img = _PILImage.open(_fp)
        _max_w = 600
        if _img.width > _max_w:
            _img = _img.resize((_max_w, int(_max_w * _img.height / _img.width)), _PILImage.LANCZOS)
        if _img.mode in ('RGBA', 'P'):
            _img = _img.convert('RGB')
        _buf = _io.BytesIO()
        _img.save(_buf, format='JPEG', quality=90)
        _b64 = 'data:image/jpeg;base64,' + base64.b64encode(_buf.getvalue()).decode()
        _xxs_parts.append('<div class="xinxiaoshi-item" onclick="openLightbox(this.querySelector(\'img\').src)"><img src="' + _b64 + '" alt="获奖作品" loading="lazy"></div>')
    _xxs_parts.append('</div>')
    _xxs_parts.append('<p class="xinxiaoshi-label">部分作品展示</p>')
    xinxiaoshi_html = '\n'.join(_xxs_parts)

# ===== 星小狮图集 (品牌活动 全民打造星小狮) =====
xingxiaoshi_data = data.get('xingxiaoshi', [])
xingxiaoshi_groups = {}
for xs in xingxiaoshi_data:
    name = xs['name']
    parts = name.replace('\\', '/').split('/')
    subfolder = parts[0] if len(parts) >= 1 else '其他'
    xingxiaoshi_groups.setdefault(subfolder, []).append(xs)

xxs_tab_order = sorted(xingxiaoshi_groups.keys())
xxs_tabs_html = ''
xxs_contents_html = ''
xxs_group_ids = ['xxs-' + str(i) for i in range(len(xxs_tab_order))]

for i, gn in enumerate(xxs_tab_order):
    gid = xxs_group_ids[i]
    active = ' active' if i == 0 else ''
    xxs_tabs_html += '<button class="gallery-tab' + active + '" onclick="switchXxsTab(\'' + gid + '\', this)">' + gn + '</button>'
    
    files = xingxiaoshi_groups.get(gn, [])
    
    items = ''
    for j, sf in enumerate(files):
        delay = 0.1 + j * 0.05
        items += '<div class="gallery-item" style="animation-delay:' + str(round(delay, 2)) + 's" onclick="openLightbox(this.querySelector(\'img\').src)"><img src="' + sf['b64'] + '" alt="' + gn + '" loading="lazy"></div>'
    
    ac = ' active' if i == 0 else ''
    xxs_contents_html += '<div class="gallery-content' + ac + '" id="' + gid + '"><div class="gallery-grid">' + items + '</div></div>'

# ===== 组织框架图片（四个子部门）=====
DEPT_IMG_FOLDER = r'D:\17418\OneDrive—gikbjj\OneDrive - gjkbjj\桌面\新建文件夹\四个子部门'
dept_img_map = {}  # key: 关键词 → b64
if os.path.isdir(DEPT_IMG_FOLDER):
    for _fn in sorted(os.listdir(DEPT_IMG_FOLDER)):
        _ext = os.path.splitext(_fn)[1].lower()
        if _ext not in ('.png', '.jpg', '.jpeg'):
            continue
        _fp = os.path.join(DEPT_IMG_FOLDER, _fn)
        _img = _PILImage.open(_fp)
        _max_w = 500
        if _img.width > _max_w:
            _img = _img.resize((_max_w, int(_max_w * _img.height / _img.width)), _PILImage.LANCZOS)
        if _img.mode in ('RGBA', 'P'):
            _img = _img.convert('RGB')
        _buf = _io.BytesIO()
        _img.save(_buf, format='JPEG', quality=90)
        _b64 = 'data:image/jpeg;base64,' + base64.b64encode(_buf.getvalue()).decode()
        for _kw in ['融媒体', '青小狮', '师大之声', '狮山青年']:
            if _kw in _fn:
                dept_img_map[_kw] = _b64
                break

dept_groups = [
    dept_img_map.get('融媒体', ''),
    dept_img_map.get('青小狮', ''),
    dept_img_map.get('师大之声', ''),
    dept_img_map.get('狮山青年', ''),
]

dept_html = '<div class="dept-grid">'
for idx, (img_src, nm, desc) in enumerate(zip(dept_groups, dept_names, dept_descs)):
    dept_html += '<div class="dept-card fade-in">'
    dept_html += '<div class="dept-name">' + nm + '</div>'
    dept_html += '<div class="dept-desc">' + desc + '</div>'
    if img_src:
        dept_html += '<div class="dept-img-single" onclick="openLightbox(this.querySelector(\'img\').src)"><img src="' + img_src + '" alt="' + nm + '"></div>'
    dept_html += '</div>'
dept_html += '</div>'

# ===== Brand images =====
brand_html = ''
for b in data.get('brand', []):
    brand_html += '<div class="brand-img-box" onclick="openLightbox(this.querySelector(\'img\').src)"><img src="' + b['b64'] + '" alt="品牌形象"></div>'

# ===== 徽章图片 =====
BADGE_FOLDER = r'D:\17418\OneDrive—gikbjj\OneDrive - gjkbjj\桌面\huizhang'
badge_html = ''
if os.path.isdir(BADGE_FOLDER):
    _bd_parts = []
    _bd_files = sorted(os.listdir(BADGE_FOLDER))
    for _fn in _bd_files:
        _ext = os.path.splitext(_fn)[1].lower()
        if _ext not in ('.png', '.jpg', '.jpeg'):
            continue
        _fp = os.path.join(BADGE_FOLDER, _fn)
        _img = _PILImage.open(_fp)
        _max_w = 500
        if _img.width > _max_w:
            _img = _img.resize((_max_w, int(_max_w * _img.height / _img.width)), _PILImage.LANCZOS)
        if _img.mode == 'P':
            _img = _img.convert('RGBA')
        _buf = _io.BytesIO()
        _img.save(_buf, format='PNG')
        _b64 = 'data:image/png;base64,' + base64.b64encode(_buf.getvalue()).decode()
        _bd_parts.append('<div class="badge-img-box" onclick="openLightbox(this.querySelector(\'img\').src)"><img src="' + _b64 + '" alt="徽章"></div>')
    badge_html = '\n'.join(_bd_parts)

# ===== Studio Gallery with Tabs (新分类) =====
# 分类来源：
#   节日类   → 工作室图/节日海报
#   节气类   → 工作室图/节气海报
#   文创类   → 线上家教/文创类
studio_groups = {}
for sf in data['studio']:
    name = sf['name']
    if '节日' in name:
        gn = '节日类'
    elif '节气' in name:
        gn = '节气类'
    else:
        gn = '文创类'
    studio_groups.setdefault(gn, []).append(sf)

tab_order = ['节日类', '节气类', '文创类']
tabs_html = ''
contents_html = ''
group_ids = ['studio-jieri', 'studio-jieqi', 'studio-wenchuang']

for i, gn in enumerate(tab_order):
    gid = group_ids[i]
    active = ' active' if i == 0 else ''
    tabs_html += '<button class="gallery-tab' + active + '" onclick="switchGalleryTab(\'' + gid + '\', this)">' + gn + '</button>'

    files = studio_groups.get(gn, [])
    
    items = ''
    for j, sf in enumerate(files):
        delay = 0.1 + j * 0.05
        items += '<div class="gallery-item" style="animation-delay:' + str(round(delay, 2)) + 's" onclick="openLightbox(this.querySelector(\'img\').src)"><img src="' + sf['b64'] + '" alt="' + gn + '" loading="lazy"></div>'
    
    ac = ' active' if i == 0 else ''
    contents_html += '<div class="gallery-content' + ac + '" id="' + gid + '"><div class="gallery-grid">' + items + '</div></div>'

# ===== Awards certificates (compact thumbnails for 3x3 grid) =====
award_html = ''
for i, a in enumerate(data.get('awards', [])):
    extra = ''
    if i == 5:  # 第6张图，上移让"四川师范大学青春川师"居中
        extra = ' style="object-position:center 58%;"'
    award_html += '<div class="cert-item" onclick="openLightbox(this.querySelector(\'img\').src)"><img src="' + a['b64'] + '" alt="获奖证书" loading="lazy"' + extra + '></div>'

# ===== Awards timeline data =====
award_years = [
    (2017, '青春川师获评<strong>"2016-2017优秀高校团委微博"</strong>称号；《狮山青年》杂志社、青春川师获评<strong>"2016-2017四川省十佳校园媒体"</strong>称号。'),
    (2018, '青春川师、《狮山青年》杂志社获评<strong>"2017-2018四川省十佳校园媒体"</strong>称号；师大之声广播站获评<strong>"最佳潜质奖及最佳人气奖"</strong>。'),
    (2019, '青春川师获评<strong>"2018年度最具服务力高校团委微博"</strong>称号；在"第三届·全国高校新媒体"评选中获评<strong>"最佳人气奖"</strong>，在"新春走基层"中国青年报·中青在线全媒体传播"我看见"系列短视频征集活动中获评<strong>"优秀组织单位"</strong>称号。'),
    (2020, '《狮山青年》杂志社在"中国青年报·中青校媒2019寻找百强校媒"活动中获评<strong>"全国十佳高校校园媒体"</strong>，青春川师获评<strong>"全国优秀高校校园媒体"</strong>；青春川师、《狮山青年》杂志社、师大之声广播站分别获评<strong>"四川省十佳校媒"</strong>称号，《狮山青年》杂志社、师大之声广播站分别获评<strong>"最佳人气奖"</strong>；青春川师在中国青年报·中青校媒"青年当红不让"系列活动中获评<strong>"优秀校园媒体"</strong>称号。'),
    (2021, '青春川师入选<strong>"全国高校共青团重点新媒体工作室"</strong>；获评<strong>"2020年全国十佳高校校园媒体"</strong>。《狮山青年》杂志社在"寻找全国百强校园媒体"活动中获评<strong>"2020年全国优秀高校校园媒体"</strong>称号；青春川师、《狮山青年》杂志社获评<strong>"2021年度四川省十佳校园媒体"</strong>称号。'),
    (2022, '青春川师入选<strong>"2022-2023年度全国高校共青团新媒体重点工作室"</strong>。'),
    (2023, '青春川师获评<strong>"2022-2023全国影响力高校可视化融媒团队"</strong>称号。'),
    (2024, '《狮山青年》杂志社获评<strong>"2023-2024全国影响力高校可视化融媒团队"</strong>称号；青春川师《2024青小狮音乐节报道》获评<strong>"2023-2024年度卓越影响力校园新闻专题作品"</strong>。'),
    (2025, '2025年，《狮山青年》杂志社入选<strong>"2024-2025年度高校校园媒体融合创新案例"</strong>；青春川师《"川师青年说"专题作品》入选<strong>"2024-2025年度高校融合创新新闻专题"</strong>；两者均被收录于《高校新闻扶持计划案例集（2025）》；共青团工作经验被四川省教育厅采纳入<strong>2026年第8期工作简报</strong>。'),
    (2026, '共青团工作经验被四川省教育厅采纳入<strong>2026年第8期工作简报</strong>。'),
]

# Build timeline bar nodes + JS data map (single panel, text-only swap)
_tl_nodes = ''
_tl_txt = '  var _aw={' + ','.join(str(yr)+':`'+txt+'`' for yr,txt in award_years) + '};'
for i, (yr, txt) in enumerate(award_years):
    _active = ' active' if i == 0 else ''
    _tl_nodes += '<div class="h-tl-node' + _active + '" data-year="' + str(yr) + '" onclick="showAwardYear(' + str(yr) + ',this)"><div class="h-tl-dot"></div><span class="h-tl-label">' + str(yr) + '</span></div>'

# ===== 视频宣发 =====
_video_folder = r'D:\17418\OneDrive—gikbjj\OneDrive - gjkbjj\桌面\视频宣发\视频宣发'
video_html = ''
_video_items = []
if os.path.isdir(_video_folder):
    for _fn in sorted(os.listdir(_video_folder)):
        _fp = os.path.join(_video_folder, _fn)
        _ext = os.path.splitext(_fn)[1].lower()
        if _ext not in ('.png', '.jpg', '.jpeg'):
            continue
        # Extract sequence number: "10httpsweixin..." -> seq=10, rest="httpsweixin..."
        _name_no_ext = os.path.splitext(_fn)[0]
        _m = __import__('re').match(r'^(\d+)(https.+)', _name_no_ext)
        if not _m:
            continue
        _seq = int(_m.group(1))
        _stem = _m.group(2)
        # URL: httpsweixin.qq.comsphXXXX -> https://weixin.qq.com/s/phXXXX
        _url = _stem.replace('https', 'https://', 1).replace('.comsph', '.com/sph/', 1)
        # Process image
        _img = _PILImage.open(_fp)
        _max_w = 700
        if _img.width > _max_w:
            _img = _img.resize((_max_w, int(_max_w * _img.height / _img.width)), _PILImage.LANCZOS)
        if _img.mode in ('RGBA', 'P'):
            _img = _img.convert('RGB')
        _buf = _io.BytesIO()
        _img.save(_buf, format='JPEG', quality=88)
        _b64 = base64.b64encode(_buf.getvalue()).decode()
        _video_items.append((_seq, _b64, _url, _fn))

# Sort by sequence number
_video_items.sort(key=lambda x: x[0])

for _seq, _b64, _url, _fn in _video_items:
    video_html += '<div class="media-item"><a href="' + _url + '" target="_blank" rel="noopener"><img src="data:image/jpeg;base64,' + _b64 + '" alt="视频宣发" loading="lazy"></a></div>'

# ===== Weibo =====
# Load from new folder: 微博创意推送/{子文件夹}
WEIBO_NEW_BASE = r'D:\17418\OneDrive—gikbjj\OneDrive - gjkbjj\桌面\新建文件夹\微博创意推送'
_weibo_folders = [
    ('#小狮随手拍', '小狮随手拍',  'weibo-suipai'),
    ('#小狮子投票', '小狮子投票',  'weibo-toupiao'),
    ('#狮信集',     '狮信集',      'weibo-shixinji'),
    ('#狮语·筑梦',  '狮语·筑梦',  'weibo-zhumeng'),
]

weibo_sub_tabs_html = ''
weibo_sub_contents_html = ''
for i, (cat_name, sub_dir, sub_id) in enumerate(_weibo_folders):
    active = ' active' if i == 0 else ''
    weibo_sub_tabs_html += '<button class="weibo-sub-tab' + active + '" onclick="switchWeiboTab(\'' + sub_id + '\', this)">' + cat_name + '</button>'

    items = ''
    _wfolder = os.path.join(WEIBO_NEW_BASE, sub_dir)
    if os.path.isdir(_wfolder):
        for _wfn in sorted(os.listdir(_wfolder)):
            _wext = os.path.splitext(_wfn)[1].lower()
            if _wext not in ('.png', '.jpg', '.jpeg'):
                continue
            _wfp = os.path.join(_wfolder, _wfn)
            _wimg = _PILImage.open(_wfp)
            if _wimg.width > 700:
                _wimg = _wimg.resize((700, int(700 * _wimg.height / _wimg.width)), _PILImage.LANCZOS)
            if _wimg.mode in ('RGBA', 'P'):
                _wimg = _wimg.convert('RGB')
            _wbuf = _io.BytesIO()
            _wimg.save(_wbuf, format='JPEG', quality=90)
            _wb64 = 'data:image/jpeg;base64,' + base64.b64encode(_wbuf.getvalue()).decode()
            items += '<div class="media-item" onclick="openLightbox(this.querySelector(\'img\').src)"><img src="' + _wb64 + '" alt="' + cat_name + '" loading="lazy"></div>'

    ac = ' active' if i == 0 else ''
    weibo_sub_contents_html += '<div class="weibo-sub-content' + ac + '" id="' + sub_id + '"><div class="media-grid">' + items + '</div></div>'

# ===== Assemble full HTML =====
html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>共青团四川师范大学委员会宣传调研部</title>
<style>
''' + css + '''
</style>
</head>
<body>

<!-- Navigation -->
<nav class="nav" id="nav">
    <img class="nav-logo" src="''' + nav_logo_b64 + '''" alt="青春川师">
    <div class="nav-links">
        <a href="#hero">首页</a>
        <a href="#about">团队介绍</a>
        <a href="#org">组织框架</a>
        <a href="#brand">品牌形象</a>
        <a href="#awards">工作成效</a>
        <a href="#content">矩阵建设</a>
        <a href="#activities">品牌活动</a>
        <a href="#team">合作交流</a>
        <a href="#content-follow">关注我们</a>
    </div>
</nav>

<!-- Hero Section -->
<section class="hero" id="hero">
    <p class="hero-top-text">共青团四川师范大学委员会</p>
    <div class="hero-img-wrap">
        <img src="''' + hp_b64 + '''" alt="宣传调研部">
    </div>
    <p class="hero-subtitle">思想引领·服务青年</p>
    <div class="hero-scroll" onclick="document.getElementById('about').scrollIntoView({behavior:'smooth'})">
        <span></span>
    </div>
</section>

<!-- 一、团队介绍 -->
<div id="about" class="section-dark">
    <div class="section-inner">
        <h2 class="section-title">团队介绍</h2>
        <div class="about-grid">
            <div class="about-card fade-in">
                <p><span style="font-weight:bold;color:var(--primary);">共青团四川师范大学委员会宣传调研部（全媒体中心）</span>，是共青团四川师范大学委员会下属的官方宣传出口，统筹运营微信、微博、认证QQ空间、校园广播、纸质刊物等多元传播平台，下设<span style="font-weight:bold;color:var(--primary);">融媒体中心</span>、<span style="font-weight:bold;color:var(--primary);">《狮山青年》杂志社</span>、<span style="font-weight:bold;color:var(--primary);">师大之声校园广播</span>、<span style="font-weight:bold;color:var(--primary);">青小狮工作室</span>四大团队。</p>
            </div>
            <div class="about-card fade-in">
                <p>团队以<span style="font-weight:bold;color:var(--primary);">思想引领</span>为核心职责，以<span style="font-weight:bold;color:var(--primary);">服务青年</span>为根本宗旨，充分发挥全媒体平台的政治引领与文化浸润作用，聚焦青年关切、深耕优质内容。以"青小狮"为核心IP，打通<span style="font-weight:bold;color:var(--primary);">"文字-声音-视觉-影像"全媒传播链路</span>，讲好川师青年故事，传递正向价值，凝聚青春力量。</p>
            </div>
        </div>
    </div>
</div>

<!-- 二、组织框架 -->
<div id="org" class="section">
    <h2 class="section-title">组织框架</h2>
    <div class="section-desc" style="display:flex; flex-direction:column; align-items:center; gap:6px;">
        <p style="margin:0;">四大团队以<span style="font-weight:bold;color:var(--primary);">"让改变，现在就发生"</span>为核心理念</p>
        <p style="margin:0;">联动校院两级宣传力量</p>
        <p style="margin:0;">实现内容、活动、人才、品牌<span style="font-weight:bold;color:var(--primary);">四维共建</span></p>
        <p style="margin:0;">打造协同高效的<span style="font-weight:bold;color:var(--primary);">青年传播矩阵</span></p>
    </div>
    ''' + dept_html + '''
</div>

<div class="lion-icon">
            <img src="''' + lion_b64 + '''" alt="青小狮">
        </div>

<!-- 三、品牌形象 -->
<div id="brand" class="section-dark">
    <div class="section-inner">
        <h2 class="section-title">品牌形象</h2>
        <p class="brand-intro">为<span style="font-weight:bold;color:var(--primary);">创新校园文化传播形式</span>、<span style="font-weight:bold;color:var(--primary);">丰富网络思政视觉表达</span>，以青年喜闻乐见的方式开展思想引领，共青团四川师范大学委员会于2016年打造官方IP形象——<span style="font-weight:bold;color:var(--primary);">青小狮</span>。</p>
        
        <p class="brand-intro">"青"取自青春、青年之意，锚定<span style="font-weight:bold;color:var(--primary);">青年群体</span>定位，象征蓬勃朝气；"狮"与"师"谐音，呼应四川师范大学的<span style="font-weight:bold;color:var(--primary);">校园文脉与精神标识</span>。形象融入灵动活泼的设计语言，赋予IP鲜明的个性魅力，兼具亲和力与传播势能。</p>
        ''' + ('<div class="brand-grid">' + badge_html + '</div>' if badge_html else '') + '''
        <div class="brand-grid" style="margin-top:32px;">
            ''' + brand_html + '''
        </div>
    </div>
</div>

<!-- 四、工作成效 -->
<div id="awards" class="section-dark">
    <div class="section-inner">
        <h2 class="section-title">工作成效</h2>
        <div class="h-timeline-bar fade-in">
            <div class="h-timeline-track">
                <div class="h-timeline-line"></div>
                ''' + _tl_nodes + '''
            </div>
        </div>
        <div class="award-panel fade-in" id="aw-panel">
            <span class="award-year-tag" id="aw-tag">2017 年</span>
            <p id="aw-text">青春川师获评<strong>"2016-2017优秀高校团委微博"</strong>称号；《狮山青年》杂志社、青春川师获评<strong>"2016-2017四川省十佳校园媒体"</strong>称号。</p>
        </div>
        <div class="certs-grid fade-in">
            ''' + award_html + '''
        </div>
    </div>
</div>

<!-- 六、矩阵建设 -->
<div id="content" class="section">
    <h2 class="section-title">矩阵建设</h2>
    <div class="content-tabs">
        <button class="content-tab active" onclick="switchContent(\'wechat\', this)">微信运营</button>
        <button class="content-tab" onclick="switchContent(\'weibo-sec\', this)">微博运营</button>
        <button class="content-tab" onclick="switchContent(\'video-sec\', this)">视频宣发</button>
        <button class="content-tab" onclick="switchContent(\'paper\', this)">纸媒深度</button>
        <button class="content-tab" onclick="switchContent(\'radio\', this)">广播声量</button>
        <button class="content-tab" onclick="switchContent(\'design\', this)">小狮图集</button>
    </div>

    <!-- 微信公众号 -->
    <div class="content-section active" id="content-wechat">
        <div class="content-list">
            ''' + wx_cards_html + '''
    </div>
    </div>

    <!-- 纸媒深度 -->
    <div class="content-section" id="content-paper">
        <div class="content-list">
''' + _paper_cards + '''
        </div>
    </div>

    <!-- 广播声量 -->
    <div class="content-section" id="content-radio">
        <div class="content-list">
            <div class="content-card"><h4>（一）日常栏目</h4><p>《乐活梦享家》分享影视故事，《素年拾光》用音乐治愈心灵，《生活加点料》解锁校园周边乐趣。</p>''' + daily_audio_html + '''</div>
            <div class="content-card"><h4>（二）站庆栏目</h4><p>"站庆"音频专栏，与融媒体中心同步推送；"路过我的声音"，让每一个普通同学都能被听见。</p>''' + station_audio_html + '''</div>
            <div class="content-card"><h4>（三）节点策划</h4><p>五四青年节、国庆、毕业季，推出定制主题片花与特别节目，用声音定格校园时光。</p>''' + jingle_audio_html + '''</div>
        </div>
    </div>

            <!-- 小狮图集 -->
            <div class="content-section" id="content-design">
                <p class="section-desc">一起来看看川师大的青小狮吧！</p>
                <div class="gallery-tabs">
                    ''' + tabs_html + '''
                </div>
                ''' + contents_html + '''
            </div>

    <!-- 视频宣发 -->
    <div class="content-section" id="content-video-sec">
        <p class="section-desc">＃五四青年节 | ＃社会实践 | ＃校园文艺活动</p>
        <div class="media-grid">
            ''' + video_html + '''
        </div>
    </div>

    <!-- 微博创意推送 -->
    <div class="content-section" id="content-weibo-sec">
        <div class="weibo-sub-tabs">
            ''' + weibo_sub_tabs_html + '''
        </div>
        ''' + weibo_sub_contents_html + '''
    </div>
</div>

<!-- 七、特色活动 -->
<div id="activities" class="section-dark">
    <div class="section-inner">
        <h2 class="section-title">品牌活动</h2>
        <div class="activity-list">
            <div class="activity-card fade-in">
                <h4>"青春川师"网络素养训练营</h4>
                <p>训练营一年一期，采用"1+N+1"的培训形式，邀请业内资深专家授课，内容涉及<span style="font-weight:bold;color:var(--primary);">新闻采编</span>、<span style="font-weight:bold;color:var(--primary);">媒体运营</span>、<span style="font-weight:bold;color:var(--primary);">播音主持</span>、<span style="font-weight:bold;color:var(--primary);">视觉设计</span>等领域，参训学员覆盖校院两级团学宣传队伍，<span style="font-weight:bold;color:var(--primary);">致力于提升川师团属网络宣传队伍的专业素养与舆情应对水平</span>。</p>
                ''' + xunliany_html + '''
            </div>
            <div class="activity-card fade-in">
                <h4>全民打造"星"小狮创意设计大赛</h4>
                <p>团队坚持落实<span style="font-weight:bold;color:var(--primary);">共青团思想文化工作产品化战略</span>，将"青小狮"形象标识加入团属思想引领体系，鼓励全校师生通过图片、视频、音频等多种创作形式，<span style="font-weight:bold;color:var(--primary);">对"青小狮"形象进行创新设计</span>，打造青小狮在学生群体中的IP形象，提升其影响范围和传播力度，增强学子凝聚力、延续学校文化基因。</p>
                ''' + xinxiaoshi_html + '''
                <div class="gallery-tabs" style="margin-top:20px;">
                    ''' + xxs_tabs_html + '''
                </div>
                ''' + xxs_contents_html + '''
            </div>
        </div>
    </div>
</div>

<!-- 八、合作交流 -->
<div id="team" class="section">
    <h2 class="section-title">合作交流</h2>

    <div class="team-category fade-in">
        <h3>共青团中央</h3>
        <div class="content-list">
            <div class="content-card"><p>多名团队成员参与<span style="font-weight:bold;color:var(--primary);">共青团中央</span><span style="font-weight:bold;color:var(--primary);">"青梅计划"</span>线上课程，成功推选1名成员至<span style="font-weight:bold;color:var(--primary);">共青团中央</span>实习。</p></div>
        </div>
    </div>

    <div class="team-category fade-in">
        <h3>中青校媒</h3>
        <div class="content-list">
            <div class="content-card"><p>团队积极参与中青校媒各项活动，与<span style="font-weight:bold;color:var(--primary);">中国青年报社四川记者站</span>保持密切联系与合作交流。目前已<span style="font-weight:bold;color:var(--primary);">连续8年</span>推选团队成员至中青校媒（四川），并成功竞选担任主席团成员。</p>
                <div class="team-img-row">
                    <img src="''' + _team_imgs.get('image1.jpeg', '') + '''" alt="中青校媒-1" loading="lazy">
                    <img src="''' + _team_imgs.get('image2.jpeg', '') + '''" alt="中青校媒-2" loading="lazy">
                    <img src="''' + _team_imgs.get('image3.jpeg', '') + '''" alt="中青校媒-3" loading="lazy">
                </div>
            </div>
        </div>
    </div>

    <div class="team-category fade-in">
        <h3>省级平台</h3>
        <div class="content-list">
            <div class="content-card"><p>与<span style="font-weight:bold;color:var(--primary);">四川省青少年新媒体中心</span>建立合作，成立推文小组为<span style="font-weight:bold;color:var(--primary);">天府新青年</span>公众号供稿，目前成功发布推文16篇。</p>
                <div class="tfqn-grid">
''' + ''.join(f'                    <a href="{_url}" target="_blank" rel="noopener" class="tfqn-item"><img src="{_b64}" alt="天府新青年推文" loading="lazy"></a>\n' for _url, _b64 in _tfqn_imgs) + '''                </div>
            </div>
            <div class="content-card"><p>推选多名团队成员至<span style="font-weight:bold;color:var(--primary);">川观新闻</span>、<span style="font-weight:bold;color:var(--primary);">青聚锦官城</span>等省市级优秀媒体平台实习。</p></div>
        </div>
    </div>
</div>

<!-- 关注我们 -->
    <div id="content-follow" style="background: linear-gradient(180deg, var(--bg-warm), var(--primary-vlight)); padding: 60px 20px 0;">
        <h2 class="section-title">关注我们</h2>
        ''' + follow_html_wechat + '''
        ''' + follow_html_weibo + '''
    </div>

<!-- Footer -->
<footer class="footer">
    <div class="footer-lion">
        <img src="''' + lion_b64 + '''" alt="青小狮">
    </div>
    <h2>致每一位青春川师的同行者</h2>
    <p>时光作序，步履不停</p>
    <p>与青春同向，与热忱同频</p>
    <p>宣传调研部（全媒体中心）因你而年轻</p>
    <p>未来可期，我们携手向前</p>
</footer>

<!-- Lightbox -->
<div class="lightbox" id="lightbox" onclick="closeLightbox()">
    <span class="lightbox-close">&times;</span>
    <img src="" alt="大图" id="lightbox-img">
</div>

<script>
// Navigation scroll effect
window.addEventListener('scroll', function() {
    document.getElementById('nav').classList.toggle('scrolled', window.scrollY > 60);
});

// Gallery tab switching
function switchGalleryTab(id, btn) {
    document.querySelectorAll('.gallery-content').forEach(function(el) { el.classList.remove('active'); });
    document.querySelectorAll('.gallery-tab').forEach(function(el) { el.classList.remove('active'); });
    document.getElementById(id).classList.add('active');
    btn.classList.add('active');
}

// Gallery "show more" button
function showMoreGallery(btn, gid) {
    var content = document.getElementById(gid);
    var items = content.querySelectorAll('.gallery-item.hidden');
    items.forEach(function(el) { el.classList.remove('hidden'); });
    btn.parentElement.style.display = 'none';
}

// Content tab switching
function switchContent(name, btn) {
    document.querySelectorAll('.content-section').forEach(function(el) { el.classList.remove('active'); });
    document.querySelectorAll('.content-tab').forEach(function(el) { el.classList.remove('active'); });
    document.getElementById('content-' + name).classList.add('active');
    btn.classList.add('active');
}

// Weibo sub-tab switching
function switchWeiboTab(id, btn) {
    document.querySelectorAll('.weibo-sub-content').forEach(function(el) { el.classList.remove('active'); });
    document.querySelectorAll('.weibo-sub-tab').forEach(function(el) { el.classList.remove('active'); });
    document.getElementById(id).classList.add('active');
    btn.classList.add('active');
}

// 星小狮 tab switching
function switchXxsTab(id, btn) {
    var parent = btn.closest('.activity-card');
    parent.querySelectorAll('.gallery-content').forEach(function(el) { el.classList.remove('active'); });
    parent.querySelectorAll('.gallery-tab').forEach(function(el) { el.classList.remove('active'); });
    document.getElementById(id).classList.add('active');
    btn.classList.add('active');
}

// Lightbox
function openLightbox(src) {
    var lb = document.getElementById('lightbox');
    document.getElementById('lightbox-img').src = src;
    lb.classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeLightbox() {
    document.getElementById('lightbox').classList.remove('active');
    document.body.style.overflow = '';
}

// Scroll animation
var observer = new IntersectionObserver(function(entries) {
    entries.forEach(function(entry) {
        if (entry.isIntersecting) {
            entry.target.classList.add('visible');
            observer.unobserve(entry.target);
        }
    });
}, { threshold: 0.1 });

document.querySelectorAll('.fade-in').forEach(function(el) {
    observer.observe(el);
});

// Award timeline switcher — frame stays, only text swaps
''' + _tl_txt + '''
function showAwardYear(year, btn) {
    document.querySelectorAll('.h-tl-node').forEach(function(n) { n.classList.remove('active'); });
    btn.classList.add('active');
    var tag = document.getElementById('aw-tag');
    var txt = document.getElementById('aw-text');
    if (tag) tag.textContent = year + ' 年';
    if (txt && _aw[year]) txt.innerHTML = _aw[year];
    var bar = document.querySelector('.h-timeline-bar');
    if (bar) {
        bar.scrollTo({ left: btn.offsetLeft - bar.offsetWidth/2 + btn.offsetWidth/2, behavior: 'smooth' });
    }
}
</script>
</body>
</html>'''

# ===== Write HTML =====
output_path = os.path.join(BASE, 'campus-media-h5.html')
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html)

size_mb = os.path.getsize(output_path) / (1024 * 1024)
print(f'HTML written: {output_path}')
print(f'Size: {size_mb:.1f} MB')
print(f'Done!')
tput_path = os.path.join(BASE, 'campus-media-h5.html')
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html)

size_mb = os.path.getsize(output_path) / (1024 * 1024)
print(f'HTML written: {output_path}')
print(f'Size: {size_mb:.1f} MB')
print(f'Done!')
