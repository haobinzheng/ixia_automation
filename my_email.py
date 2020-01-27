import smtplib
Python_version = 3
if Python_version == 2:
  from email.MIMEMultipart import MIMEMultipart
  import email.mime.multipart
  from email.MIMEText import MIMEText
  from email.MIMEBase import MIMEBase
  from email import encoders
  from email.Utils import COMMASPACE, formatdate
  from email import Encoders
else:
  from email import encoders
  from email.message import Message
  from email.mime.audio import MIMEAudio
  from email.mime.base import MIMEBase
  from email.mime.image import MIMEImage
  from email.mime.multipart import MIMEMultipart
  from email.mime.text import MIMEText

COMMASPACE = ', '
# print(dir(email))
import os
import datetime


def send_Message():
  # cmd = """osascript<<END
  #   tell application "Messages"

  #   send "test imessage from python" to buddy "4088967681 #" of (service 1 whose service type is iMessage)

  #   end tell
  #   END
  #   """

  new_cmd = """ osascript -e
  'tell application "Messages"

    set targetBuddy to "+14088967681"
    set targetService to id of 1st service whose service type = iMessage


    set textMessage to 'test test again'

    set theBuddy to buddy targetBuddy of service id targetService
    send textMessage to theBuddy

  end tell'
  """
  cmd = "osascript my_message.app '{}'".format("test test test")
  print(new_cmd)
  os.system(cmd)


def send_email(user, pwd, recipient, subject, body):
  import smtplib

  FROM = user
  TO = recipient if isinstance(recipient, list) else [recipient]
  SUBJECT = subject
  TEXT = body

  # Prepare actual message
  message = """From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
  try:
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.ehlo()
    server.starttls()
    server.login(user, pwd)
    server.sendmail(FROM, TO, message)
    server.close()
    print('Successfully sent mail for {}'.format(subject))
    return True
  except Exception as e:
    print("failed to send mail for {}".format(subject))
    return False


def sendMail(to, subject, text, files=[]):
  assert type(to) == list
  assert type(files) == list

  smtpUser = 'haobin.zheng08'
  smtpPass = 'Shenghuo2014+'

  msg = MIMEMultipart()
  msg['From'] = smtpUser
  msg['To'] = COMMASPACE.join(to)
  #msg['Date'] = formatdate(localtime=True)
  msg['Date'] = datetime.date.today().strftime('%Y %b %d')
  msg['Subject'] = subject

  msg.attach(MIMEText(text))

  for file in files:
    part = MIMEBase('application', "octet-stream")
    part.set_payload(open(file, "rb").read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename="%s"'
                    % os.path.basename(file))
    msg.attach(part)

  server = smtplib.SMTP('smtp.gmail.com:587')
  server.ehlo_or_helo_if_needed()
  server.starttls()
  server.ehlo_or_helo_if_needed()
  server.login(smtpUser, smtpPass)
  server.sendmail(smtpUser, to, msg.as_string())

  print('Email with file attachment is sent out!')

  server.quit()


if __name__ == "__main__":
  # send_Message()
  # exit()
  user = 'haobin.zheng08@gmail.com'
  pwd = 'Shenghuo2014+'
  to = ['haobin.zheng08@gmail.com', 'hbz.zheng@gmail.com']
  body = "Hey, what's up?\n\n- You"
  subject = 'OMG Super Important Message'
  #send_email(user, pwd, to, subject, body)
  #print("first method works, now tring the 2nd one with file attachment")
  # a new approach
  smtpUser = 'haobin.zheng08'
  smtpPass = 'Shenghuo2014+'

  toAdd = 'haobin.zheng08@gmail.com'
  fromAdd = smtpUser

  today = datetime.date.today()

  subject = 'Data File 01 %s' % today.strftime('%Y %b %d')
  header = 'To :' + toAdd + '\n' + 'From : ' + fromAdd + '\n' + 'Subject : ' + subject + '\n'
  body = 'This is a data file on %s' % today.strftime('%Y %b %d')

  #attach = 'Data on %s.csv' % today.strftime('%Y-%m-%d')
  attach = 'stock_log.txt'

  # print header
  sendMail([toAdd], subject, body, [attach])
  # user = 'haobin.zheng08'
  # smtp_host = 'smtp.gmail.com'
  # smtp_port = 587
  # server = smtplib.SMTP()
  # server.connect(smtp_host, smtp_port)
  # server.ehlo()
  # server.starttls()
  # server.login(user, pwd)
  # fromaddr = input('Send mail by the name of: ')
  # tolist = input('To: ').split()
  # sub = input('Subject: ')

  # msg = email.MIMEMultipart.MIMEMultipart()
  # msg['From'] = fromaddr
  # msg['To'] = email.Utils.COMMASPACE.join(tolist)
  # msg['Subject'] = sub
  # msg.attach(MIMEText(input('Body: ')))
  # msg.attach(MIMEText('\nsent via python', 'plain'))
  # server.sendmail(user, tolist, msg.as_string())
