#!/usr/bin/env python
# coding: utf-8

# Author: Alex Ksikes

# TODO:
# - we should subclass form.Form instead.

import web, re, urlparse, datetime, urllib, utils, string, time, datetime

# import HTMLParser

# html_parser = HTMLParser.HTMLParser()

def format_date(d, f):
    return d.strftime(f)

def url_quote(url):
    return web.urlquote(url)

def html_quote(html):
    return web.htmlquote(html)

def url_encode(query, clean=True, doseq=True, **kw):
    query = web.dictadd(query, kw)
    if clean is True:
        for q, v in query.items():
            if not v:
                del query[q]
    return urllib.urlencode(query, doseq)

def cut_length(s, max=40, tooltip=False):
    s_cut = s[0:]
    if len(s) > max:
        s_cut = s[0:max] + '...'
    if tooltip:
        s_cut = '<span title="%s">%s</span>' % (s, s_cut)
    
    return s_cut

def get_nice_url(url):
    host, path = urlparse.urlparse(url)[1:3]
    if path == '/':
        path = ''
    return cut_length(host+path)

def capitalize_first(str):
    if not str:
        str = ''
    return ' '.join(map(string.capitalize, str.lower().split()))

def text2html(s):
    s = replace_breaks(s)
    s = replace_indents(s)
    return replace_links(s)
    
def replace_breaks(s):
    s = re.sub('\r', '<br />' ,s )
    return re.sub('\n', '<br />', s)

def replace_indents(s):
    s = re.sub('\t', 4*' ', s)
    return re.sub('\s{2}', '&nbsp;'*2, s)

# reg = "([a-zA-Z0-9:\/\])((http|https|ftp):\/\/)?([A-Za-z0-9-]+\.)+[A-Za-z]{2,}(:[0-9]+)?[.\/=\?%\-&_~`@[\]\':+!]*([^\"\"])*?(?![\/=\?%\-&_~`@[\]\':+!A-Za-z0-9.])"

def replace_links(s):
    return re.sub('(http://[^\s]+)', r'<a rel="nofollow" href="\1">' + r'\1' + '</a>', s, re.M)

# we may need to get months ago as well
def how_long(d):
    return web.datestr(d, datetime.datetime.now())

def split(pattern, str):
    return re.split(pattern, str)

def sub(pattern, rpl, str):
    p = re.compile(pattern, re.I)
    return p.sub(rpl, str)

def render_form(form, from_input, to_input):
    # do each input from from_input to to_input
    inputs = list(form.inputs)
    def index(inputs, name):
        for n, input in enumerate(inputs):
            if input.name == name:
                return n
        return -1
       
    start = index(inputs, from_input)
    till = index(inputs, to_input)
    form.inputs = inputs[start:till+1]
    
    # render the top note ourselves
    html = ''
    if start == 0 and not form.valid:
        if form.note:
            html = '<div class="wrong">%s</div>\n' % form.note
        else:
            html = '<div class="wrong">Oups looks like you\'ve made a couple of errors. Please correct the errors below and try again.</div>\n'
    form.note = None
    
    html += form.render_css()
    form.inputs = tuple(inputs)
    
    return html

def get_site_domain():
    import config
    return config.site_domain

def timestrf(timeData):
    n = datetime.datetime.now()
    s = timeData
    mkt_last = time.mktime(s.timetuple())
    mkt_now = time.mktime(n.timetuple())
    delt_time = (mkt_now - mkt_last)/60 #转换为分钟
    d = (n-s) #时间差

    if delt_time < 1:
        return '刚刚' + str(d.seconds) + '秒前'
    elif delt_time < 60:
        u = d.seconds/60
        return str(u) + '分钟前'
    elif  60 <= delt_time < 60*24 :
        u = d.seconds/(60*60)
        return str(u) + '小时前'
    elif 60*24 <= delt_time < 60*24*2:
        return '昨天' +  timeData.strftime("%H:%M")
    elif 60*24*2 <= delt_time < 60*24*3:
        return '前天' + timeData.strftime("%H:%M")
    else:
        return timeData.strftime("%m月%d日 %H:%M")

# Configuration for urlize() function
LEADING_PUNCTUATION  = ['(', '<', '&lt;']
TRAILING_PUNCTUATION = ['.', ',', ')', '>', '\n', '&gt;']

# list of possible strings used for bullets in bulleted lists
DOTS = ['&middot;', '*', '\xe2\x80\xa2', '&#149;', '&bull;', '&#8226;']

unencoded_ampersands_re = re.compile(r'&(?!(\w+|#\d+);)')
word_split_re = re.compile(r'(\s+)')
punctuation_re = re.compile('^(?P<lead>(?:%s)*)(?P<middle>.*?)(?P<trail>(?:%s)*)$' % \
    ('|'.join([re.escape(x) for x in LEADING_PUNCTUATION]),
    '|'.join([re.escape(x) for x in TRAILING_PUNCTUATION])))
simple_email_re = re.compile(r'^\S+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9._-]+$')
link_target_attribute_re = re.compile(r'(<a [^>]*?)target=[^\s>]+')
html_gunk_re = re.compile(r'(?:<br clear="all">|<i><\/i>|<b><\/b>|<em><\/em>|<strong><\/strong>|<\/?smallcaps>|<\/?uppercase>)', re.IGNORECASE)
hard_coded_bullets_re = re.compile(r'((?:<p>(?:%s).*?[a-zA-Z].*?</p>\s*)+)' % '|'.join([re.escape(x) for x in DOTS]), re.DOTALL)
trailing_empty_content_re = re.compile(r'(?:<p>(?:&nbsp;|\s|<br \/>)*?</p>\s*)+\Z')

def autolink(text, trim_url_limit=None, nofollow=False):
    """
    Converts any URLs in text into clickable links. Works on http://, https:// and
    www. links. Links can have trailing punctuation (periods, commas, close-parens)
    and leading punctuation (opening parens) and it'll still do the right thing.

    If trim_url_limit is not None, the URLs in link text will be limited to
    trim_url_limit characters.

    If nofollow is True, the URLs in link text will get a rel="nofollow" attribute.
    """
    trim_url = lambda x, limit=trim_url_limit: limit is not None and (x[:limit] + (len(x) >=limit and '...' or ''))  or x
    words = word_split_re.split(text)
    nofollow_attr = nofollow and ' rel="nofollow"' or ''
    for i, word in enumerate(words):
        match = punctuation_re.match(word)
        if match:
            lead, middle, trail = match.groups()
            if middle.startswith('www.') or ('@' not in middle and not middle.startswith('http://') and not middle.startswith('https://') and \
                    len(middle) > 0 and middle[0] in string.letters + string.digits and \
                    (middle.endswith('.org') or middle.endswith('.net') or middle.endswith('.com'))):
                middle = '<a href="http://%s"%s target="_blank">%s</a>' % (middle, nofollow_attr, trim_url(middle))
            if middle.startswith('http://') or middle.startswith('https://'):
                middle = '<a href="%s"%s target="_blank">%s</a>' % (middle, nofollow_attr, trim_url(middle))
            if '@' in middle and not middle.startswith('www.') and not ':' in middle \
                and simple_email_re.match(middle):
                middle = '<a href="mailto:%s">%s</a>' % (middle, middle)
            if lead + middle + trail != word:
                words[i] = lead + middle + trail
    return ''.join(words)

# auto convert *.sinaimg.cn/*/*.jpg and bcs.baidu.com/*.jpg links to image tags
def sinaimg(value):
    imgs = re.findall('(http://ww[0-9]{1}.sinaimg.cn/[a-zA-Z0-9]+/[a-zA-Z0-9]+.[a-z]{3})\s?', value)
    for img in imgs:
        value = value.replace(img, '<a href="' + img + '" target="_blank"><img src="' + img + '" class="imgly" border="0" /></a>')
    baidu_imgs = re.findall('(http://(bcs.duapp.com|img.xiachufang.com|i.xiachufang.com)/([a-zA-Z0-9\.\-\_\/]+).jpg)\s?', value)
    for img in baidu_imgs:
        value = value.replace(img[0], '<a href="' + img[0] + '" target="_blank"><img src="' + img[0] + '" class="imgly" border="0" /></a>')
    return value

# auto convert youtube.com links to player
def youtube(value):
    videos = re.findall('(http://www.youtube.com/watch\?v=[a-zA-Z0-9\-\_]+)\s?', value)
    if (len(videos) > 0):
        for video in videos:
            video_id = re.findall('http://www.youtube.com/watch\?v=([a-zA-Z0-9\-\_]+)', video)
            value = value.replace('http://www.youtube.com/watch?v=' + video_id[0], '<object width="100%" height="500"><param name="movie" value="http://www.youtube.com/v/' + video_id[0] + '?fs=1&amp;hl=en_US"></param><param name="allowFullScreen" value="true"></param><param name="allowscriptaccess" value="always"></param><embed src="http://www.youtube.com/v/' + video_id[0] + '?fs=1&amp;hl=en_US" type="application/x-shockwave-flash" allowscriptaccess="always" allowfullscreen="true" width="620" height="500"></embed></object>')
        return value
    else:
        return value

# auto convert tudou.com links to player
# example: http://www.tudou.com/programs/view/ro1Yt1S75bA/
def tudou(value):
    videos = re.findall('(http://www.tudou.com/programs/view/[a-zA-Z0-9\=]+/)\s?', value)
    # logging.error(value)
    # logging.error(videos)
    if (len(videos) > 0):
        for video in videos:
            video_id = re.findall('http://www.tudou.com/programs/view/([a-zA-Z0-9\=]+)/', video)
            value = value.replace('http://www.tudou.com/programs/view/' + video_id[0] + '/', '<embed src="http://www.tudou.com/v/' + video_id[0] + '/" quality="high" width="100%" height="420" align="middle" allowScriptAccess="sameDomain" type="application/x-shockwave-flash"></embed>')
        return value
    else:
        return value

# auto convert youku.com links to player
# example: http://v.youku.com/v_show/id_XMjA1MDU2NTY0.html
def youku(value):
    videos = re.findall('(http://v.youku.com/v_show/id_[a-zA-Z0-9\=]+.html)\s?', value)
    # logging.error(value)
    # logging.error(videos)
    if (len(videos) > 0):
        for video in videos:
            video_id = re.findall('http://v.youku.com/v_show/id_([a-zA-Z0-9\=]+).html', video)
            value = value.replace('http://v.youku.com/v_show/id_' + video_id[0] + '.html', '<embed src="http://player.youku.com/player.php/sid/' + video_id[0] + '/v.swf" quality="high" width="100%" height="420" align="middle" allowScriptAccess="sameDomain" type="application/x-shockwave-flash"></embed>')
        return value
    else:
        return value

# auto convert xiami.com links to player
# example: http://www.xiami.com/song/16024
def xiami(value):
    musics = re.findall('(http://www.xiami.com/song/[0-9]+)\s?', value)
    if (len(musics) > 0):
        for music in musics:
            music_id = re.findall('http://www.xiami.com/song/([0-9]+)', music)
            value = value.replace('http://www.xiami.com/song/' + music_id[0], '<embed src="http://www.xiami.com/widget/15289_' + music_id[0] + '/singlePlayer.swf" type="application/x-shockwave-flash" width="257" height="33" wmode="transparent"></embed>')
        return value
    else:
        return value


# via https://gist.github.com/dndn/859717
#更深层次的过滤，类似instapaper或者readitlater这种服务，很有意思的研究课题
##过滤HTML中的标签
#将HTML中标签等信息去掉
#@param htmlstr HTML字符串.
def filter_tags(htmlstr):
    #先过滤CDATA
    re_cdata=re.compile('//<!\[CDATA\[[^>]*//\]\]>',re.I) #匹配CDATA
    re_script=re.compile('<\s*script[^>]*>[^<]*<\s*/\s*script\s*>',re.I)#Script
    re_style=re.compile('<\s*style[^>]*>[^<]*<\s*/\s*style\s*>',re.I)#style
    re_br=re.compile('<br\s*?/?>')#处理换行
    re_h=re.compile('</?\w+[^>]*>')#HTML标签
    re_comment=re.compile('<!--[^>]*-->')#HTML注释
    s=re_cdata.sub('',htmlstr)#去掉CDATA
    s=re_script.sub('',s) #去掉SCRIPT
    s=re_style.sub('',s)#去掉style
    s=re_br.sub('\n',s)#将br转换为换行
    s=re_h.sub('',s) #去掉HTML 标签
    s=re_comment.sub('',s)#去掉HTML注释
    #去掉多余的空行
    blank_line=re.compile('\n+')
    s=blank_line.sub('\n',s)
    s=replaceCharEntity(s)#替换实体
    return s

##替换常用HTML字符实体.
#使用正常的字符替换HTML中特殊的字符实体.
#你可以添加新的实体字符到CHAR_ENTITIES中,处理更多HTML字符实体.
#@param htmlstr HTML字符串.
def replaceCharEntity(htmlstr):
    CHAR_ENTITIES={'nbsp':' ','160':' ',
                'lt':'<','60':'<',
                'gt':'>','62':'>',
                'amp':'&','38':'&',
                'quot':'"','34':'"',}
    
    re_charEntity=re.compile(r'&#?(?P<name>\w+);')
    sz=re_charEntity.search(htmlstr)
    while sz:
        entity=sz.group()#entity全称，如&gt;
        key=sz.group('name')#去除&;后entity,如&gt;为gt
        try:
            htmlstr=re_charEntity.sub(CHAR_ENTITIES[key],htmlstr,1)
            sz=re_charEntity.search(htmlstr)
        except KeyError:
            #以空串代替
            htmlstr=re_charEntity.sub('',htmlstr,1)
            sz=re_charEntity.search(htmlstr)
    return htmlstr

def repalce(s,re_exp,repl_string):
    return re_exp.sub(repl_string,s)
