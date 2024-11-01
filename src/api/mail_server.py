from datetime import datetime
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

from config import get_settings


settings = get_settings()
sended = False


def send_email(toAddr: str | list[str], content: str, subject: str = ""):
    """发送邮件

    Args:
        toAddr (str | list[str]): 收件人邮箱地址
        content (str): 邮件内容
    """
    global sended
    if sended:
        return
    sended = True
    if isinstance(toAddr, str):
        toAddr = [toAddr]

    # 创建一个MIMEMultipart对象
    msg = MIMEMultipart()
    msg["From"] = f"{settings.mail_nick_name}<{settings.mail_username}>"
    msg["Reply-To"] = "1636700244@qq.com"
    msg["To"] = ",".join(toAddr)
    msg["Date"] = Header(
        datetime.now().strftime("%a, %d %b %Y %H:%M:%S %z"), "utf-8"
    ).encode()
    msg["Subject"] = Header(subject, "utf-8").encode()
    msg.attach(MIMEText(content, "plain", "utf-8"))

    smtpObj = smtplib.SMTP_SSL(
        settings.mail_smtp_server, settings.mail_smtp_port, timeout=10
    )
    smtpObj.login(settings.mail_username, settings.mail_password)
    smtpObj.sendmail(settings.mail_username, toAddr, msg.as_string())

    smtpObj.quit()
