import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header


def send(log: str, password: str, let_html: str, topic: str, name: bool, surname: bool, birthday: bool) -> bool:
    regxp = '(@\w+.\w+)'
    mail_server = re.findall(regxp, log)
    mail_server = str(mail_server)
    mail_server = mail_server.replace('[', '').replace(']', '').replace('\'', '')

    if mail_server == '@gmail.com':
        mailsender = smtplib.SMTP('smtp.gmail.com', 587)
    elif mail_server == '@yandex.ru':
        mailsender = smtplib.SMTP('smtp.yandex.ru', 587)
    elif mail_server == '@mail.ru':
        mailsender = smtplib.SMTP('smtp.mail.ru', 587)
    elif mail_server == '@outlook.com':
        mailsender = smtplib.SMTP('smtp.outlook.com', 587)
    else:
        print('Неизвестный сервер')
        return False

    mailsender.starttls()
    mailsender.login(log, password)
    msg = MIMEMultipart('alternative')
    msg['Subject'] = Header(topic, 'utf-8')
    msg['From'] = log

    with open('recipient_list.txt', 'r', encoding='utf8') as f:
        # в строке: адрес имя фамилия дата рождения
        for data in f:
            data = data.replace('[', '').replace('\'', '').replace(']', '').replace('\n', '')
            mail, person_name, person_surname, person_birthday = data.split()
            msg['To'] = mail

            if name:
                let_html = let_html.replace('(name)', person_name)
            if surname:
                let_html = let_html.replace('(surname)', person_surname)
            if birthday:
                let_html = let_html.replace('(birthday)', person_birthday)
            let_html = let_html.replace('(mail)', mail)
            part = MIMEText(let_html, 'html')
            msg.attach(part)
            mailsender.sendmail(log, mail, msg.as_string())
            mailsender.quit()
    return True


