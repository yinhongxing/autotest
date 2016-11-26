#!/usr/bin/env python
# -*- coding:utf-8 -*-
import smtplib
from email.mime.text import MIMEText
from email.header import Header
subject = 'python email test'
mailto_list = ["yinhongxing@ablecloud.cn"]
mail_host = "smtp.163.com"
mail_user = "yinhongxing2016@163.com"
mail_pass = "ablecloud"
mail_postfix = "163.com"


def send_mail(to_list, sub, content):
    me = "auto_test" + "<" + mail_user + "@" + mail_postfix + ">"
    msg = MIMEText(content, _subtype='plain', _charset='utf-8')
    msg['Subject'] = sub
    msg['From'] = me
    msg['To'] = ";".join(to_list)
    # msg = MIMEText('hello', 'text', 'utf-8')
    # msg['Subject'] = Header(subject, 'utf-8')
    try:
        server = smtplib.SMTP()

        server.connect(mail_host)
        #server.starttls()
        #server.set_debuglevel(1)
        server.login(mail_user, mail_pass)
        server.sendmail(me, to_list, msg.as_string())
        server.close()
        return True
    except Exception, e:
        print str(e)
        return False


# if __name__ == '__main__':
#     if send_mail(mailto_list, "注册成功", "已经注册成功！"):
#         print "send success"
#     else:
#         print "send fail"