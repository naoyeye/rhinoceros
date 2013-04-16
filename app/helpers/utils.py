#!/usr/bin/env python
# coding: utf-8

import os
import web
import config
import Image, ImageFilter

import md5, time, types

def dict_remove(d, *keys):
    for k in keys:
        if d.has_key(k):
            del d[k]
    
def capitalize_first(str):
    if not str:
        str = ''
    return ' '.join(map(string.capitalize, str.lower().split()))

def make_unique_md5():
    return md5.md5(time.ctime() + config.encryption_key).hexdigest()

def get_all_functions(module):
    functions = {}
    for f in [module.__dict__.get(a) for a in dir(module)
        if isinstance(module.__dict__.get(a), types.FunctionType)]:
        functions[f.__name__] = f
    return functions

def sqlands(left, lst):
    """Similar to webpy sqlors but for ands"""
    if isinstance(lst, web.utils.iters):
        lst = list(lst)
        ln = len(lst)
        if ln == 0:
            return web.SQLQuery("1!=2")
        if ln == 1:
            lst = lst[0]
    if isinstance(lst, web.utils.iters):
        return web.SQLQuery(['('] +
          sum([[left, web.sqlparam(x), ' AND '] for x in lst], []) +
          ['1!=2)']
        )
    else:
        return left + web.sqlparam(lst)

def get_ip():
    return web.ctx.get('ip', '000.000.000.000')

def store(tablename, _test=False, **values):
    try:
        db.insert(tablename, **values)
    except:
        db.update(tablename, **values)

#高斯模糊
class MyGaussianBlur(ImageFilter.Filter):
    name = "GaussianBlur"

    def __init__(self, radius=2, bounds=None):
        self.radius = radius
        self.bounds = bounds

        # print self.radius
        # print '2222222222'

    def filter(self, image):
        if self.bounds:
            clips = image.crop(self.bounds).gaussian_blur(self.radius)
            image.paste(clips, self.bounds)
            return image
        else:
            return image.gaussian_blur(self.radius)


#生成头像缩略图 （供裁剪用）
#def make_thumb(path, sizes=[(160,160)]):
def make_thumb(path):
    """
    sizes 参数传递要生成的尺寸，可以生成多种尺寸
    """
    base, ext = os.path.splitext(path)
    try:
        im = Image.open(path)
    except IOError:
        print ' in  IOError'
        return
    mode = im.mode
    if mode not in ('L', 'RGB'):
        if mode == 'RGBA':
            # 透明图片需要加白色底
            im.load()
            alpha = im.split()[3]
            bgmask = alpha.point(lambda x: 255-x)
            im = im.convert('RGB')
            # paste(color, box, mask)
            im.paste((255,255,255), None, bgmask)
        else:
            im = im.convert('RGB')

    # if width == height:
    #     region = im
    # else:
    #     if width > height:
    #         delta = (width - height)/2
    #         box = (delta, 0, delta+height, height)
    #     else:
    #         delta = (height - width)/2
    #         box = (0, delta, width, delta+width)
    #     region = im.crop(box)

    #for size in sizes:
        # if ext == '.gif':
        #     filename = base + "_" + "%sx%s" % (str(size[0]), str(size[1])) + ext
        # else:
        #     filename = base + "_" + "%sx%s" % (str(size[0]), str(size[1])) + ".jpg"
    filename = base + "_160.jpg"
    #thumb = region.resize((size[0],size[1]), Image.ANTIALIAS)
    thumb = im.thumbnail((160,160), Image.ANTIALIAS)
    im.save(filename, quality=100) # 默认 JPEG 保存质量是 75, 不太清楚。可选值(0~100)

#裁剪缩略图
def make_thumb_crop(path, x, y, w, h):
    #/static/upload/image/2012/8/7/2012875121_66cb2d42c83e97f6eac6eb6a0ec28a1f_160.jpg
    #切割为
    #/static/upload/image/2012/8/7/2012875121_66cb2d42c83e97f6eac6eb6a0ec28a1f
    base = os.path.splitext(path)[0][:-4]
    im = Image.open(path)
    filename = base + "_48.jpg"
    x2 = int(round(float(x)))
    y2 = int(round(float(y)))
    w2 = int(round(float(w)))
    h2 = int(round(float(h)))

    box = (x2, y2, x2+w2, y2+h2)
    region = im.crop(box)
    thumb = region.resize((48,48), Image.ANTIALIAS)
    thumb.save(filename, quality=100) # 默认 JPEG 保存质量是 75, 不太清楚。可选值(0~100)

#生成node 75x75 缩略图
def make_node_thumb(path):
    base, ext = os.path.splitext(path)
    try:
        im = Image.open(path)
    except IOError:
        print ' in  IOError'
        return

    mode = im.mode
    if mode not in ('L', 'RGB'):
        if mode == 'RGBA':
            # 透明图片需要加白色底
            im.load()
            alpha = im.split()[3]
            bgmask = alpha.point(lambda x: 255-x)
            im = im.convert('RGB')
            # paste(color, box, mask)
            im.paste((255,255,255), None, bgmask)
        else:
            im = im.convert('RGB')

    width, height = im.size
    # 裁剪图片成正方形
    if width > height:
        delta = (width - height) / 2
        box = (delta, 0, width - delta, height)
        region = im.crop(box)
    elif height > width:
        delta = (height - width) / 2
        box = (0, delta, width, height - delta)
        region = im.crop(box)
    else:
        region = im

    filename = base + "_75.jpg"

    thumb = region.resize((75, 75), Image.ANTIALIAS)
    # thumb = im.thumbnail((75,75), Image.ANTIALIAS)
    thumb.save(filename, quality=100) # 默认 JPEG 保存质量是 75, 不太清楚。可选值(0~100)

#生成post 1200x550 / 750x230 / 365x230 缩略图
def make_post_thumb(path, sizes=[(1200,550), (750,230), (365,230), (366,366), (751,365)]):
    """
    sizes 参数传递要生成的尺寸，可以生成多种尺寸
    """
    base, ext = os.path.splitext(path)
    try:
        im = Image.open(path)
    except IOError:
        print ' in  IOError'
        return
    mode = im.mode
    if mode not in ('L', 'RGB'):
        if mode == 'RGBA':
            # 透明图片需要加白色底
            im.load()
            alpha = im.split()[3]
            bgmask = alpha.point(lambda x: 255-x)
            im = im.convert('RGB')
            # paste(color, box, mask)
            im.paste((255,255,255), None, bgmask)
        else:
            im = im.convert('RGB')

    width, height = im.size
    
    for size in sizes:
        filename = base + "_" + str(size[0]) + ".jpg"
        #如果图片小于宽度或者高度
        # if size[0] > width or size[1] > height:
        #     if size[0] > width:
        #         b = int(size[0]/width) - 1
        #     elif size[1] > height:
        #         b = int(size[1]/height) - 1

        #     if b > 1:
        #         im = im.filter(MyGaussianBlur(radius=b))

        if float(width) / float(height) == float(str(size[0])) / float(str(size[1])):
            newimg = im.resize((int(size[0]), int(size[1])), Image.ANTIALIAS)
            box = (0, 0, int(size[0]), int(size[1]))
            region = newimg.crop(box)
            region.save(filename, quality=100)
        if float(width) / float(height) < float(size[0]) / float(size[1]):
            #如果是高图，先把原图重设到size宽
            newimg = im.resize((int(size[0]), int(float(height)/(float(width)/float(size[0])))), Image.ANTIALIAS)
            newimg_width, newimg_height = newimg.size
            delta = (newimg_height - int(size[1]))/2
            if int(size[0]) == 751:
                delta = (newimg_height - int(size[1]))/4
            box = (0, delta, int(size[0]), delta+int(size[1]))
            region = newimg.crop(box)
            region.save(filename, quality=100)
        if float(width) / float(height) > float(size[0]) / float(size[1]):
            #如果是宽图，先把原图重设到size高
            newimg = im.resize((int(float(width)/(float(height)/float(size[1]))), int(size[1])), Image.ANTIALIAS)
            newimg_width, newimg_height = newimg.size
            delta = (newimg_width - int(size[0]))/2
            # if int(size[0]) == 751:
            #     print '================'
            #     print '2222222222222222'
                # delta = 0
            box = (delta, 0, delta+int(size[0]), int(size[1]))
            region = newimg.crop(box)
            region.save(filename, quality=100)

# def make_post_thumb_450(path):
#     base, ext = os.path.splitext(path)
#     try:
#         im = Image.open(path)
#     except IOError:
#         print ' in  IOError'
#         return
#     mode = im.mode
#     if mode not in ('L', 'RGB'):
#         if mode == 'RGBA':
#             # 透明图片需要加白色底
#             im.load()
#             alpha = im.split()[3]
#             bgmask = alpha.point(lambda x: 255-x)
#             im = im.convert('RGB')
#             # paste(color, box, mask)
#             im.paste((255,255,255), None, bgmask)
#         else:
#             im = im.convert('RGB')
#     filename = base + "_450.jpg"
#     thumb = im.thumbnail((450,450), Image.ANTIALIAS)
#     im.save(filename, quality=100) # 默认 JPEG 保存质量是 75, 不太清楚。可选值(0~100)


def make_thumb_3(path, sizes=[(1201,1201),(450,450)]):
    """
    sizes 参数传递要生成的尺寸，可以生成多种尺寸
    """
    base, ext = os.path.splitext(path)
    try:
        im = Image.open(path)
    except IOError:
        print ' in  IOError'
        return
    mode = im.mode
    if mode not in ('L', 'RGB'):
        if mode == 'RGBA':
            # 透明图片需要加白色底
            im.load()
            alpha = im.split()[3]
            bgmask = alpha.point(lambda x: 255-x)
            im = im.convert('RGB')
            # paste(color, box, mask)
            im.paste((255,255,255), None, bgmask)
        else:
            im = im.convert('RGB')

    # width, height = im.size

    # if width == height:
    #     region = im
    # else:
    #     if width > height:
    #         delta = (width - height)/2
    #         box = (delta, 0, delta+height, height)
    #     else:
    #         delta = (height - width)/2
    #         box = (0, delta, width, delta+width)
    #     region = im.crop(box)

    # for size in sizes:
        # if size == 1201:
    filename = base + "_1201-max.jpg"
    width, height = im.size

    #如果图片小于宽度或者高度
    # for size in sizes:
    #     if size[0] > width or size[1] > height:
    #         if size[0] > width:
    #             b = int(size[0]/width) - 1
    #             if b > 1:
    #                 print b
    #                 print '1---------'
    #                 im = im.filter(MyGaussianBlur(radius=b))
    #             else:
    #                 print '1111111111'
    #         elif size[1] > height:
    #             b = int(size[1]/height) - 1

    #             if b > 1:
    #                 print b
    #                 print '2---------'
    #                 im = im.filter(MyGaussianBlur(radius=b))
    #             else:
    #                 print '2222222222'


    thumb = im.thumbnail((1201,1201), Image.ANTIALIAS)
    im.save(filename, quality=100) # 默认 JPEG 保存质量是 75, 不太清楚。可选值(0~100)
    # elif size == 450:
    filename = base + "_450-max.jpg"
    #2013.02.10 改变大小 实际存储为640
    thumb = im.thumbnail((640,640), Image.ANTIALIAS)
    im.save(filename, quality=100) # 默认 JPEG 保存质量是 75, 不太清楚。可选值(0~100)
