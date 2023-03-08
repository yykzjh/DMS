from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, FileResponse, StreamingHttpResponse
from django.conf import settings
from django.core import paginator
from django.db.models import *
from django.forms.models import model_to_dict
# from datetime import datetime, timedelta
import datetime
# import requests
import codecs
import csv
import copy
import os
import uuid
import json
import time
import urllib
from urllib.parse import quote
from document_management_system.settings import DOCUMENTS_BASE_DIR
from File.utils import (ZipUtility, judgeFilePermission, getFilePosition, getFolderPositionUtil, 
    getFolderPositionObj, getAllVersionsOfFile, getFileVersion, setOverTime, addNewFilingAudit, addNewFileAudit, 
    word2html, excel2pdf)
from User.models import *
from File.models import *


def index(request):
    return HttpResponse("file index!")



def getChildFolders(request):
    level = int(request.GET.get("level"))
    position = int(request.GET.get("position"))

    res = []
    if level == 0:
        projectTeams = ProjectTeam.objects.annotate(id=F("_id"))
        for projectTeam in projectTeams:
            managers = list(projectTeam.managers.values_list("_id", flat=True))
            projectTeam = projectTeam.__dict__
            projectTeam["managers"] = managers
            del projectTeam["_state"]
            res.append(projectTeam)
    elif level == 1:
        cabinets = FilingCabinet.objects.filter(position=position).annotate(id=F("_id"))
        for cabinet in cabinets:
            managers = list(cabinet.managers.values_list("_id", flat=True))
            cabinet = cabinet.__dict__
            cabinet["managers"] = managers
            cabinet["position"] = cabinet["position_id"]
            del cabinet["_state"]
            res.append(cabinet)
    elif level == 2:
        cases = FilingCase.objects.filter(position=position).annotate(id=F("_id"), type=F("_type"))
        for case in cases:
            managers = list(case.managers.values_list("_id", flat=True))
            permission_users = list(case.permission_users.values_list("_id", flat=True))
            case = case.__dict__
            case["managers"] = managers
            case["permission_users"] = permission_users
            case["position"] = case["position_id"]
            del case["_state"]
            res.append(case)
    elif level == 3:
        res = list(FilingBox.objects.filter(position=position, is_active=True).annotate(id=F("_id")).values())

    return JsonResponse({
        'res': res
    })



def getFilesData(request):
    setOverTime()

    data = json.loads(request.body.decode("utf-8").replace("'", "\""))
    userid = data.get('userid')
    level = int(data.get('level'))
    position_id = int(data.get('id'))
    page = int(data.get('page'))
    pageSize = int(data.get('pageSize'))
    fileName = data.get('fileName')
    creator = data.get('creator')

    superior_type = False
    if level == 3:
        superior_type = True
    elif level == 4:
        superior_type = False
    
    filesData = list(File.objects \
        .filter(superior_type=superior_type, position=position_id, 
            name__contains=fileName, creator__name__contains=creator, is_active=True) \
        .annotate(id=F("_id"), creator_name=F('creator__name'), type=F('_type'))
        .values())
    
    totalSize = len(filesData)
    res = filesData[pageSize*(page-1):pageSize*page]
    for file in res:
        file["permit"] = judgeFilePermission(file["id"], userid)
        file["creator"] = file["creator_name"]
        file["position"] = getFilePosition(file["id"])
        file["datetime"] = file["datetime"].strftime("%Y-%m-%d %H:%M:%S")
        del file["_id"]
        del file["_type"]
        del file["creator_id"]
        del file["creator_name"]
        # print(file["datetime"])

    return JsonResponse({
        'errcode':0,
        'errmsg':"ok",
        'res':res,
        'totalSize':totalSize
    })



def getFolderPosition(request):
    level = int(request.GET.get("level"))
    position_id = int(request.GET.get("id"))

    return JsonResponse({
        "position" : getFolderPositionUtil(level, position_id)
    })



def addNewFile(request):
    name = request.POST.get('name')
    level = int(request.POST.get('level'))
    position_id = int(request.POST.get('position_id'))
    creator_id = request.POST.get('creator_id')
    version_description = request.POST.get('version_description')
    _type = request.POST.get("type")
    remark = request.POST.get('remark')
    files = request.FILES.getlist("files")

    try:
        createUser = User.objects.get(_id=creator_id)
    except:
        return JsonResponse({
            'errcode': 1,
            'errmsg': "can not find creator account!"
        })
    superior_type = (level == 3)
    # 创建文件对象
    newFile = File.objects.create(
        name = name,
        superior_type = superior_type,
        position = position_id,
        creator = createUser,
        remark = remark,
        _type = _type
    )
    # 创建版本对象
    newVersion = FileVersions.objects.create(
        file = newFile,
        description = version_description,
    )
    # 保存新建文件的版本号
    newFile.current_version_id = newVersion._id
    newFile.save()

    # 生成版本文件夹保存地址
    file_folder_name = ''.join(str(uuid.uuid3(uuid.NAMESPACE_DNS, name)).split('-')) + "__" + name
    folder_full_path = os.path.join(DOCUMENTS_BASE_DIR, file_folder_name, str(newVersion._id))
    # 将文件夹地址保存在数据库
    newFile.url = file_folder_name
    newFile.save()

    # 保存文件
    for f in files:
        if not os.path.exists(folder_full_path):
            os.makedirs(folder_full_path, 755)
        with open(os.path.join(folder_full_path, f.name), "wb+") as file:
            for chunk in f.chunks():
                file.write(chunk)

    addNewFileAudit(createUser, "新增", newFileObj=newFile)
    return JsonResponse({
        'errcode':0,
        'errmsg':'ok'
    })
    


def getFileBasicInfo(request):
    fileId = int(request.GET.get("fileId"))

    # 找到数据库中的文件对象
    fileObj = File.objects.filter(_id=fileId).first()
    if fileObj is None: return JsonResponse({'errcode':1,'errmsg':"can not find this file!"})
    # 找到该文件当前的版本对象
    verObj = FileVersions.objects.filter(_id=fileObj.current_version_id).first()
    if verObj is None: return JsonResponse({'errcode':1,'errmsg':"can not find current version of this file!"})
    # 获取文件夹全路径
    folder_full_path = os.path.join(DOCUMENTS_BASE_DIR, fileObj.url, str(verObj._id))
    # 获取所有文件夹下所有附件的名称
    childFileNames = os.listdir(folder_full_path)

    name = fileObj.name
    position = getFilePosition(fileId)
    creator = fileObj.creator.name
    createTime = fileObj.datetime.strftime("%Y-%m-%d %H:%M:%S")
    _type = fileObj._type
    remark = fileObj.remark

    return JsonResponse({
        'errcode':0,
        'errmsg':"ok",
        'res':{
            'name': name,
            'position': position,
            'creator': creator,
            'createTime': createTime,
            'type': _type,
            'remark': remark,
            'childFileNames': childFileNames
        }
    })



def previewFile(request):
    fileId = int(request.GET.get("fileId"))
    fileName = request.GET.get("fileName")

    # 找到数据库中的文件对象
    fileObj = File.objects.filter(_id=fileId).first()
    if fileObj is None: return JsonResponse({'errcode':1,'errmsg':"can not find this file!"})
    # 找到该文件当前的版本对象
    verObj = FileVersions.objects.filter(_id=fileObj.current_version_id).first()
    if verObj is None: return JsonResponse({'errcode':1,'errmsg':"can not find current version of this file!"})
    # 获取文件全路径
    file_full_path = os.path.join(DOCUMENTS_BASE_DIR, fileObj.url, str(verObj._id), fileName)

    # # 文件格式转换
    # pdfConverter = PDFConverter()
    # file = pdfConverter.run(file_full_path)
    # if file == None:
    #     with open(file_full_path, 'rb') as f:
    #         file = f.read()
    # response = HttpResponse(file, content_type="application/pdf")

    ext = file_full_path.split('.')[-1].lower()
    contentType = ""
    if ext == "jpg" or ext == "jpeg":
        contentType = "image/jpeg"
    elif ext == "png":
        contentType = "image/png"
    elif ext == "doc" or ext == "docx":
        contentType = "text/html"
    elif ext == "txt":
        contentType = "text/plain"
    elif ext == "pdf":
        contentType = "application/pdf"
    elif ext == "xls" or ext == "xlsx":
        contentType = "text/html"
    
    file = None
    if ext == "xls" or ext == "xlsx":
        file = excel2pdf(file_full_path)
    elif ext == "doc" or ext == "docx":
        file = word2html(file_full_path)
    if file == None:
        with open(file_full_path, 'rb') as f:
            file = f.read()
    response = HttpResponse(file, content_type=contentType)
    return response



def downloadFile(request):
    fileId = int(request.GET.get("fileId"))
    fileName = request.GET.get("fileName")

    # 找到数据库中的文件对象
    fileObj = File.objects.filter(_id=fileId).first()
    if fileObj is None: return JsonResponse({'errcode':1,'errmsg':"can not find this file!"})
    # 找到该文件当前的版本对象
    verObj = FileVersions.objects.filter(_id=fileObj.current_version_id).first()
    if verObj is None: return JsonResponse({'errcode':1,'errmsg':"can not find current version of this file!"})
    # 获取文件全路径
    file_full_path = os.path.join(DOCUMENTS_BASE_DIR, fileObj.url, str(verObj._id), fileName)
    
    file=open(file_full_path, 'rb')
    response =FileResponse(file)
    response['Content-Type']='application/octet-stream'
    response["Access-Control-Expose-Headers"] = "Content_Disposition"
    response['Content_Disposition']='attachment;filename="{0}"'.format(quote(fileName))
    return response



def downloadFolder(request):
    fileId = int(request.GET.get("fileId"))

    # 找到数据库中的文件对象
    fileObj = File.objects.filter(_id=fileId).first()
    if fileObj is None: return JsonResponse({'errcode':1,'errmsg':"can not find this file!"})
    # 找到该文件当前的版本对象
    verObj = FileVersions.objects.filter(_id=fileObj.current_version_id).first()
    if verObj is None: return JsonResponse({'errcode':1,'errmsg':"can not find current version of this file!"})
    # 获取要打包的文件夹全路径
    folder_full_path = os.path.join(DOCUMENTS_BASE_DIR, fileObj.url, str(verObj._id))

    # 创建打包工具类
    zipUtility = ZipUtility()
    zipUtility.toZip(folder_full_path, fileObj.name)

    # 返回下载
    response = StreamingHttpResponse(zipUtility.zip_file)
    response['Content-Type'] = "application/octet-stream"
    response["Access-Control-Expose-Headers"] = "Content_Disposition"
    response['Content_Disposition'] = 'attachment;filename="{0}"'.format(quote(fileObj.name) + ".zip")
    return response



def deleteFile(request):
    fileId = int(request.GET.get("fileId"))
    operatorid = request.GET.get("userid")

    try:
        operatorObj = User.objects.get(_id=operatorid, is_active=True)
    except:
        return JsonResponse({
            'errcode':1,
            'errmsg':"can not find your account!"
        })

    try:
        delFile = File.objects.get(_id=fileId)
    except:
        return JsonResponse({
            'errcode':1,
            'errmsg':"can not find this file!"
        })
    
    oldFileObj = copy.deepcopy(delFile)
    delFile.is_active = False
    delFile.save()

    addNewFileAudit(operatorObj, "删除", oldFileObj=oldFileObj)

    return JsonResponse({
        'errcode':0,
        'errmsg': "ok"
    })



def deleteSelectionFiles(request):
    data = json.loads(request.body.decode("utf-8").replace("'", "\""))
    fileIds = data.get("fileIds")
    operatorid = data.get("userid")

    try:
        operatorObj = User.objects.get(_id=operatorid, is_active=True)
    except:
        return JsonResponse({
            'errcode':1,
            'errmsg':"can not find your account!"
        })

    delFiles = []
    for fileId in fileIds:
        try:
            delFile = File.objects.get(_id=fileId)
            delFiles.append(delFile)
        except:
            return JsonResponse({
                'errcode':1,
                'errmsg':"can not find one of these files!"
            })
    
    for delFile in delFiles:
        oldFileObj = copy.deepcopy(delFile)
        delFile.is_active = False
        delFile.save()
        addNewFileAudit(operatorObj, "删除", oldFileObj=oldFileObj)

    return JsonResponse({
        'errcode':0,
        'errmsg': "ok"
    })



def getFileEditInfo(request):
    fileId = int(request.GET.get("fileId"))

    # 找到数据库中的文件对象
    theFile = File.objects.filter(_id=fileId, is_active=True) \
        .annotate(id=F('_id'), type=F('_type'), creator_name=F('creator__name'), createTime=F('datetime')).values()
    if len(theFile) == 0: return JsonResponse({'errcode':1,'errmsg':"can not find this file!"})
    theFile = theFile[0]
    print(theFile)

    theFile["position"] = getFolderPositionObj(3 if theFile["superior_type"] else 4, theFile["position"])
    theFile["versions"] = getAllVersionsOfFile(theFile["id"])
    theFile["currentVersion"] = theFile["current_version_id"]
    theFile["creator"] = theFile["creator_name"]
    theFile["createTime"] = theFile["createTime"].strftime("%Y-%m-%d %H:%M:%S")
    del theFile["creator_name"]
    del theFile["_id"]
    del theFile["_type"]
    del theFile["datetime"]
    del theFile["current_version_id"]
    del theFile["superior_type"]
    del theFile["is_active"]
    del theFile["creator_id"]
    print(theFile)

    return JsonResponse({
        'errcode': 0,
        'errmsg': "ok",
        'res': theFile
    })



def getChildPositions(request):
    level = int(request.GET.get("level"))
    position = int(request.GET.get("position"))
    userid = request.GET.get("userid")
    _type = request.GET.get("type")

    res = []
    if level == 0:
        projectTeams = ProjectTeam.objects.annotate(id=F("_id"))
        for projectTeam in projectTeams:
            managers = list(projectTeam.managers.values_list("_id", flat=True))
            if userid not in managers:
                break
            else:
                projectTeam = projectTeam.__dict__
                res.append({
                    "id": projectTeam["id"],
                    "name": projectTeam["name"]
                })
    elif level == 1:
        cabinets = FilingCabinet.objects.filter(position=position).annotate(id=F("_id"))
        for cabinet in cabinets:
            managers = list(cabinet.managers.values_list("_id", flat=True))
            if userid not in managers:
                break
            else:
                cabinet = cabinet.__dict__
                res.append({
                    "id": cabinet["id"],
                    "name": cabinet["name"]
                })
    elif level == 2:
        cases = FilingCase.objects.filter(position=position, _type=_type).annotate(id=F("_id"), type=F("_type"))
        for case in cases:
            managers = list(case.managers.values_list("_id", flat=True))
            if userid not in managers:
                break
            else:
                case = case.__dict__
                res.append({
                    "id": case["id"],
                    "name": case["name"]
                })
    elif level == 3:
        res = list(FilingBox.objects.filter(position=position, is_active=True).annotate(id=F("_id")).values("id", "name"))

    print(res)
    return JsonResponse({
        'res': res
    })



def addNewVersion(request):
    fileId = int(request.POST.get("fileId"))
    description = request.POST.get("version_description")
    files = request.FILES.getlist("files")

    # 找到文件对象
    try:
        fileObj = File.objects.get(_id=fileId)
    except:
        return JsonResponse({
            'errcode': 1,
            'errmsg': "can not find the file!"
        })
    # 创建版本对象
    newVersion = FileVersions.objects.create(
        file = fileObj,
        description = description,
    )

    # 生成版本文件夹保存地址
    file_folder_name = fileObj.url
    folder_full_path = os.path.join(DOCUMENTS_BASE_DIR, file_folder_name, str(newVersion._id))

    # 保存文件
    for f in files:
        if not os.path.exists(folder_full_path):
            os.makedirs(folder_full_path, 755)
        with open(os.path.join(folder_full_path, f.name), "wb+") as file:
            for chunk in f.chunks():
                file.write(chunk)

    return JsonResponse({
        'errcode':0,
        'errmsg':'ok',
        'newVersion':{
            'id': newVersion._id,
            'description':newVersion.description
        }
    })



def editFile(request):
    data = json.loads(request.body.decode("utf-8").replace("'", "\""))
    fileId = int(data.get("fileId"))
    name = data.get("name")
    level = int(data.get("level"))
    position = int(data.get("position"))
    remark = data.get("remark")
    versionId = int(data.get("versionId"))
    operatorid = data.get("userid")

    try:
        operatorObj = User.objects.get(_id=operatorid, is_active=True)
    except:
        return JsonResponse({
            'errcode':1,
            'errmsg':"can not find your account!"
        })
    
    # 找到文件对象
    try:
        fileObj = File.objects.get(_id=fileId, is_active=True)
    except:
        return JsonResponse({
            'errcode': 1,
            'errmsg': "can not find this file!"
        })
    
    oldFileObj = copy.deepcopy(fileObj)
    
    fileObj.name = name
    fileObj.superior_type = True if level==3 else False
    fileObj.position = position
    fileObj.remark = remark
    fileObj.current_version_id = versionId
    fileObj.save()

    addNewFileAudit(operatorObj, "修改", newFileObj=fileObj, oldFileObj=oldFileObj)

    return JsonResponse({
        'errcode': 0,
        'errmsg': "ok"
    })



def deleteFilingBox(request):
    boxId = int(request.GET.get("boxId"))
    operatorid = request.GET.get("userid")

    try:
        operatorObj = User.objects.get(_id=operatorid, is_active=True)
    except:
        return JsonResponse({
            'errcode':1,
            'errmsg':"can not find your account!"
        })

    # 找到该文件盒对象
    try:
        boxObj = FilingBox.objects.get(_id=boxId, is_active=True)
    except:
        return JsonResponse({
            'errcode': 1,
            'errmsg': "can not find this filingbox!"
        })
    
    oldBoxObj = copy.deepcopy(boxObj)

    # 把该文件盒下的文件转移到文件盒所在的文件柜格
    cnt = File.objects.filter(superior_type=False, position=boxObj._id, is_active=True).update(position=boxObj.position._id, superior_type=True)

    # 删除该文件盒
    boxObj.is_active = False
    boxObj.save()
    addNewFilingAudit(4, operatorObj, "删除", oldFilingObj=oldBoxObj)

    return JsonResponse({
        'errcode': 0,
        'errmsg':"ok"
    })



def addNewFiling(request):
    # 先确定添加的层级
    level = int(request.GET.get("level"))
    operatorid = request.GET.get("userid")

    try:
        operatorObj = User.objects.get(_id=operatorid, is_active=True)
    except:
        return JsonResponse({
            'errcode':1,
            'errmsg':"can not find your account!"
        })

    # 根据层级接受不同的参数
    if level == 0:
        name = request.GET.get("name")
        remark = request.GET.get("remark")
        manager_id = request.GET.get("manager_id")

        # 获取管理员对象
        try:
            managerObj = User.objects.get(_id=manager_id, is_active=True)
        except:
            return JsonResponse({
                'errcode':1,
                'errmsg':"can not find this manager!"
            })
        
        # 插入新数据
        newProjectTeam = ProjectTeam.objects.create(name=name, remark=remark)
        newProjectTeam.managers.add(managerObj)
        addNewFilingAudit(level+1, operatorObj, "新增", newFilingObj=newProjectTeam)
    
    elif level == 1:
        position_id = request.GET.get("position_id")
        name = request.GET.get("name")
        remark = request.GET.get("remark")
        manager_id = request.GET.get("manager_id")

        # 获取项目组对象和管理员对象
        try:
            projectTeamObj = ProjectTeam.objects.get(_id=position_id)
        except:
            return JsonResponse({
                'errcode':1,
                'errmsg':"can not find this project team!"
            })
        try:
            managerObj = User.objects.get(_id=manager_id, is_active=True)
        except:
            return JsonResponse({
                'errcode':1,
                'errmsg':"can not find this manager!"
            })
        
        # 插入新数据
        newCabinet = FilingCabinet.objects.create(name=name, position=projectTeamObj, remark=remark)
        newCabinet.managers.add(managerObj)
        addNewFilingAudit(level+1, operatorObj, "新增", newFilingObj=newCabinet)
    
    elif level == 2:
        position_id = request.GET.get("position_id")
        name = request.GET.get("name")
        _type = request.GET.get("type")
        remark = request.GET.get("remark")
        manager_id = request.GET.get("manager_id")

        # 获取文件柜对象和管理员对象
        try:
            cabinetObj = FilingCabinet.objects.get(_id=position_id)
        except:
            return JsonResponse({
                'errcode':1,
                'errmsg':"can not find this filing cabinet!"
            })
        try:
            managerObj = User.objects.get(_id=manager_id, is_active=True)
        except:
            return JsonResponse({
                'errcode':1,
                'errmsg':"can not find this manager!"
            })
        
        # 插入新数据
        newCase = FilingCase.objects.create(name=name, _type=_type, position=cabinetObj, remark=remark)
        newCase.managers.add(managerObj)
        addNewFilingAudit(level+1, operatorObj, "新增", newFilingObj=newCase)
    
    elif level == 3:
        position_id = request.GET.get("position_id")
        name = request.GET.get("name")
        remark = request.GET.get("remark")

        # 获取文件柜格对象
        try:
            caseObj = FilingCase.objects.get(_id=position_id)
        except:
            return JsonResponse({
                'errcode':1,
                'errmsg':"can not find this filing case!"
            })
        
        # 插入新数据
        newBox = FilingBox.objects.create(name=name, position=caseObj, remark=remark, is_active=True)
        addNewFilingAudit(level+1, operatorObj, "新增", newFilingObj=newBox)

    return JsonResponse({
        'errcode':0,
        'errmsg':"ok"
    })



def getEditFilingInfo(request):
    level = int(request.GET.get("level"))
    _id = int(request.GET.get("id"))

    res = {}
    if level == 1:
        try:
            projectTeamObj = ProjectTeam.objects.get(_id=_id)
        except:
            return JsonResponse({
                'errcode':1,
                'errmsg':"can not find this project team!"
            })
        managerNameList = list(projectTeamObj.managers.values_list("name", flat=True))
        managerNames = ", ".join(managerNameList)
        positionStr = "/"
        res = model_to_dict(projectTeamObj, fields=["name", "remark"])
        res["managerNames"] = managerNames
        res["position"] = positionStr
    
    elif level == 2:
        try:
            cabinetObj = FilingCabinet.objects.get(_id=_id)
        except:
            return JsonResponse({
                'errcode':1,
                'errmsg':"can not find this filing cabinet!"
            })
        managerNameList = list(cabinetObj.managers.values_list("name", flat=True))
        managerNames = ", ".join(managerNameList)
        positionStr = getFolderPositionUtil(level-1, cabinetObj.position._id)
        res = model_to_dict(cabinetObj, fields=["name", "remark"])
        res["managerNames"] = managerNames
        res["position"] = positionStr
    
    elif level == 3:
        try:
            caseObj = FilingCase.objects.get(_id=_id)
        except:
            return JsonResponse({
                'errcode':1,
                'errmsg':"can not find this filing case!"
            })
        managerNameList = list(caseObj.managers.values_list("name", flat=True))
        managerNames = ", ".join(managerNameList)
        positionStr = getFolderPositionUtil(level-1, caseObj.position._id)
        permitUserList = list(caseObj.permission_users.annotate(id=F("_id")).values("id", "name"))
        res = model_to_dict(caseObj, fields=["name", "_type", "remark"])
        res["managerNames"] = managerNames
        res["position"] = positionStr
        res["permitUserList"] = permitUserList
        res["type"] = res["_type"]
        del res["_type"]
    elif level == 4:
        try:
            boxObj = FilingBox.objects.get(_id=_id, is_active=True)
        except:
            return JsonResponse({
                'errcode':1,
                'errmsg':"can not find this filing box!"
            })
        positionObjList = getFolderPositionObj(level-1, boxObj.position._id)
        res = model_to_dict(boxObj, fields=["name", "remark"])
        res["positions"] = positionObjList
    
    print(res)
    return JsonResponse({
        'errcode':0,
        'errmsg':"ok",
        'res':res
    })



def editFiling(request):
    data = json.loads(request.body.decode("utf-8").replace("'", "\""))
    level = int(data.get("level"))
    operatorid = data.get("userid")

    try:
        operatorObj = User.objects.get(_id=operatorid, is_active=True)
    except:
        return JsonResponse({
            'errcode':1,
            'errmsg':"can not find your account!"
        })

    if level == 1:
        _id = int(data.get("id"))
        name = data.get("name")
        remark = data.get("remark")

        try:
            projectTeamObj = ProjectTeam.objects.get(_id=_id)
        except:
            return JsonResponse({
                'errcode':1,
                'errmsg':"can not find this project team!"
            })
        
        oldProjectTeamObj = copy.deepcopy(projectTeamObj)
        projectTeamObj.name = name
        projectTeamObj.remark = remark
        projectTeamObj.save()
        addNewFilingAudit(level, operatorObj, "修改", newFilingObj=projectTeamObj, oldFilingObj=oldProjectTeamObj)
    
    elif level == 2:
        _id = int(data.get("id"))
        name = data.get("name")
        remark = data.get("remark")

        try:
            cabinetObj = FilingCabinet.objects.get(_id=_id)
        except:
            return JsonResponse({
                'errcode':1,
                'errmsg':"can not find this filing cabinet!"
            })
        
        oldCabinetObj = copy.deepcopy(cabinetObj)
        cabinetObj.name = name
        cabinetObj.remark = remark
        cabinetObj.save()
        addNewFilingAudit(level, operatorObj, "修改", newFilingObj=cabinetObj, oldFilingObj=oldCabinetObj)
    
    elif level == 3:
        _id = int(data.get("id"))
        name = data.get("name")
        remark = data.get("remark")
        permitUserList = data.get("permitUserList")

        try:
            caseObj = FilingCase.objects.get(_id=_id)
        except:
            return JsonResponse({
                'errcode':1,
                'errmsg':"can not find this filing case!"
            })
        
        oldCaseObj = copy.deepcopy(caseObj)
        oldPermitUserList = sorted(list(oldCaseObj.permission_users.values_list("name", flat=True)))

        caseObj.name = name
        caseObj.remark = remark
        permitUserObjList = []
        for permitUser in permitUserList:
            try:
                permitUserObj = User.objects.get(_id=permitUser["id"], is_active=True)
            except:
                return JsonResponse({
                    'errcode':1,
                    'errmsg':"can not find permit user!"
                })
            permitUserObjList.append(permitUserObj)

        caseObj.permission_users.clear()
        for permitUserObj in permitUserObjList:
            caseObj.permission_users.add(permitUserObj)
        caseObj.save()

        newPermitUserList = sorted(list(caseObj.permission_users.values_list("name", flat=True)))
        addNewFilingAudit(level, operatorObj, "修改", newFilingObj=caseObj, oldFilingObj=oldCaseObj, \
            newPermitUsers=newPermitUserList, oldPermitUsers=oldPermitUserList)
    
    elif level == 4:
        _id = int(data.get("id"))
        name = data.get("name")
        remark = data.get("remark")
        position_id = data.get("position_id")

        try:
            boxObj = FilingBox.objects.get(_id=_id, is_active=True)
        except:
            return JsonResponse({
                'errcode':1,
                'errmsg':"can not find this filing box!"
            })
        
        try:
            caseObj = FilingCase.objects.get(_id=position_id)
        except:
            return JsonResponse({
                'errcode':1,
                'errmsg':"can not find this position!"
            })
        
        oldBoxObj = copy.deepcopy(boxObj)
        boxObj.name = name
        boxObj.remark = remark
        boxObj.position = caseObj
        boxObj.save()
        addNewFilingAudit(level, operatorObj, "修改", newFilingObj=boxObj, oldFilingObj=oldBoxObj)
    
    return JsonResponse({
        'errcode':0,
        'errmsg':"ok"
    })



def getFileApprovers(request):
    fileId = int(request.GET.get("fileId"))
    try:
        fileObj = File.objects.get(_id=fileId)
    except:
        return JsonResponse({
            'errcode':1,
            'errmsg':"can not find this file!"
        })

    caseObj = ""
    if fileObj.superior_type:
        try:
            caseObj = FilingCase.objects.get(_id=fileObj.position)
        except:
            return JsonResponse({
                'errcode':1,
                'errmsg':"can not find the filing case of this file!"
            })
    else:
        try:
            boxObj = FilingBox.objects.get(_id=fileObj.position, is_active=True)
        except:
            return JsonResponse({
                'errcode':1,
                'errmsg':"can not find the filing box of this file!"
            })
        caseObj = boxObj.position
    
    approversList = []
    currentObj = caseObj
    for i in range(3):
        managers = currentObj.managers.annotate(id=F('_id')).values("id", "name")
        for manager in managers:
            if manager not in approversList:
                approversList.append(manager)
        if i == 2:
            break
        currentObj = currentObj.position
    print(approversList)

    return JsonResponse({
        'errcode':0,
        'errmsg':"ok",
        'res':approversList
    })



def addNewBorrowRecord(request):
    data = json.loads(request.body.decode("utf-8").replace("'", "\""))
    borrowUser = data.get("borrowUser")
    borrowFile = data.get("borrowFile")
    reason = data.get("reason")
    bstime = data.get("bstime")
    betime = data.get("betime")
    approvers = data.get("approvers")
    notifyers = data.get("notifyers")
    remark = data.get("remark")

    # 获得用户对象和文件对象
    try:
        userObj = User.objects.get(_id=borrowUser["id"], is_active=True)
    except:
        return JsonResponse({
            'errcode':1,
            'errmsg':"can not find this user!"
        })
    try:
        fileObj = File.objects.get(_id=borrowFile["id"])
    except:
        return JsonResponse({
            'errcode':1,
            'errmsg':"can not find this file!"
        })
    
    if userObj.borrow_count <= 0:
        return JsonResponse({
            'errcode':1,
            'errmsg': "您的借阅次数已达上限！"
        })
    
    haveBorrowRecord = BorrowRecords.objects.filter(borrow_user=userObj, borrow_file=fileObj, status__in=[0, 1, 3, 4], show_user=True)
    if len(haveBorrowRecord) > 0:
        return JsonResponse({
            'errcode':1,
            'errmsg':"您已经借阅了该文件，请勿重复借阅！"
        })

    # 先把审批人和抄送人的对象查出来
    approverObjList = []
    notifyerObjList = []
    for approver in approvers:
        try:
            approverObj = User.objects.get(_id=approver["id"], is_active=True)
        except:
            return JsonResponse({
                'errcode':1,
                'errmsg':"can not find someone approver!"
            })
        approverObjList.append(approverObj)
    for notifyer in notifyers:
        try:
            notifyerObj = User.objects.get(_id=notifyer["id"], is_active=True)
        except:
            return JsonResponse({
                'errcode':1,
                'errmsg':"can not find someone notifyer!"
            })
        notifyerObjList.append(notifyerObj)

    # 新增借阅记录
    newBorrowRecord = BorrowRecords.objects.create(
        borrow_user = userObj,
        borrow_file = fileObj,
        borrow_version_id = fileObj.current_version_id,
        reason = reason,
        bstime = bstime,
        betime = betime,
        remark = remark,
        status = 0,
        is_active = True
    )
    # 添加审批人
    for approverObj in approverObjList:
        newBorrowRecord.approvers.add(approverObj)
    # 添加抄送人
    for notifyerObj in notifyerObjList:
        newBorrowRecord.notifyers.add(notifyerObj)
    # 借阅次数减1
    userObj.borrow_count -= 1
    userObj.save()
    return JsonResponse({
        'errcode':0,
        'errmsg':"ok"
    })



def getMyBorrowRecord(request):
    setOverTime()

    data = json.loads(request.body.decode("utf-8").replace("'", "\""))
    userid = data.get("userid")
    statusList = data.get("statusList")
    page = int(data.get("page"))
    pageSize = int(data.get("pageSize"))

    try:
        userObj = User.objects.get(_id=userid, is_active=True)
    except:
        return JsonResponse({
            'errcode':1,
            'errmsg': "can not find your account!"
        })
    
    borrowRecords = list(BorrowRecords.objects.filter(borrow_user=userObj, status__in=statusList, show_user=True) \
        .annotate(id=F('_id'), fileName=F('borrow_file__name'), approverName=F('real_approver__name')) \
        .values("id", "fileName", "reason", "bstime", "betime", "stime", "ptime", "approverName", "status", "remark", "urge"))
    
    totalSize = len(borrowRecords)
    borrowRecords = borrowRecords[(page-1)*pageSize:page*pageSize]

    upperTime = datetime.datetime.now() - datetime.timedelta(hours=2)
    for borrowRecord in borrowRecords:
        borrowRecord["btime"] = borrowRecord["bstime"].strftime("%Y-%m-%d %H:%M:%S") + "  至  " + \
                                borrowRecord["betime"].strftime("%Y-%m-%d %H:%M:%S")
        del borrowRecord["bstime"]
        del borrowRecord["betime"]

        if borrowRecord["status"] == 0:
            if borrowRecord["stime"] > upperTime:
                borrowRecord["urge"] = 3
            elif borrowRecord["urge"] == True:
                borrowRecord["urge"] = 2
            elif borrowRecord["stime"] <= upperTime and borrowRecord["urge"] == False :
                borrowRecord["urge"] = 1
        else:
            del borrowRecord["urge"]
        
        borrowRecord["stime"] = borrowRecord["stime"].strftime("%Y-%m-%d %H:%M:%S")
        if borrowRecord["ptime"] is not None:
            borrowRecord["ptime"] = borrowRecord["ptime"].strftime("%Y-%m-%d %H:%M:%S")
    
    return JsonResponse({
        'errcode':0,
        "errmsg":"ok",
        'res':borrowRecords,
        "totalSize": totalSize
    })



def getMyBorrowRecords(request):
    setOverTime()

    data = json.loads(request.body.decode("utf-8").replace("'", "\""))
    userid = data.get("userid")
    statusList = data.get("statusList")
    fileName = data.get("fileName")
    page = int(data.get("page"))
    pageSize = int(data.get("pageSize"))

    try:
        userObj = User.objects.get(_id=userid, is_active=True)
    except:
        return JsonResponse({
            'errcode':1,
            'errmsg': "can not find your account!"
        })
    
    borrowRecords = list(BorrowRecords.objects \
        .filter(borrow_user=userObj, status__in=statusList, borrow_file__name__contains=fileName, show_user=True) \
        .annotate(id=F('_id'), fileName=F('borrow_file__name')) \
        .values("id", "fileName", "reason", "bstime", "betime", "stime", "status", "remark", "urge"))
    
    totalSize = len(borrowRecords)
    borrowRecords = borrowRecords[(page-1)*pageSize:page*pageSize]

    upperTime = datetime.datetime.now() - datetime.timedelta(hours=2)
    for borrowRecord in borrowRecords:
        borrowRecord["btime"] = borrowRecord["bstime"].strftime("%Y-%m-%d %H:%M:%S") + "  至  " + \
                                borrowRecord["betime"].strftime("%Y-%m-%d %H:%M:%S")
        del borrowRecord["bstime"]
        del borrowRecord["betime"]

        if borrowRecord["status"] == 0:
            if borrowRecord["stime"] > upperTime:
                borrowRecord["urge"] = 3
            elif borrowRecord["urge"] == True:
                borrowRecord["urge"] = 2
            elif borrowRecord["stime"] <= upperTime and borrowRecord["urge"] == False :
                borrowRecord["urge"] = 1
        else:
            del borrowRecord["urge"]
        
        borrowRecord["stime"] = borrowRecord["stime"].strftime("%Y-%m-%d %H:%M:%S")
    
    return JsonResponse({
        'errcode':0,
        "errmsg":"ok",
        'res':borrowRecords,
        "totalSize": totalSize
    })



def getManageBorrowRecord(request):
    setOverTime()

    data = json.loads(request.body.decode("utf-8").replace("'", "\""))
    userid = data.get("userid")
    statusList = data.get("statusList")
    page = int(data.get("page"))
    pageSize = int(data.get("pageSize"))

    try:
        userObj = User.objects.get(_id=userid, is_active=True)
    except:
        return JsonResponse({
            'errcode':1,
            'errmsg': "can not find your account!"
        })
    
    borrowRecords = BorrowRecords.objects.filter(status__in=statusList, is_active=True) \
        .annotate(id=F('_id'), userName=F('borrow_user__name'), fileName=F('borrow_file__name')).order_by("-urge", "stime")
    
    res = []
    for borrowRecord in borrowRecords:
        if borrowRecord.status == 0:
            approvers = list(borrowRecord.approvers.values_list("_id", flat=True))
            if userid in approvers:
                borrowRecord = dict(
                    id = borrowRecord.id,
                    userName = borrowRecord.userName,
                    fileName = borrowRecord.fileName,
                    bstime = borrowRecord.bstime,
                    betime = borrowRecord.betime,
                    stime = borrowRecord.stime,
                    reason = borrowRecord.reason,
                    status = borrowRecord.status,
                    remark = borrowRecord.remark,
                    urge = borrowRecord.urge
                )
                borrowRecord["btime"] = borrowRecord["bstime"].strftime("%Y-%m-%d %H:%M:%S") + "  至  " + \
                                        borrowRecord["betime"].strftime("%Y-%m-%d %H:%M:%S")
                del borrowRecord["bstime"]
                del borrowRecord["betime"]
                borrowRecord["stime"] = borrowRecord["stime"].strftime("%Y-%m-%d %H:%M:%S")
                res.append(borrowRecord)
        elif borrowRecord.status in [1, 2, 4, 5]:
            if userid == borrowRecord.real_approver._id:
                borrowRecord = dict(
                    id = borrowRecord.id,
                    userName = borrowRecord.userName,
                    fileName = borrowRecord.fileName,
                    bstime = borrowRecord.bstime,
                    betime = borrowRecord.betime,
                    stime = borrowRecord.stime,
                    reason = borrowRecord.reason,
                    ptime = borrowRecord.ptime,
                    opinion = borrowRecord.opinion,
                    status = borrowRecord.status
                )
                borrowRecord["btime"] = borrowRecord["bstime"].strftime("%Y-%m-%d %H:%M:%S") + "  至  " + \
                                        borrowRecord["betime"].strftime("%Y-%m-%d %H:%M:%S")
                del borrowRecord["bstime"]
                del borrowRecord["betime"]
                borrowRecord["stime"] = borrowRecord["stime"].strftime("%Y-%m-%d %H:%M:%S")
                borrowRecord["ptime"] = borrowRecord["ptime"].strftime("%Y-%m-%d %H:%M:%S")
                res.append(borrowRecord)
    
    totalSize = len(res)
    res = res[(page-1)*pageSize:page*pageSize]
    
    return JsonResponse({
        'errcode':0,
        "errmsg":"ok",
        'res':res,
        "totalSize": totalSize
    })



def getManageBorrowRecords(request):
    setOverTime()

    data = json.loads(request.body.decode("utf-8").replace("'", "\""))
    userid = data.get("userid")
    statusList = data.get("statusList")
    userName = data.get("userName")
    fileName = data.get("fileName")
    page = int(data.get("page"))
    pageSize = int(data.get("pageSize"))

    try:
        userObj = User.objects.get(_id=userid, is_active=True)
    except:
        return JsonResponse({
            'errcode':1,
            'errmsg': "can not find your account!"
        })
    
    borrowRecords = BorrowRecords.objects \
        .filter(status__in=statusList, borrow_user__name__contains=userName, borrow_file__name__contains=fileName, is_active=True) \
        .annotate(id=F('_id'), userName=F('borrow_user__name'), fileName=F('borrow_file__name')).order_by("status", "-urge", "stime")
    
    res = []
    for borrowRecord in borrowRecords:
        if borrowRecord.status == 0:
            approvers = list(borrowRecord.approvers.values_list("_id", flat=True))
            if userid in approvers:
                borrowRecord = dict(
                    id = borrowRecord.id,
                    userName = borrowRecord.userName,
                    fileName = borrowRecord.fileName,
                    bstime = borrowRecord.bstime,
                    betime = borrowRecord.betime,
                    stime = borrowRecord.stime,
                    reason = borrowRecord.reason,
                    ptime = borrowRecord.ptime,
                    opinion = borrowRecord.opinion,
                    status = borrowRecord.status,
                    urge = borrowRecord.urge
                )
                borrowRecord["btime"] = borrowRecord["bstime"].strftime("%Y-%m-%d %H:%M:%S") + "  至  " + \
                                        borrowRecord["betime"].strftime("%Y-%m-%d %H:%M:%S")
                del borrowRecord["bstime"]
                del borrowRecord["betime"]
                borrowRecord["stime"] = borrowRecord["stime"].strftime("%Y-%m-%d %H:%M:%S")
                res.append(borrowRecord)
        elif borrowRecord.status in [1, 2, 3, 4, 5]:
            if userid == borrowRecord.real_approver._id:
                borrowRecord = dict(
                    id = borrowRecord.id,
                    userName = borrowRecord.userName,
                    fileName = borrowRecord.fileName,
                    bstime = borrowRecord.bstime,
                    betime = borrowRecord.betime,
                    stime = borrowRecord.stime,
                    reason = borrowRecord.reason,
                    ptime = borrowRecord.ptime,
                    opinion = borrowRecord.opinion,
                    status = borrowRecord.status
                )
                borrowRecord["btime"] = borrowRecord["bstime"].strftime("%Y-%m-%d %H:%M:%S") + "  至  " + \
                                        borrowRecord["betime"].strftime("%Y-%m-%d %H:%M:%S")
                del borrowRecord["bstime"]
                del borrowRecord["betime"]
                borrowRecord["stime"] = borrowRecord["stime"].strftime("%Y-%m-%d %H:%M:%S")
                borrowRecord["ptime"] = borrowRecord["ptime"].strftime("%Y-%m-%d %H:%M:%S")
                res.append(borrowRecord)
    
    totalSize = len(res)
    res = res[(page-1)*pageSize:page*pageSize]
    
    return JsonResponse({
        'errcode':0,
        "errmsg":"ok",
        'res':res,
        "totalSize": totalSize
    })



def handleReturnFile(request):
    borrowRecordId = request.GET.get("borrowRecordId")

    try:
        borrowRecordObj = BorrowRecords.objects.get(_id=borrowRecordId)
    except:
        return JsonResponse({
            'errcode':1,
            'errmsg': "can not find this borrow record!"
        })
    now = datetime.datetime.now()
    borrowRecordObj.etime = now
    borrowRecordObj.status = 4
    borrowRecordObj.save()
    return JsonResponse({
        'errcode':0,
        'errmsg':"ok"
    })



def handleUrgeFile(request):
    borrowRecordId = request.GET.get("borrowRecordId")

    try:
        borrowRecordObj = BorrowRecords.objects.get(_id=borrowRecordId)
    except:
        return JsonResponse({
            'errcode':1,
            'errmsg': "can not find this borrow record!"
        })
    borrowRecordObj.urge = True
    borrowRecordObj.save()
    return JsonResponse({
        'errcode':0,
        'errmsg':"ok"
    })



def handleDeleteBorrowRecord(request):
    borrowRecordId = request.GET.get("borrowRecordId")
    _type = int(request.GET.get("type"))

    try:
        borrowRecord = BorrowRecords.objects.get(_id=borrowRecordId)
    except:
        return JsonResponse({
            'errcode':1,
            'errmsg': "can not find this borrow record!"
        })
    
    if _type == 1:
        borrowRecord.show_user = False
    elif _type == 2:
        borrowRecord.is_active = False
    borrowRecord.save()
    
    return JsonResponse({
        'errcode': 0,
        'errmsg': "ok"
    })



def handleAgreeFile(request):
    borrowRecordId = request.GET.get("borrowRecordId")
    approverId = request.GET.get("approverId")
    approveOpinion = request.GET.get("approveOpinion")

    try:
        borrowRecordObj = BorrowRecords.objects.get(_id=borrowRecordId)
    except:
        return JsonResponse({
            'errcode':1,
            'errmsg': "can not find this borrow record!"
        })
    try:
        approverObj = User.objects.get(_id=approverId, is_active=True)
    except:
        JsonResponse({
            'errcode':1,
            'errmsg':"can not find your account!"
        })

    now = datetime.datetime.now()
    borrowRecordObj.ptime = now
    borrowRecordObj.real_approver = approverObj
    borrowRecordObj.opinion = approveOpinion
    borrowRecordObj.status = 1
    borrowRecordObj.save()
    return JsonResponse({
        'errcode':0,
        'errmsg':"ok"
    })



def handleRefuseFile(request):
    borrowRecordId = request.GET.get("borrowRecordId")
    approverId = request.GET.get("approverId")
    approveOpinion = request.GET.get("approveOpinion")

    try:
        borrowRecordObj = BorrowRecords.objects.get(_id=borrowRecordId)
    except:
        return JsonResponse({
            'errcode':1,
            'errmsg': "can not find this borrow record!"
        })
    try:
        approverObj = User.objects.get(_id=approverId, is_active=True)
    except:
        JsonResponse({
            'errcode':1,
            'errmsg':"can not find your account!"
        })

    now = datetime.datetime.now()
    borrowRecordObj.ptime = now
    borrowRecordObj.real_approver = approverObj
    borrowRecordObj.opinion = approveOpinion
    borrowRecordObj.status = 2
    borrowRecordObj.borrow_user.borrow_count = borrowRecordObj.borrow_user.borrow_count + 1
    borrowRecordObj.borrow_user.save()
    borrowRecordObj.save()
    return JsonResponse({
        'errcode':0,
        'errmsg':"ok"
    })



def handleConfirmFile(request):
    borrowRecordId = request.GET.get("borrowRecordId")

    try:
        borrowRecordObj = BorrowRecords.objects.get(_id=borrowRecordId)
    except:
        return JsonResponse({
            'errcode':1,
            'errmsg': "can not find this borrow record!"
        })
    
    borrowRecordObj.borrow_user.borrow_count = borrowRecordObj.borrow_user.borrow_count + 1
    borrowRecordObj.borrow_user.save()
    borrowRecordObj.status = 5
    borrowRecordObj.save()
    return JsonResponse({
        'errcode':0,
        'errmsg':"ok"
    })



def agreeSelectionRecords(request):
    data = json.loads(request.body.decode("utf-8").replace("'", "\""))
    borrowRecordIds = data.get("borrowRecordIds")
    approverId = data.get("approverId")
    approveOpinion = data.get("approveOpinion")

    borrowRecordObjs = []
    for borrowRecordId in borrowRecordIds:
        try:
            borrowRecordObj = BorrowRecords.objects.get(_id=borrowRecordId)
        except:
            return JsonResponse({
                'errcode':1,
                'errmsg':"can not find one of these borrow records!"
            })
        borrowRecordObjs.append(borrowRecordObj)
    try:
        approverObj = User.objects.get(_id=approverId, is_active=True)
    except:
        JsonResponse({
            'errcode':1,
            'errmsg':"can not find your account!"
        })
    
    now = datetime.datetime.now()
    for borrowRecordObj in borrowRecordObjs:
        borrowRecordObj.ptime = now
        borrowRecordObj.real_approver = approverObj
        borrowRecordObj.opinion = approveOpinion
        borrowRecordObj.status = 1
        borrowRecordObj.save()
    return JsonResponse({
        'errcode':0,
        'errmsg':"ok"
    })



def refuseSelectionRecords(request):
    data = json.loads(request.body.decode("utf-8").replace("'", "\""))
    borrowRecordIds = data.get("borrowRecordIds")
    approverId = data.get("approverId")
    approveOpinion = data.get("approveOpinion")

    borrowRecordObjs = []
    for borrowRecordId in borrowRecordIds:
        try:
            borrowRecordObj = BorrowRecords.objects.get(_id=borrowRecordId)
        except:
            return JsonResponse({
                'errcode':1,
                'errmsg':"can not find one of these borrow records!"
            })
        borrowRecordObjs.append(borrowRecordObj)
    try:
        approverObj = User.objects.get(_id=approverId, is_active=True)
    except:
        JsonResponse({
            'errcode':1,
            'errmsg':"can not find your account!"
        })
    
    now = datetime.datetime.now()
    for borrowRecordObj in borrowRecordObjs:
        borrowRecordObj.ptime = now
        borrowRecordObj.real_approver = approverObj
        borrowRecordObj.opinion = approveOpinion
        borrowRecordObj.status = 2
        borrowRecordObj.borrow_user.borrow_count = borrowRecordObj.borrow_user.borrow_count + 1
        borrowRecordObj.borrow_user.save()
        borrowRecordObj.save()
    return JsonResponse({
        'errcode':0,
        'errmsg':"ok"
    })



def confirmSelectionRecords(request):
    data = json.loads(request.body.decode("utf-8").replace("'", "\""))
    borrowRecordIds = data.get("borrowRecordIds")

    borrowRecordObjs = []
    for borrowRecordId in borrowRecordIds:
        try:
            borrowRecordObj = BorrowRecords.objects.get(_id=borrowRecordId)
        except:
            return JsonResponse({
                'errcode':1,
                'errmsg':"can not find one of these borrow records!"
            })
        borrowRecordObjs.append(borrowRecordObj)
    
    for borrowRecordObj in borrowRecordObjs:
        borrowRecordObj.borrow_user.borrow_count = borrowRecordObj.borrow_user.borrow_count + 1
        borrowRecordObj.borrow_user.save()
        borrowRecordObj.status = 5
        borrowRecordObj.save()
    return JsonResponse({
        'errcode':0,
        'errmsg':"ok"
    })



def deleteSelectionRecords(request):
    data = json.loads(request.body.decode("utf-8").replace("'", "\""))
    borrowRecordIds = data.get("borrowRecordIds")

    borrowRecordObjs = []
    for borrowRecordId in borrowRecordIds:
        try:
            borrowRecordObj = BorrowRecords.objects.get(_id=borrowRecordId)
        except:
            return JsonResponse({
                'errcode':1,
                'errmsg':"can not find one of these borrow records!"
            })
        borrowRecordObjs.append(borrowRecordObj)
    
    for borrowRecordObj in borrowRecordObjs:
        borrowRecordObj.is_active = False
        borrowRecordObj.save()
    return JsonResponse({
        'errcode':0,
        'errmsg':"ok"
    })



def getFilingAudits(request):
    # get请求全是字符串，post请求可以保留数据原类型，注意数据为空时，前端传来的是空字符还是None
    data = json.loads(request.body.decode("utf-8").replace("'", "\""))
    operations = data.get("operations")
    structures = data.get("structures")
    lowerDateTime = data.get("lowerDateTime")
    upperDateTime = data.get("upperDateTime")
    userName = data.get("userName")
    filingName = data.get("filingName")
    page = data.get("page")
    pageSize = data.get("pageSize")

    # 处理筛选条件
    if lowerDateTime is None:
        lowerDateTime = datetime.datetime(1, 1, 1)
    else:
        lowerDateTime = datetime.datetime.strptime(lowerDateTime, "%Y-%m-%d %H:%M:%S")
    if upperDateTime is None:
        upperDateTime = datetime.datetime(9999, 1, 1)
    else:
        upperDateTime = datetime.datetime.strptime(upperDateTime, "%Y-%m-%d %H:%M:%S")
    if len(operations) == 0:
        operations = ["新增", "修改", "删除"]
    if len(structures) == 0:
        structures = [1, 2, 3, 4]

    filingAudits = FilingAudit.objects \
        .filter(operate_user__name__contains=userName, operation__in=operations, level__in=structures, \
                datetime__range=(lowerDateTime, upperDateTime)) \
        .annotate(id=F("_id"), userName=F("operate_user__name"), nameVary=F("name_vary"), \
                    permitUsersVary=F("permit_users_vary"), positionVary=F("position_vary"), remarkVary=F("remark_vary")) \
        .values("id", "level", "filing_id", "userName", "datetime", "operation", "target", "nameVary", \
                "permitUsersVary", "positionVary", "remarkVary")
    
    res = []
    structureTypes = ["项目组", "文件柜", "文件柜格", "文件盒"]
    for filingAudit in filingAudits:
        filingObj = ""
        if filingAudit["level"] == 1:
            try:
                filingObj = ProjectTeam.objects.get(_id=filingAudit["filing_id"])
            except:
                continue
        elif filingAudit["level"] == 2:
            try:
                filingObj = FilingCabinet.objects.get(_id=filingAudit["filing_id"])
            except:
                continue
        elif filingAudit["level"] == 3:
            try:
                filingObj = FilingCase.objects.get(_id=filingAudit["filing_id"])
            except:
                continue
        elif filingAudit["level"] == 4:
            try:
                filingObj = FilingBox.objects.get(_id=filingAudit["filing_id"])
            except:
                continue
        if filingName in filingObj.name:
            if filingAudit["level"] == 1:
                filingAudit["filingPath"] = getFolderPositionUtil(0, 0) + filingObj.name
            else:
                filingAudit["filingPath"] = getFolderPositionUtil(filingAudit["level"]-1, filingObj.position._id) + filingObj.name
            filingAudit["structureType"] = structureTypes[filingAudit["level"]-1]
            filingAudit["datetime"] = filingAudit["datetime"].strftime("%Y-%m-%d %H:%M:%S")
            res.append(filingAudit)
    
    totalSize = len(res)
    res = res[(page-1)*pageSize:page*pageSize]

    return JsonResponse({
        'errcode':0,
        'errmsg': "ok",
        'res': res,
        'totalSize': totalSize
    })




def getFileAudits(request):
    # get请求全是字符串，post请求可以保留数据原类型，注意数据为空时，前端传来的是空字符还是None
    data = json.loads(request.body.decode("utf-8").replace("'", "\""))
    operations = data.get("operations")
    lowerDateTime = data.get("lowerDateTime")
    upperDateTime = data.get("upperDateTime")
    userName = data.get("userName")
    fileName = data.get("fileName")
    page = data.get("page")
    pageSize = data.get("pageSize")

    # 处理筛选条件
    if lowerDateTime is None:
        lowerDateTime = datetime.datetime(1, 1, 1)
    else:
        lowerDateTime = datetime.datetime.strptime(lowerDateTime, "%Y-%m-%d %H:%M:%S")
    if upperDateTime is None:
        upperDateTime = datetime.datetime(9999, 1, 1)
    else:
        upperDateTime = datetime.datetime.strptime(upperDateTime, "%Y-%m-%d %H:%M:%S")
    if len(operations) == 0:
        operations = ["新增", "修改", "删除"]

    fileAudits = FileAudit.objects \
        .filter(operate_user__name__contains=userName, operate_file__name__contains=fileName, operation__in=operations, \
                datetime__range=(lowerDateTime, upperDateTime)) \
        .annotate(id=F("_id"), file_id=F("operate_file___id"), file_name=F("operate_file__name"), userName=F("operate_user__name"), \
                nameVary=F("name_vary"), versionVary=F("version_vary"), positionVary=F("position_vary"), remarkVary=F("remark_vary")) \
        .values("id", "file_id", "file_name", "userName", "datetime", "operation", "target", "nameVary", \
                "versionVary", "positionVary", "remarkVary")
    
    res = []
    for fileAudit in fileAudits:
        fileAudit["filePath"] = getFilePosition(fileAudit["file_id"]) + "/" + fileAudit["file_name"]
        fileAudit["datetime"] = fileAudit["datetime"].strftime("%Y-%m-%d %H:%M:%S")
        res.append(fileAudit)
    
    totalSize = len(res)
    res = res[(page-1)*pageSize:page*pageSize]

    return JsonResponse({
        'errcode':0,
        'errmsg': "ok",
        'res': res,
        'totalSize': totalSize
    })




def exportFilingAudits(request):
    # get请求全是字符串，post请求可以保留数据原类型，注意数据为空时，前端传来的是空字符还是None
    data = json.loads(request.body.decode("utf-8").replace("'", "\""))
    operations = data.get("operations")
    structures = data.get("structures")
    lowerDateTime = data.get("lowerDateTime")
    upperDateTime = data.get("upperDateTime")
    userName = data.get("userName")
    filingName = data.get("filingName")

    # 处理筛选条件
    if lowerDateTime is None:
        lowerDateTime = datetime.datetime(1, 1, 1)
    else:
        lowerDateTime = datetime.datetime.strptime(lowerDateTime, "%Y-%m-%d %H:%M:%S")
    if upperDateTime is None:
        upperDateTime = datetime.datetime(9999, 1, 1)
    else:
        upperDateTime = datetime.datetime.strptime(upperDateTime, "%Y-%m-%d %H:%M:%S")
    if len(operations) == 0:
        operations = ["新增", "修改", "删除"]
    if len(structures) == 0:
        structures = [1, 2, 3, 4]

    filingAudits = FilingAudit.objects \
        .filter(operate_user__name__contains=userName, operation__in=operations, level__in=structures, \
                datetime__range=(lowerDateTime, upperDateTime)) \
        .annotate(id=F("_id"), userName=F("operate_user__name"), nameVary=F("name_vary"), \
                    permitUsersVary=F("permit_users_vary"), positionVary=F("position_vary"), remarkVary=F("remark_vary")) \
        .values("id", "level", "filing_id", "userName", "datetime", "operation", "target", "nameVary", \
                "permitUsersVary", "positionVary", "remarkVary")
    
    res = []
    structureTypes = ["项目组", "文件柜", "文件柜格", "文件盒"]
    for filingAudit in filingAudits:
        filingObj = ""
        if filingAudit["level"] == 1:
            try:
                filingObj = ProjectTeam.objects.get(_id=filingAudit["filing_id"])
            except:
                continue
        elif filingAudit["level"] == 2:
            try:
                filingObj = FilingCabinet.objects.get(_id=filingAudit["filing_id"])
            except:
                continue
        elif filingAudit["level"] == 3:
            try:
                filingObj = FilingCase.objects.get(_id=filingAudit["filing_id"])
            except:
                continue
        elif filingAudit["level"] == 4:
            try:
                filingObj = FilingBox.objects.get(_id=filingAudit["filing_id"])
            except:
                continue
        if filingName in filingObj.name:
            if filingAudit["level"] == 1:
                filingAudit["filingPath"] = getFolderPositionUtil(0, 0) + filingObj.name
            else:
                filingAudit["filingPath"] = getFolderPositionUtil(filingAudit["level"]-1, filingObj.position._id) + filingObj.name
            filingAudit["structureType"] = structureTypes[filingAudit["level"]-1]
            filingAudit["datetime"] = filingAudit["datetime"].strftime("%Y-%m-%d %H:%M:%S")
            res.append(filingAudit)

    response = HttpResponse(content_type='text/csv')
    response.write(codecs.BOM_UTF8)
    filingAuditKeys = ['userName', 'operation', 'structureType', 'filingPath', 'datetime', 'target', 'nameVary', \
                        'permitUsersVary', 'positionVary', 'remarkVary']
    writer = csv.DictWriter(response, fieldnames=filingAuditKeys, extrasaction='ignore')
    writer.writerow({
        'userName':'操作人',
        'operation':'操作类型',
        'structureType':'结构类型',
        'filingPath':'当前结构路径',
        'datetime':'操作时间',
        'target':'操作对象',
        'nameVary':"名称变化",
        'permitUsersVary':"开放权限的用户变化",
        'positionVary':"位置变化",
        'remarkVary':"备注变化"
    })
    for row in res:
        writer.writerow(row)

    return response




def exportFileAudits(request):
    # get请求全是字符串，post请求可以保留数据原类型，注意数据为空时，前端传来的是空字符还是None
    data = json.loads(request.body.decode("utf-8").replace("'", "\""))
    operations = data.get("operations")
    lowerDateTime = data.get("lowerDateTime")
    upperDateTime = data.get("upperDateTime")
    userName = data.get("userName")
    fileName = data.get("fileName")

    # 处理筛选条件
    if lowerDateTime is None:
        lowerDateTime = datetime.datetime(1, 1, 1)
    else:
        lowerDateTime = datetime.datetime.strptime(lowerDateTime, "%Y-%m-%d %H:%M:%S")
    if upperDateTime is None:
        upperDateTime = datetime.datetime(9999, 1, 1)
    else:
        upperDateTime = datetime.datetime.strptime(upperDateTime, "%Y-%m-%d %H:%M:%S")
    if len(operations) == 0:
        operations = ["新增", "修改", "删除"]

    fileAudits = FileAudit.objects \
        .filter(operate_user__name__contains=userName, operate_file__name__contains=fileName, operation__in=operations, \
                datetime__range=(lowerDateTime, upperDateTime)) \
        .annotate(id=F("_id"), file_id=F("operate_file___id"), file_name=F("operate_file__name"), userName=F("operate_user__name"), \
                nameVary=F("name_vary"), versionVary=F("version_vary"), positionVary=F("position_vary"), remarkVary=F("remark_vary")) \
        .values("id", "file_id", "file_name", "userName", "datetime", "operation", "target", "nameVary", \
                "versionVary", "positionVary", "remarkVary")
    
    res = []
    for fileAudit in fileAudits:
        fileAudit["filePath"] = getFilePosition(fileAudit["file_id"]) + "/" + fileAudit["file_name"]
        fileAudit["datetime"] = fileAudit["datetime"].strftime("%Y-%m-%d %H:%M:%S")
        res.append(fileAudit)

    response = HttpResponse(content_type='text/csv')
    response.write(codecs.BOM_UTF8)
    fileAuditKeys = ['userName', 'operation', 'filePath', 'datetime', 'target', 'nameVary', 'versionVary', 'positionVary', 'remarkVary']
    writer = csv.DictWriter(response, fieldnames=fileAuditKeys, extrasaction='ignore')
    writer.writerow({
        'userName':'操作人',
        'operation':'操作类型',
        'filePath':'当前文件路径',
        'datetime':'操作时间',
        'target':'操作对象',
        'nameVary':"名称变化",
        'versionVary':"文件版本变化",
        'positionVary':"位置变化",
        'remarkVary':"备注变化"
    })
    for row in res:
        writer.writerow(row)

    return response














