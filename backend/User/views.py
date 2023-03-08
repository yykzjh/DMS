from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, FileResponse, StreamingHttpResponse
from django.conf import settings
from django.core import paginator
from django.db.models import *
import os
import datetime
import json
import re
import time
import urllib
import base64
import shutil
import uuid
import requests
import pandas as pd
from User.models import *
from File.models import *
import jwt
from django.core.mail import send_mail, send_mass_mail, EmailMultiAlternatives
from document_management_system.settings import SECRET_KEY, AVATAR_BASE_DIR, DEFAULT_FROM_EMAIL
from File.utils import setOverTime
from User.utils import (getToken, getRandomToken1, getRandomToken2, cleanInvalidVerificationCode, 
    getAccessToken)



def index(request):
    return HttpResponse("user index!")



def validate(request):
    setOverTime()
    token = request.GET.get('token')
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return JsonResponse({
            'errcode':0,
            'errmsg':'ok'
        })
        print(ok)
    except Exception as e:
        # 如果 jwt 被篡改过; 或者算法不正确; 如果设置有效时间, 过了有效期; 或者密钥不相同; 都会抛出相应的异常
        print(e)
        return JsonResponse({
            'errcode':1,
            'errmsg':str(e)
        })



def login(request):
    setOverTime()
    data = json.loads(request.body.decode("utf-8").replace("'", "\""))
    userid = data.get("userid")
    pwd = data.get("pwd")
    remote_addr = request.META.get("REMOTE_ADDR")

    try:
        userObj = User.objects.get(Q(Q(_id=userid)|Q(phone=userid)|Q(email=userid))&Q(password=pwd)&Q(is_active=True))
    except:
        return JsonResponse({
            'errcode':1,
            'errmsg':"can not find this user!"
        })
    
    token = getToken(userObj._id, remote_addr)
    permissionList = list(userObj.role.permissions.values_list("_id", flat=True))
    print(permissionList)

    if 1 not in permissionList:
        return JsonResponse({
            'errcode': 1,
            'errmsg': "you don't have login permission!"
        })

    user = {
        "userid": userObj._id,
        "role_id": userObj.role._id,
        'username':userObj.name,
        "permissions" :permissionList, 
        "token": token
    }
    return JsonResponse({
        'errcode':0,
        'errmsg':"ok",
        'user': user
    })



def getNewPermitUser(request):
    userid = request.GET.get("userid")

    try:
        userObj = User.objects.annotate(id=F('_id')).values("id", "name").get(id=userid, is_active=True)
    except:
        return JsonResponse({
            'errcode':1,
            'errmsg':"can not find this user!"
        })
    return JsonResponse({
        'errcode':0,
        'errmsg':"ok!",
        "user":userObj
    })



def getUserBasicInfo(request):
    userid = request.GET.get("userid")

    try:
        userObj = User.objects.get(_id=userid, is_active=True)
    except:
        return JsonResponse({
            'errcode':1,
            'errmsg': "can not find this user!"
        })
    
    userInfoForm = dict(
        userid = userObj._id,
        name = userObj.name,
        dept = userObj.dept.name,
        role = userObj.role.name,
        borrowCount = userObj.borrow_count,
        phone = userObj.phone,
        email = userObj.email,
        wechat = userObj.wechat
    )
    return JsonResponse({
        'errcode': 0,
        'errmsg': "ok",
        'userInfoForm': userInfoForm
    })



def editUserBasicInfo(request):
    userid = request.GET.get("userid")
    name = request.GET.get("name")

    try:
        userObj = User.objects.get(_id=userid, is_active=True)
    except:
        return JsonResponse({
            'errcode': 1,
            'errmsg': "can not find your account!"
        })
    
    userObj.name = name
    userObj.save()
    return JsonResponse({
        'errcode': 0,
        'errmsg': "ok"
    })



def getAvatar(request):
    userid = request.GET.get("userid")

    try:
        userObj = User.objects.get(_id=userid, is_active=True)
    except:
        return JsonResponse({
            'errcode':1,
            'errmsg': "can not find this user!"
        })
    
    if userObj.avatar_url == None or userObj.avatar_url == "":
        with open(os.path.join(AVATAR_BASE_DIR, "default-avatar.jpg"), "rb") as f:
            image_data = f.read()
        return HttpResponse(image_data)
    
    else:
        with open(os.path.join(AVATAR_BASE_DIR, userObj.avatar_url), "rb") as f:
            image_data = f.read()
        return HttpResponse(image_data)



def updateAvatar(request):
    data = json.loads(request.body.decode("utf-8").replace("'", "\""))
    avatar_base64 = data.get("avatar")
    userid = data.get("userid")

    # 处理图像数据
    avatarExt = avatar_base64.split(',')[0].split(':')[1].split(';')[0].split("/")[1]
    avatar_base64_data = avatar_base64.split(",")[1]
    avatar = base64.b64decode(avatar_base64_data)
    print(avatarExt)

    try:
        userObj = User.objects.get(_id=userid, is_active=True)
    except:
        return JsonResponse({
            'errcode': 1,
            'errmsg': "can not find your account!"
        })
    
    # 删除原头像
    if userObj.avatar_url is not None and userObj.avatar_url != "":
        oldAvatarFolder = os.path.join(AVATAR_BASE_DIR, userObj.avatar_url.split("\\")[0])
        print(oldAvatarFolder)
        shutil.rmtree(oldAvatarFolder)
    
    new_avatar_folder_name = ''.join(str(uuid.uuid3(uuid.NAMESPACE_DNS, userid)).split('-'))
    new_avatar_folder_full_path = os.path.join(AVATAR_BASE_DIR, new_avatar_folder_name)
    new_avatar_full_path = os.path.join(AVATAR_BASE_DIR, new_avatar_folder_name, userObj._id + "." + avatarExt)
    new_avatar_url = os.path.join(new_avatar_folder_name, userObj._id + "." + avatarExt)
    print(new_avatar_full_path)
    print(new_avatar_url)

    if not os.path.exists(new_avatar_folder_full_path):
        os.makedirs(new_avatar_folder_full_path, 755)
    with open(new_avatar_full_path, "wb") as f:
        f.write(avatar)
    
    userObj.avatar_url = new_avatar_url
    userObj.save()

    return JsonResponse({
        'errcode':0,
        'errmsg':"ok"
    })



def getUserSecurityInfo(request):
    userid = request.GET.get("userid")

    try:
        userObj = User.objects.get(_id=userid, is_active=True)
    except:
        return JsonResponse({
            'errcode':1,
            'errmsg': "can not find this user!"
        })
    
    res = {
        'password': userObj.password,
        'phone': userObj.phone,
        'email': userObj.email,
        'wechat': userObj.wechat,
        'faceVerification': userObj.face_verification,
    }

    return JsonResponse({
        'errcode':0,
        'errmsg':"ok",
        'res':res
    })



def modifyPassword(request):
    userid = request.GET.get("userid")
    newPassword = request.GET.get("newPassword")

    try:
        userObj = User.objects.get(_id=userid, is_active=True)
    except:
        return JsonResponse({
            'errcode':1,
            'errmsg': "can not find your account!"
        })
    
    if newPassword == userObj.password:
        return JsonResponse({
            'errcode': 1,
            'errmsg': "new password can not be the same as the old password!"
        })
    
    userObj.password = newPassword
    userObj.save()
    return JsonResponse({
        'errcode':0,
        'errmsg':"ok"
    })



def sendEmailVerificationCode(request):
    userid = request.GET.get("userid")
    email = request.GET.get("email")
    print("1")

    try:
        userObj = User.objects.get(_id=userid, is_active=True)
    except:
        return JsonResponse({
            'errcode': 1,
            'errmsg': "can not find your account!"
        })
    
    if re.match("^(([^()[\]\\.,;:\s@\"]+(\.[^()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$", email)==None:
        return JsonResponse({
            'errcode': 1,
            'errmsg': "the format of the email is incorrect!"
        })
    print("2")
    
    code = getRandomToken2(8)
    newRecord = EmailVerificationCode.objects.create(
        apply_user = userObj,
        email = email,
        code = code,
        is_used = False,
        expire = datetime.datetime.now() + datetime.timedelta(minutes=5)
    )

    content = '''<!DOCTYPE html>
        <html>
        <meta charset="UTF-8">
        <head>
        <title>邮箱认证验证码</title>
        </head>
        <body>
        <div>尊敬的用户您好:</div>
         
                <p>要完成邮箱认证我们只需要确保这是您的电子邮件地址：</p>
                        <span style="color:red;">{email}</span>
                <p>这是您需要输入的验证码：</p>
                        <span style="font-size:36px;font-weight:700;">{code}</span>
                <p>请您在邮箱认证页面确认输入的邮箱是否正确，并且正确输入上面的验证码，切勿将验证码泄露给他人！</p>
        </body>
        </html>
                    '''.format(email=email, code=code)
    try:
        msg = EmailMultiAlternatives("邮箱认证", content, DEFAULT_FROM_EMAIL, [email])
        msg.attach_alternative(content, "text/html")
        msg.send()
    except Exception as e:
        print("4")
        return JsonResponse({
            'errcode': 1,
            'errmsg': str(e)
        })
    print("3")
    return JsonResponse({
        'errcode':0,
        'errmsg': "ok"
    })



def modifyEmail(request):
    cleanInvalidVerificationCode()

    userid = request.GET.get("userid")
    newEmail = request.GET.get("newEmail")
    verificationCode = request.GET.get("verificationCode")

    try:
        userObj = User.objects.get(_id=userid, is_active=True)
    except:
        return JsonResponse({
            'errcode':1,
            'errmsg': "can not find your account!"
        })
    
    try:
        verificationCodeRecord = EmailVerificationCode \
            .objects.get(apply_user=userObj, email=newEmail, code=verificationCode, is_used=False)
    except:
        return JsonResponse({
            'errcode': 1,
            'errmsg': "your email or verification code is not correct!"
        })
    
    if datetime.datetime.now() > verificationCodeRecord.expire:
        return JsonResponse({
            'errcode': 1,
            'errmsg': "your verification code is invalid!"
        })
    
    verificationCodeRecord.is_used = True
    verificationCodeRecord.save()
    
    userObj.email = newEmail
    userObj.save()
    return JsonResponse({
        'errcode': 0,
        'errmsg': "ok"
    })



def handleFaceVerify(request):
    data = json.loads(request.body.decode("utf-8").replace("'", "\""))
    userid = data.get("userid")
    face_base64_image = data.get("face")

    try:
        userObj = User.objects.get(_id=userid, is_active=True)
    except:
        return JsonResponse({
            'errcode': 1,
            'errmsg': "can not find your account!"
        })
    

    # 首次请求获取access_token
    access_token = getAccessToken()
    # 人脸注册请求路由
    request_url = "https://aip.baidubce.com/rest/2.0/face/v3/faceset/user/add"
    # 请求头
    headers = {'content-type': 'application/json'}
    # 完整的请求路由
    complete_request_url = request_url + "?access_token=" + access_token
    # 请求体中的请求参数
    params = {
        'image':face_base64_image,
        'image_type':'BASE64',
        'group_id':'user',
        'user_id':userObj._id,
        'quality_control':'NORMAL',
        'liveness_control':'NORMAL'
    }
    params = json.dumps(params)
    # 发送人脸注册请求
    response = requests.post(complete_request_url, data=params, headers=headers)
    # 返回信息处理
    if response:
        response = response.json()
        if response['error_code'] == 0 and response['error_msg'] == 'SUCCESS':
            userObj.face_verification = True
            userObj.save()
            return JsonResponse({
                'errcode': 0,
                'errmsg': "ok"
            })
        else:
            return JsonResponse({
                'errcode': 1,
                'errmsg': response['error_msg']
            })
    
    return JsonResponse({
        'errcode': 1,
        'errmsg': "face verify error!"
    })



def handleFaceRecognitionLogin(request):
    data = json.loads(request.body.decode("utf-8").replace("'", "\""))
    face_base64_image = data.get("face")
    remote_addr = request.META.get("REMOTE_ADDR")

    # 首次请求获取access_token
    access_token = getAccessToken()
    # 人脸搜索请求路由
    request_url = "https://aip.baidubce.com/rest/2.0/face/v3/search"
    # 请求头faceLogin
    headers = {'content-type': 'application/json'}
    # 完整的请求路由
    complete_request_url = request_url + "?access_token=" + access_token
    # 请求体中的请求参数
    params = {
        'image':face_base64_image,
        'image_type':'BASE64',
        'group_id_list':'user',
        'quality_control':'LOW',
        'liveness_control':'NORMAL'
    }
    params = json.dumps(params)
    # 发送人脸搜索请求
    response = requests.post(complete_request_url, data=params, headers=headers)
    if response:
        response = response.json()
        print(response)
        if response['error_code'] == 0 and response['error_msg'] == 'SUCCESS':
            user = response['result']['user_list'][0]
            if user['score'] > 80:
                try:
                    userObj = User.objects.get(_id=user['user_id'], is_active=True)
                except:
                    return JsonResponse({
                        'errcode': 1,
                        'errmsg': "can not find this user!"
                    })
                
                token = getToken(userObj._id, remote_addr)
                permissionList = list(userObj.role.permissions.values_list("_id", flat=True))
                user = {
                    "userid": userObj._id,
                    "role_id": userObj.role._id,
                    'username':userObj.name,
                    "permissions" :permissionList, 
                    "token": token
                }
                return JsonResponse({
                    'errcode':0,
                    'errmsg':"ok",
                    'user': user
                })

            else:
                return JsonResponse({
                    'errcode': 1,
                    'errmsg': "can not find match enough face!"
                })
        else:
            return JsonResponse({
                'errcode': 1,
                'errmsg': response['error_msg']
            })
    else:
        return JsonResponse({
            'errcode': 1,
            'errmsg': "face recognition error!"
        })



def getUsers(request):
    data = json.loads(request.body.decode("utf-8").replace("'", "\""))
    userId = data.get("userId")
    userName = data.get("userName")
    selectedDepartments = data.get("selectedDepartments")
    selectedRoles = data.get("selectedRoles")
    selectedStatus = data.get("selectedStatus")
    selectedWhetherFaceVerification = data.get("selectedWhetherFaceVerification")
    page = data.get("page")
    pageSize = data.get("pageSize")

    # print(userId)
    # print(userName)
    # print(selectedDepartments)
    # print(selectedRoles)
    # print(selectedStatus)
    # print(type(selectedStatus))
    # print(selectedWhetherFaceVerification)
    # print(page)
    # print(pageSize)

    departmentList = list(Department.objects.annotate(id=F("_id")).values("id", "name"))
    roleList = list(Role.objects.annotate(id=F("_id")).values("id", "name"))

    if selectedStatus == "":
        selectedStatus = [True, False]
    else:
        selectedStatus = [selectedStatus]
    if selectedWhetherFaceVerification == "":
        selectedWhetherFaceVerification = [True, False]
    else:
        selectedWhetherFaceVerification = [selectedWhetherFaceVerification]

    users = []
    if len(selectedDepartments) == 0 and len(selectedRoles) == 0:
        users = list(User.objects \
            .filter(_id__contains=userId, name__contains=userName, is_active__in=selectedStatus, \
                    face_verification__in=selectedWhetherFaceVerification) \
            .annotate(id=F("_id"), department=F("dept__name"), roleName=F("role__name"), borrowCount=F("borrow_count"), \
                    faceVerification=F("face_verification"), active=F("is_active")) \
            .values("id", "name", "password", "department", "roleName", "borrowCount", "phone", "email", \
                    "wechat", "faceVerification", "active"))
    elif len(selectedDepartments) == 0 and len(selectedRoles) != 0:
        users = list(User.objects \
            .filter(_id__contains=userId, name__contains=userName, role___id__in=selectedRoles, \
                    is_active__in=selectedStatus, face_verification__in=selectedWhetherFaceVerification) \
            .annotate(id=F("_id"), department=F("dept__name"), roleName=F("role__name"), borrowCount=F("borrow_count"), \
                    faceVerification=F("face_verification"), active=F("is_active")) \
            .values("id", "name", "password", "department", "roleName", "borrowCount", "phone", "email", \
                    "wechat", "faceVerification", "active"))
    elif len(selectedDepartments) != 0 and len(selectedRoles) == 0:
        users = list(User.objects \
            .filter(_id__contains=userId, name__contains=userName, dept___id__in=selectedDepartments, \
                    is_active__in=selectedStatus, face_verification__in=selectedWhetherFaceVerification) \
            .annotate(id=F("_id"), department=F("dept__name"), roleName=F("role__name"), borrowCount=F("borrow_count"), \
                    faceVerification=F("face_verification"), active=F("is_active")) \
            .values("id", "name", "password", "department", "roleName", "borrowCount", "phone", "email", \
                    "wechat", "faceVerification", "active"))
    else:
        users = list(User.objects \
            .filter(_id__contains=userId, name__contains=userName, dept___id__in=selectedDepartments, \
                    role___id__in=selectedRoles, is_active__in=selectedStatus, \
                    face_verification__in=selectedWhetherFaceVerification) \
            .annotate(id=F("_id"), department=F("dept__name"), roleName=F("role__name"), borrowCount=F("borrow_count"), \
                    faceVerification=F("face_verification"), active=F("is_active")) \
            .values("id", "name", "password", "department", "roleName", "borrowCount", "phone", "email", "wechat", \
                    "faceVerification", "active"))
    
    totalSize = len(users)
    users = users[(page-1)*pageSize:page*pageSize]

    for user in users:
        user["faceVerification"] = "已认证" if user["faceVerification"] else "未认证"
        user["active"] = 1 if user["active"] else  0

    return JsonResponse({
        'errcode': 0,
        'errmsg': "ok",
        "totalSize": totalSize,
        "res": users,
        "departmentList": departmentList,
        "roleList": roleList,
    })



def handleDeleteUser(request):
    userid = request.GET.get("userid")

    try:
        userObj = User.objects.get(_id=userid)
    except:
        return JsonResponse({
            'errcode': 1,
            'errmsg': "can not find this user!"
        })
    
    if userObj.is_active == False:
        return JsonResponse({
            'errcode': 1,
            'errmsg': "this user had been deleted!"
        })

    userObj.is_active = False
    userObj.save()

    return JsonResponse({
        'errcode': 0,
        'errmsg': "ok"
    })



def handleDeleteSelectionUsers(request):
    data = json.loads(request.body.decode("utf-8").replace("'", "\""))
    useridList = data.get("useridList")

    userObjList = []
    for userid in useridList:
        try:
            userObj = User.objects.get(_id=userid)
        except:
            return JsonResponse({
                'errcode': 1,
                'errmsg': "can not find one of these selected users!"
            })
        
        if userObj.is_active == False:
            return JsonResponse({
                'errcode': 1,
                'errmsg': "one of these selected users had been deleted!"
            })
        
        userObjList.append(userObj)

    for userObj in userObjList:
        userObj.is_active = False
        userObj.save()

    return JsonResponse({
        'errcode': 0,
        'errmsg': "ok"
    })



def handleRecoverUser(request):
    userId = request.GET.get("userId")

    try:
        userObj = User.objects.get(_id=userId)
    except:
        return JsonResponse({
            'errcode': 1,
            'errmsg': "can not find this user!"
        })
    
    if userObj.is_active == True:
        return JsonResponse({
            'errcode': 1,
            'errmsg': "this user is active!"
        })
    
    userObj.is_active = True
    userObj.save()
    return JsonResponse({
        'errcode': 0,
        'errmsg': "ok"
    })



def getUserInfo(request):
    userId = request.GET.get("userId")

    try:
        userObj = User.objects.get(_id=userId)
    except:
        return JsonResponse({
            'errcode': 1,
            'errmsg': "can not find this user!"
        })
    
    if userObj.is_active == False:
        return JsonResponse({
            'errcode': 1,
            'errmsg': "you can only edit active user!"
        })

    userForm = {
        'id': userObj._id,
        'name': userObj.name,
        'password': userObj.password,
        'currentDept': userObj.dept._id if userObj.dept!=None else "",
        'currentRole': userObj.role._id if userObj.role!=None else "",
        'phone': userObj.phone
    }
    departmentList = list(Department.objects.annotate(id=F("_id")).values("id", "name"))
    roleList = list(Role.objects.annotate(id=F("_id")).values("id", "name"))
    return JsonResponse({
        'errcode': 0,
        'errmsg': "ok",
        'userForm': userForm,
        'departmentList': departmentList,
        'roleList': roleList
    })



def handleEditUser(request):
    data = json.loads(request.body.decode("utf-8").replace("'", "\""))
    userForm = data.get("userForm")

    try:
        userObj = User.objects.get(_id=userForm["id"])
    except:
        return JsonResponse({
            'errcode': 1,
            'errmsg': "can not find this user!"
        })
    
    if userObj.is_active == False:
        return JsonResponse({
            'errcode': 1,
            'errmsg': "you can only edit active user!"
        })
    
    try:
        deptObj = Department.objects.get(_id=userForm["currentDept"])
    except:
        return JsonResponse({
            'errcode': 1,
            'errmsg': "can not find this department!"
        })
    
    try:
        roleObj = Role.objects.get(_id=userForm["currentRole"])
    except:
        return JsonResponse({
            'errcode': 1,
            'errmsg': "can not find this role!"
        })
    
    userObj.name = userForm["name"]
    userObj.password = userForm["password"]
    userObj.dept = deptObj
    userObj.borrow_count = roleObj.borrow_total_count - (userObj.role.borrow_total_count - userObj.borrow_count)
    userObj.role = roleObj
    userObj.phone = userForm["phone"]
    userObj.save()
    return JsonResponse({
        'errcode': 0,
        'errmsg': "ok"
    })



def getDepartmentsAndRolesList(request):
    departmentList = list(Department.objects.annotate(id=F("_id")).values("id", "name"))
    roleList = list(Role.objects.annotate(id=F("_id")).values("id", "name"))
    return JsonResponse({
        'errcode': 0,
        'errmsg': "ok",
        'departmentList': departmentList,
        'roleList': roleList
    })



def addNewUser(request):
    data = json.loads(request.body.decode("utf-8").replace("'", "\""))
    newUserForm = data.get("newUserForm")
    
    try:
        deptObj = Department.objects.get(_id=newUserForm["deptId"])
    except:
        return JsonResponse({
            'errcode': 1,
            'errmsg': "can not find this department!"
        })
    
    try:
        roleObj = Role.objects.get(_id=newUserForm["roleId"])
    except:
        return JsonResponse({
            'errcode': 1,
            'errmsg': "can not find this role!"
        })
    
    newUserObj = User.objects.create(
        _id = newUserForm["id"],
        name = newUserForm["name"],
        password = newUserForm["password"],
        dept = deptObj,
        role = roleObj,
        phone = newUserForm["phone"],
        borrow_count = roleObj.borrow_total_count,
        face_verification = False,
        is_active = True
    )
    return JsonResponse({
        'errcode': 0,
        'errmsg': "ok"
    })



def handleImportNewUsers(request):
    newUsersFile = request.FILES.get("newUsersFile")

    # 根据excel的文件类型分别采用不同的引擎加载文件
    if newUsersFile.content_type == "application/vnd.ms-excel":
        df = pd.read_excel(newUsersFile.file, usecols=[0,1,2,3], keep_default_na=False)
    elif newUsersFile.content_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
        df = pd.read_excel(newUsersFile.file, usecols=[0,1,2,3], keep_default_na=False, engine='openpyxl')

    # 获取职工角色对象
    try:
        roleObj = Role.objects.get(name="普通职工")
    except:
        return JsonResponse({
            'errcode': 1,
            'errmsg': "can not find staff role!"
        })

    # 先遍历一遍获取所有的部门对象
    departmentObjList = []
    for index, row in df.iterrows():
        dept = None
        if row["部门"] != "":
            try:
                dept = Department.objects.get(name=row["部门"])
            except:
                return JsonResponse({
                    'errcode': 1,
                    'errmsg': "can not find the department of the {userid} staff".format(userid=row["工号"])
                })
        departmentObjList.append(dept)

        try:
            userObj = User.objects.get(_id=row["工号"])
            return JsonResponse({
                'errcode': 1,
                'errmsg': "the {userid} id already exists!".format(userid=row["工号"])
            })
        except:
            continue
    
    # 遍历创建所有用户
    for index, row in df.iterrows():
        phone = None
        if row["电话号码"] != "":
            phone = row["电话号码"]

        User.objects.create(
            _id = row["工号"],
            name = row["姓名"],
            password = row["工号"],
            dept = departmentObjList[index],
            role = roleObj,
            phone = phone,
            borrow_count = roleObj.borrow_total_count,
            face_verification = False,
            is_active = True
        )
    return JsonResponse({
        'errcode': 0,
        'errmsg': "ok",
        'sum': len(df)
    })



def getRoles(request):
    page = int(request.GET.get("page"))
    pageSize = int(request.GET.get("pageSize"))

    roles = Role.objects.all()

    totalSize = len(roles)
    roles = roles[(page-1)*pageSize:page*pageSize]

    res = []
    for role in roles:
        res.append({
            'id': role._id,
            'name': role.name,
            'borrowTotalCount': role.borrow_total_count,
            'currentPermissions': list(role.permissions.annotate(id=F('_id')).values("id", "description"))
        })
    
    allPermissions = list(Permission.objects.annotate(id=F("_id")).values("id", "description"))

    return JsonResponse({
        'errcode': 0,
        'errmsg': "ok",
        'totalSize': totalSize,
        'res': res,
        'allPermissions': allPermissions
    })



def handleModifyRolePermissions(request):
    data = json.loads(request.body.decode("utf-8").replace("'", "\""))
    roleId = data.get("roleId")
    rolePermissions = data.get("rolePermissions")

    try:
        roleObj = Role.objects.get(_id=roleId)
    except:
        return JsonResponse({
            'errcode': 1,
            'errmsg': "can not find this role!"
        })
    
    permissionObjs = []
    for permissionId in rolePermissions:
        try:
            permissionObj = Permission.objects.get(_id=permissionId)
        except:
            return JsonResponse({
                'errcode': 1,
                'errmsg': "can not find one of these new permissions!"
            })
        permissionObjs.append(permissionObj)
    
    roleObj.permissions.clear()
    for permissionObj in permissionObjs:
        roleObj.permissions.add(permissionObj)
    
    return JsonResponse({
        'errcode': 0,
        'errmsg': "ok"
    })



def handleModifyBorrowTotalCount(request):
    roleId = int(request.GET.get("roleId"))
    newBorrowTotalCount = int(request.GET.get("newBorrowTotalCount"))

    try:
        roleObj = Role.objects.get(_id=roleId)
    except:
        return JsonResponse({
            'errcode': 1,
            'errmsg': "can not find this role!"
        })
    
    for user in roleObj.users.all():
        user.borrow_count = newBorrowTotalCount - (user.role.borrow_total_count - user.borrow_count)
        user.save()
    
    roleObj.borrow_total_count = newBorrowTotalCount
    roleObj.save()
    return JsonResponse({
        'errcode': 0,
        'errmsg': "ok"
    })



def addNewRole(request):
    data = json.loads(request.body.decode("utf-8").replace("'", "\""))
    name = data.get("name")
    borrowTotalCount = int(data.get("borrowTotalCount"))
    permissions = data.get("permissions")

    permissionObjs = []
    for permissionId in permissions:
        try:
            permissionObj = Permission.objects.get(_id=permissionId)
        except:
            return JsonResponse({
                'errcode': 1,
                'errmsg': "can not find one of these new permissions!"
            })
        permissionObjs.append(permissionObj)
    
    try:
        newRole = Role.objects.create(
            name = name,
            borrow_total_count = borrowTotalCount
        )
    except:
        return JsonResponse({
            'errcode': 1,
            'errmsg': "create new role error!"
        })

    for permissionObj in permissionObjs:
        newRole.permissions.add(permissionObj)
    
    return JsonResponse({
        'errcode': 0,
        'errmsg': "ok"
    })





    





































    




















