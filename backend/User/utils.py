from django.db.models import *
from User.models import *
from File.models import *
import jwt
import base64
import time
import string
import random
from random import Random
from datetime import datetime, timedelta
import requests
from document_management_system.settings import SECRET_KEY, TOKEN_EXPIRE



# 生成token
def getToken(userid, aud):
    stime = datetime.now()
    expire = stime + timedelta(seconds=TOKEN_EXPIRE)
    payload = {
        'userid':userid,
        'iat':int(time.mktime(stime.timetuple())),
        'exp':int(time.mktime(expire.timetuple()))
    }
    headers = {
        'alg': "HS256",  # 声明所使用的算法
        'typ':"JWT"
    }
    # print(payload)
    # print(datetime.fromtimestamp(payload['iat']))
    # print(datetime.fromtimestamp(payload['exp']))
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256', headers=headers)
    return token



# 随机生成token
def getRandomToken1(length):
    length_r = length
    token = ''
    chars = 'qwertyuiopasdfghjklzxcvbnmMNBVCXZASDFGHJKLQWERTYUIOP0123456789'
    random = Random()
    for i in range(length_r):
        token += chars[random.randint(0, len(chars) - 1)]
    return token


# 第二种随机生成Token的方法
def getRandomToken2(length):
    return ''.join(random.sample(string.ascii_letters + string.digits, length))



# 清理一天前的邮箱验证码
def cleanInvalidVerificationCode():
    invalidVerificationCode = EmailVerificationCode.objects.filter(expire__lt=datetime.now() - timedelta(days=1))
    invalidVerificationCode.delete()



# 获取人脸识别的access_token
def getAccessToken():
    # client_id 为官网获取的AK， client_secret 为官网获取的SK
    host = "https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=s9GfTzj177GHIWX0hEVvX1iG&client_secret=eRGK2OXkKjYMsr5wlPHnulq7Ha98zQ0k"
    response = requests.get(host)
    print(response)
    if response:
        return response.json()['access_token']





















