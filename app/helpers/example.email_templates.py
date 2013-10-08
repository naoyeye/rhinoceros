#!/usr/bin/env python
# coding: utf-8

# TODO:
# - this should be moved to a DB.

import web
import config
from email.Header import Header  

web.config.smtp_server = 'smtp.gmail.com'
web.config.smtp_port = 587
#smtp_username = 'cookbook@gmail.com'
web.config.smtp_username = 'email'
web.config.smtp_password = 'pwd'
web.config.smtp_starttls = True

# _from = config.mail_sender
_from = 'Biu <help@biubiubiubiu.com>'
# _from = None

bcc = '' #暗抄送 # 
xxx = 'xxx <xxx@gmail.com>'
admin_list = ['xxx@gmail.com', 'yyy@gmail.com']

#=========

msg_forgot = \
'''$def with (user, token, ua, ip, tm)

Hi $user.nickname,

我们的系统收到一个请求，说你希望通过电子邮件重新设置你在 %s 的密码。你可以点击下面的链接开始重设密码：

http://%s/account/reset/$token

如果这个请求不是由你发起的，那没问题，你不用担心，你可以安全地忽略这封邮件。

如果你有任何疑问，可以回复这封邮件向我们提问。

- %s 开发团队

p.s. 作为安全备注，这次密码找回请求是由 IP 地址 $ip 使用浏览器 $ua 在 $tm 发起的

''' % (config.site_name, config.site_domain, config.site_name)

#=========

msg_create_account = \
'''$def with (email, token)

很高兴你能注册 %s! 为了验证注册邮箱的真实性，防止有人恶意注册，以及万一以后你忘记密码（希望这不会发生）时需要用此邮箱来找回密码，我们给你发了这封邮件，请点击下面的链接来确认这是你的邮箱。

http://%s/account/confirm/$token

该链接地址24小时内打开有效。

如果您错误地收到了此电子邮件，您无需执行任何操作，此注册帐号将不会启动。

如果你有任何疑问，可以回复这封邮件向我们提问。

- %s 开发团队

''' % (config.site_name, config.site_domain, config.site_name)

#=========

msg_change_email = \
'''$def with (email, token)

你在 Biu 更改了邮箱，为了验证新邮箱的真实性，我们给你发了这封邮件，请点击下面的链接来确认这是你的邮箱。

http://www.biubiubiubiu.com/welcome/confirm_email/$token

该链接地址24小时内打开有效。

如果您错误地收到了此电子邮件，您无需执行任何操作。

如果你有任何疑问，可以回复这封邮件向我们提问。

- Biu

'''

#=========

msg_change_pwd = \
'''$def with (email, user, ua, ip, tm)
<html>
<body>
<style>
body{font-size:12px;font-family: 'Helvetica Neue',Arial,'Liberation Sans',FreeSans,'Hiragino Sans GB',sans-serif;}
</style>
<h1>Hi, $user.nickname</h1>

你在 <a href="http://%s">%s</a> 的帐号 <a href="http://%s/member/$user.username">$user.username</a> 刚刚修改了密码，为了确保是本人操作，我们给你发了这封邮件。

如果不是你本人修改的密码，可以回复此邮件联系我们的工作人员。

<p style="color:#666">p.s. 作为安全备注，这次密码找回请求是由 IP 地址 $ip 使用浏览器 $ua 在 $tm 发起的</p>

- %s 开发团队
</body>
</html>

''' % (config.site_domain, config.site_name, config.site_domain, config.site_name)

#=========

apply_for_permission_temp = \
'''$def with (apply_user, apply_time)
<html>
<body>
<meta http-equiv="content-type" content="text/html; charset=utf-8" />
<style>
body{font-size:12px;font-family: 'Helvetica Neue',Arial,'Liberation Sans',FreeSans,'Hiragino Sans GB',sans-serif;background:#fff;}
</style>
<h1 style="font-size:20px;text-align:center;background:#333332;color:#fff;padding:10px 0;margin-bottom:10px;">用户 $apply_user.nickname 希望能申请开通权限</h1>
<div style="text-align:center"><a href="http://www.doubam.com/people/$apply_user.username"><img style="border-radius:50%" src="$apply_user.avatarPath"/></a></div>

<p>Ta的豆瓣地址为： http://www.douban.com/people/$apply_user.username</p>
<p>申请时间 $apply_time</p>
<p>你可以登录Biu管理后台访问 http://www.biubiubiubiu.com/admin/apply_for_permission 来处理。</p>
—— Biu
</body>
</html>
'''

#=========

apply_failed = \
'''$def with (apply_user)
<div marginwidth="0" marginheight="0" style="min-width:600px;margin:0 auto;padding:39px;font-family:'Helvetica Neue',Helvetica,Arial,Sans-serif;font-size:13px;line-height:22px;background-color:#d8d8d8"><div class="adM">
  </div><table width="100%" cellspacing="0" cellpadding="0" border="0" style="min-width:700px;margin:0 auto;font-family:'Helvetica Neue',Helvetica,Arial,Sans-serif,'Hiragino Sans GB';font-size:13px;line-height:22px">
    <tbody>
      <tr>
        <td>
          <table width="686" height="710" cellspacing="0" cellpadding="0" border="0" align="center" style="margin:0 auto">
            <tbody>
              <tr><td background="http://share.han.im/email_01.jpg" style="width:686px;min-height:710px">
                <table width="686" height="710" cellspacing="0" cellpadding="0" border="0">
                  <tbody>
                    <tr height="145">
                      <td align="right" style="vertical-align:middle;padding-right:98px">
                        <a target="_blank" href="http://www.biubiubiubiu.com" style="display:inline-block;font-weight:normal;text-decoration:none;font-size:14px;color:#eee;width:50px;font-size:13px">去Biu</a>
                      </td>
                    </tr>
                    <tr height="100">
                      <td colspan="3" style="padding-left:92px;vertical-align:middle;color:whiteSmoke;font:22px/36px 'Helvetica Neue',Helvetica,Arial,Sans-serif;font-weight:bold">
                        <div>
                          $apply_user.nickname :<br/>
                          很抱歉，您提交的申请未能符合我们的要求。:(<br/>
                          <p style="font-size:13px;margin:0;padding:0;">您可以试试在申请理由中提交更多有关于你的信息以供参考，如个人博客、网站、Flickr等。</p>
                        </div>
                      </td>
                    </tr>
                    <tr height="216" align="center">
                      <td>
                          <div style="padding-bottom:30px;line-height:27px"><a target="_blank" href="http://www.biubiubiubiu.com/" style="font-weight:normal;text-decoration:none;color:#eee;font-size:22px">访问Biu</a></div>
                        <div style="line-height:15px"><span style="color:#eee;font-size:13px;line-height:15px;font-weight:normal">阅读<span style="padding:0 3px">•</span>观看<span style="padding:0 3px">•</span>思考<span style="padding:0 3px">•</span>交流</span></div>
                      </td>
                    </tr>
                    <tr></tr>
                  </tbody>
                </table>
              </td>
            </tr></tbody>
          </table>
        </td>
      </tr>
      <tr>
         <td align="center">
          <table width="100%" cellspacing="0" cellpadding="0" border="0">
              <tbody>
                  <tr>
                      <td align="center">
                          <div style="text-align:center;padding:15px 0 100px 0;margin:0 auto;width:500px;color:#999;font-size:12px;line-height:20px">Biu &copy; 2013</div>
                      </td>
                  </tr>
              </tbody>
          </table>
        </td>
      </tr>
    </tbody>
  </table><div class="yj6qo"></div><div class="adL">
</div></div>
'''
#===========
apply_success = \
'''$def with (apply_user)
<div marginwidth="0" marginheight="0" style="min-width:600px;margin:0 auto;padding:39px;font-family:'Helvetica Neue',Helvetica,Arial,Sans-serif;font-size:13px;line-height:22px;background-color:#d8d8d8"><div class="adM">
  </div><table width="100%" cellspacing="0" cellpadding="0" border="0" style="min-width:700px;margin:0 auto;font-family:'Helvetica Neue',Helvetica,Arial,Sans-serif,'Hiragino Sans GB';font-size:13px;line-height:22px">
    <tbody>
      <tr>
        <td>
          <table width="686" height="710" cellspacing="0" cellpadding="0" border="0" align="center" style="margin:0 auto">
            <tbody>
              <tr><td background="http://share.han.im/email_01.jpg" style="width:686px;min-height:710px">
                <table width="686" height="710" cellspacing="0" cellpadding="0" border="0">
                  <tbody>
                    <tr height="145">
                      <td align="right" style="vertical-align:middle;padding-right:98px">
                        <a target="_blank" href="http://www.biubiubiubiu.com" style="display:inline-block;font-weight:normal;text-decoration:none;font-size:14px;color:#eee;width:50px;font-size:13px">去Biu</a>
                      </td>
                    </tr>
                    <tr height="100">
                      <td colspan="3" style="padding-left:92px;vertical-align:middle;color:whiteSmoke;font:22px/36px 'Helvetica Neue',Helvetica,Arial,Sans-serif;font-weight:bold">
                        <div>
                          $apply_user.nickname :<br/>
                          太棒了！您提交的申请已经通过！<br/>
                          <p style="font-size:22px;margin:0;padding:0;">您现在可以访问Biu来创建话题、发表片段了。</p>
                        </div>
                      </td>
                    </tr>
                    <tr height="216" align="center">
                      <td>
                          <div style="padding-bottom:30px;line-height:27px"><a target="_blank" href="http://www.biubiubiubiu.com/" style="font-weight:normal;text-decoration:none;color:#eee;font-size:22px">访问Biu</a></div>
                        <div style="line-height:15px"><span style="color:#eee;font-size:13px;line-height:15px;font-weight:normal">阅读<span style="padding:0 3px">•</span>观看<span style="padding:0 3px">•</span>思考<span style="padding:0 3px">•</span>交流</span></div>
                      </td>
                    </tr>
                    <tr></tr>
                  </tbody>
                </table>
              </td>
            </tr></tbody>
          </table>
        </td>
      </tr>
      <tr>
         <td align="center">
          <table width="100%" cellspacing="0" cellpadding="0" border="0">
              <tbody>
                  <tr>
                      <td align="center">
                          <div style="text-align:center;padding:15px 0 100px 0;margin:0 auto;width:500px;color:#999;font-size:12px;line-height:20px">Biu &copy; 2013</div>
                      </td>
                  </tr>
              </tbody>
          </table>
        </td>
      </tr>
    </tbody>
  </table><div class="yj6qo"></div><div class="adL">
</div></div>
'''
#=========

new_user_email = \
'''$def with (user, token)

<div marginwidth="0" marginheight="0" style="min-width:600px;margin:0 auto;padding:39px;font-family:'Helvetica Neue',Helvetica,Arial,Sans-serif;font-size:13px;line-height:22px;background-color:#d8d8d8">
<table width="100%" cellspacing="0" cellpadding="0" border="0" style="min-width:700px;margin:0 auto;font-family:'Helvetica Neue',Helvetica,Arial,Sans-serif,'Hiragino Sans GB';font-size:13px;line-height:22px">
    <tbody>
      <tr>
        <td>
          <table width="686" height="710" cellspacing="0" cellpadding="0" border="0" align="center" style="margin:0 auto">
            <tbody>
              <tr><td background="http://share.han.im/email_02.jpg" style="width:686px;min-height:710px">
                <table width="686" height="710" cellspacing="0" cellpadding="0" border="0">
                  <tbody>
                    <tr height="145">
                      <td></td>
                    </tr>
                    <tr height="100">
                      <td colspan="3" style="padding:0 92px;vertical-align:middle;color:whiteSmoke;font:12px/1.78 'Helvetica Neue',Helvetica,Arial,Sans-serif;">
                        <div>
                          <span style="font-size:22px;line-height:40px;font-weight:bold">$user.nickname :</span><br/><br/>
                          很高兴你能注册 Biu ! 为了验证邮箱的真实性，防止有人恶意注册，以及方便你收到别人对你的回复，我们给你发了这封邮件，请点击下面的链接来确认这是你的邮箱。<br/>
                          <p style="font-size:12px;margin:10px 0 0 0;font-weight:normal;padding:0;color:#fff">
                            http://www.biubiubiubiu.com/welcome/confirm_email/$token</p>
                          <p style="line-height:1.78">
                            如果上面的链接无法点击，请复制到地址栏中打开。<br/>
                            该链接地址24小时内打开有效。<br/>
                            如果您错误地收到了此电子邮件，您无需执行任何操作，此注册帐号将不会启动。<br/>
                            如果你有任何疑问，可以回复这封邮件向我们提问。</p>
                        </div>
                      </td>
                    </tr>
                    <tr height="216" align="center">
                      <td>
                          <div style="padding-bottom:30px;font-size:26px;color:#ccc;line-height:27px">Biu</div>
                        <div style="line-height:15px"><span style="color:#ccc;font-size:13px;line-height:15px;font-weight:normal">阅读<span style="padding:0 3px">•</span>观看<span style="padding:0 3px">•</span>思考<span style="padding:0 3px">•</span>交流</span></div>
                      </td>
                    </tr>
                    <tr></tr>
                  </tbody>
                </table>
              </td>
            </tr></tbody>
          </table>
        </td>
      </tr>
      <tr>
         <td align="center">
          <table width="100%" cellspacing="0" cellpadding="0" border="0">
              <tbody>
                  <tr>
                      <td align="center">
                          <div style="text-align:center;padding:15px 0 100px 0;margin:0 auto;width:500px;color:#999;font-size:12px;line-height:20px">Biu &copy; 2013</div>
                      </td>
                  </tr>
              </tbody>
          </table>
        </td>
      </tr>
    </tbody>
</table>
</div>

'''
#=========

send_feedback_tmp = \
'''$def with (user, content)
<html>
<body>
<meta http-equiv="content-type" content="text/html; charset=utf-8" />
<style>
body{font-size:12px;font-family: 'Helvetica Neue',Arial,'Liberation Sans',FreeSans,'Hiragino Sans GB',sans-serif;background:#fff;}
</style>
<h1 style="font-size:20px;text-align:center;background:#333332;color:#fff;padding:10px 0;margin-bottom:10px;">用户 $user.nickname 提交了新的反馈</h1>
<div style="text-align:center"><a href="http://www.doubam.com/people/$user.username"><img style="border-radius:50%" src="$user.avatarPath"/></a></div>

<p>Ta的豆瓣地址为： http://www.douban.com/people/$user.username</p>
<p>反馈内容：</p> 
<blockquote>$content</blockquote>
<p>你可以登录Biu管理后台访问 http://www.biubiubiubiu.com/admin/feedback 来处理。</p>
—— Biu
</body>
</html>
'''

#=========

someone_like_ur_post_notification = \
'''$def with (user, author, post)
<html>
<body>
<meta http-equiv="content-type" content="text/html; charset=utf-8" />
<style>
body{font-size:12px;font-family: 'Helvetica Neue',Arial,'Liberation Sans',FreeSans,'Hiragino Sans GB',sans-serif;background:#fff;}
</style>
$if post.postTitle == '':
    $ title = post.postCaption
$else:
    $ title = post.postTitle
Hi，$author.nickname :
<a href="http://www.biubiubiubiu.com/member/$user.username">
    <img src="$user.avatarPath">
</a>
<a href="http://www.biubiubiubiu.com/member/$user.username">$user.nickname </a>

喜欢了你的片段 <a href="http://www.biubiubiubiu.com/post/$post.id?ntf_type=2#action_block">$title</a>

—— Biu
</body>
</html>
'''

#=========

someone_comment_ur_post_notification = \
'''$def with (user, author, post)
<html>
<body>
<meta http-equiv="content-type" content="text/html; charset=utf-8" />
<style>
body{font-size:12px;font-family: 'Helvetica Neue',Arial,'Liberation Sans',FreeSans,'Hiragino Sans GB',sans-serif;background:#fff;}
</style>
$if post.postTitle == '':
    $ title = post.postCaption
$else:
    $ title = post.postTitle
Hi，$author.nickname :
<a href="http://www.biubiubiubiu.com/member/$user.username">
    <img src="$user.avatarPath">
</a>
<a href="http://www.biubiubiubiu.com/member/$user.username">$user.nickname </a>

评论了你的片段 <a href="http://www.biubiubiubiu.com/post/$post.id?ntf_type=1#postCommentForm">$title</a>

—— Biu
</body>
</html>
'''

#=========

someone_creat_new_post_notification = \
'''$def with (user, nodeAuthor, node, post)
<html>
<body>
<meta http-equiv="content-type" content="text/html; charset=utf-8" />
<style>
body{font-size:12px;font-family: 'Helvetica Neue',Arial,'Liberation Sans',FreeSans,'Hiragino Sans GB',sans-serif;background:#fff;}
</style>
$if post.postTitle == '':
    $ title = post.postCaption
$else:
    $ title = post.postTitle
Hi，$nodeAuthor.nickname :
<a href="http://www.biubiubiubiu.com/member/$user.username">
    <img src="$user.avatarPath">
</a>
<a href="http://www.biubiubiubiu.com/member/$user.username">$user.nickname </a>

在你创建的话题 <a href="http://www.biubiubiubiu.com/node/$node.id">$node.nodeName</a> 中发布了新片段 <a href="http://www.biubiubiubiu.com/post/$post.id">$title</a>

—— Biu
</body>
</html>
'''

def forgot(user, token, ua, ip, tm):
    subject = '找回密码'
    msg = web.template.Template(msg_forgot)(user, token, ua, ip, tm)
    #web.sendmail(_from, user.email, subject, msg, bcc=bcc)
    web.sendmail(_from, user.email, subject, msg, bcc=bcc)

def create_account(email, token):
    subject = '欢迎注册'+ config.site_name +'!'
    msg = web.template.Template(msg_create_account)(email, token)
    web.sendmail(_from, email, subject, msg, bcc=bcc)

def change_email(email, token):
    subject = 'Please verify your e-mail address - Biu'
    msg = web.template.Template(msg_change_email)(email, token)
    web.sendmail(_from, email, subject, msg, bcc=bcc)

def change_pwd(email, user, ua, ip, tm):
    subject = '你在' + config.site_name + '的密码已修改'
    msg = web.template.Template(msg_change_pwd)(email, user, ua, ip, tm)
    msg['subject'] = Header(subject, 'utf-8') 
    web.sendmail(_from, email, subject, msg, headers=({'Content-Type':'text/html;charset=utf-8','User-Agent': 'webpy.sendmail', 'X-Mailer': 'webpy.sendmail',}), bcc=bcc)

#用户权限申请 给管理员们发送提醒邮件
def apply_for_permission(apply_user, apply_time, email):
    subject =  'There is a new apply from Biu'
    msg = web.template.Template(apply_for_permission_temp)(apply_user, apply_time)
    msg['subject'] = Header(subject, 'utf-8') 
    admin_list = ['xxx@gmail.com', 'xxx@gmail.com']
    web.sendmail(_from, admin_list, subject, msg, headers=({'Content-Type':'text/html;charset=utf-8','User-Agent': 'webpy.sendmail', 'X-Mailer': 'webpy.sendmail',}))

#发送管理员处理后的申请结果邮件 - 通过
def email_to_user_for_apply_success(apply_user, apply_email):
    subject = 'Yeah! your application has successfully passed! - Biu'
    msg = web.template.Template(apply_success)(apply_user)
    msg['subject'] = Header(subject, 'utf-8') 
    web.sendmail(_from, apply_email, subject, msg, headers=({'Content-Type':'text/html;charset=utf-8','User-Agent': 'webpy.sendmail', 'X-Mailer': 'webpy.sendmail',}), bcc=ihanjiyun)

#发送管理员处理后的申请结果邮件 - 未通过u
def email_to_user_for_apply_fail(apply_user, apply_email):
    subject = "I'm sorry your application wasn't accepted - Biu"
    msg = web.template.Template(apply_failed)(apply_user)
    msg['subject'] = Header(subject, 'utf-8') 
    web.sendmail(_from, apply_email, subject, msg, headers=({'Content-Type':'text/html;charset=utf-8','User-Agent': 'webpy.sendmail', 'X-Mailer': 'webpy.sendmail',}), bcc=ihanjiyun)

#新用户登记邮箱 发送激活邮件
def msg_new_user_email(user, email, token):
    subject = "Welcome to Biu!"
    msg = web.template.Template(new_user_email)(user, token)
    msg['subject'] = Header(subject, 'utf-8') 
    web.sendmail(_from, email, subject, msg, headers=({'Content-Type':'text/html;charset=utf-8','X-Mailer': 'ZuckMail [version 1.00]'}), bcc=ihanjiyun)

#用户反馈
def send_feedback(user, content):
    subject = "Someone submitted a new feedback"
    msg = web.template.Template(send_feedback_tmp)(user, content)
    msg['subject'] = Header(subject, 'utf-8') 
    web.sendmail(_from, xxx, subject, msg, headers=({'Content-Type':'text/html;charset=utf-8','User-Agent': 'webpy.sendmail', 'X-Mailer': 'webpy.sendmail',}))

#用户提醒邮件 - 喜欢
def someone_like_ur_post(user, author, post):
    subject = "Some people like the article you published - Biu"
    msg = web.template.Template(someone_like_ur_post_notification)(user, author, post)
    msg['subject'] = Header(subject, 'utf-8') 
    web.sendmail(_from, author.email, subject, msg, headers=({'Content-Type':'text/html;charset=utf-8','User-Agent': 'webpy.sendmail', 'X-Mailer': 'webpy.sendmail',}))

#用户提醒邮件 - 评论
def someone_comment_ur_post(user, author, post):
    subject = "Some people have commented on your articles - Biu"
    msg = web.template.Template(someone_comment_ur_post_notification)(user, author, post)
    msg['subject'] = Header(subject, 'utf-8') 
    web.sendmail(_from, author.email, subject, msg, headers=({'Content-Type':'text/html;charset=utf-8','User-Agent': 'webpy.sendmail', 'X-Mailer': 'webpy.sendmail',}))

#在话题中增加了新片段 提醒
def someone_creat_new_post(user, nodeAuthor, node, thisPost):
    subject = "Someone posted a new article in the topic you create - Biu"
    msg = web.template.Template(someone_creat_new_post_notification)(user, nodeAuthor, node, thisPost)
    msg['subject'] = Header(subject, 'utf-8') 
    web.sendmail(_from, nodeAuthor.email, subject, msg, headers=({'Content-Type':'text/html;charset=utf-8','User-Agent': 'webpy.sendmail', 'X-Mailer': 'webpy.sendmail',}))
