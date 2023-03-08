from django.db.models import *
from User.models import *
from File.models import *
import datetime
import pandas as pd
import re



# 判断该文件是否已借出
def judgeFilePermission(fileid, userid):
    if len(BorrowRecords.objects.filter(borrow_file___id=fileid, borrow_user___id=userid, status=1, show_user=True)) > 0:
        return 1
    elif len(BorrowRecords.objects.filter(borrow_file___id=fileid, borrow_user___id=userid, status=0, show_user=True)) > 0:
        return 2
    elif len(BorrowRecords.objects.filter(borrow_file___id=fileid, borrow_user___id=userid, status=3, show_user=True)) > 0:
        return 3
    elif len(BorrowRecords.objects.filter(borrow_file___id=fileid, borrow_user___id=userid, status=4, show_user=True)) > 0:
        return 4
    else:
        return 0
      


# 获取指定文件从项目组开始的层次位置
def getFilePosition(fileid):
    try:
        file = File.objects.get(_id=fileid)
    except:
        return ""
    
    positionList = []
    if file.superior_type:
        try:
            case = FilingCase.objects.get(_id=file.position)
        except:
            return ""
        positionList.insert(0, case.name)
        positionList.insert(0, case.position.name)
        positionList.insert(0, case.position.position.name)
    else:
        try:
            box = FilingBox.objects.get(_id=file.position)
        except:
            return ""
        positionList.insert(0, box.name)
        positionList.insert(0, box.position.name)
        positionList.insert(0, box.position.position.name)
        positionList.insert(0, box.position.position.position.name)
    
    return "/".join(positionList)


# 获取从项目组开始的层次位置
def getFolderPositionUtil(level, _id):
    positionList = []
    if level == 1:
        try:
            projectTeam = ProjectTeam.objects.get(_id=_id)
        except:
            return ""
        positionList.insert(0, projectTeam.name)
    
    elif level == 2:
        try:
            cabinet = FilingCabinet.objects.get(_id=_id)
        except:
            return ""
        positionList.insert(0, cabinet.name)
        positionList.insert(0, cabinet.position.name)
    elif level == 3:
        try:
            case = FilingCase.objects.get(_id=_id)
        except:
            return ""
        positionList.insert(0, case.name)
        positionList.insert(0, case.position.name)
        positionList.insert(0, case.position.position.name)
    elif level == 4:
        try:
            box = FilingBox.objects.get(_id=_id)
        except:
            return ""
        positionList.insert(0, box.name)
        positionList.insert(0, box.position.name)
        positionList.insert(0, box.position.position.name)
        positionList.insert(0, box.position.position.position.name)
    
    return "/".join(positionList) + "/"


# 获得从项目组开始的层次位置对象列表
def getFolderPositionObj(level, _id):
    positionList = []
    if level == 1:
        try:
            projectTeam = ProjectTeam.objects.get(_id=_id)
        except:
            return ""
        positionList.insert(0, {"id": projectTeam._id, "name": projectTeam.name})
    elif level == 2:
        try:
            cabinet = FilingCabinet.objects.get(_id=_id)
        except:
            return ""
        positionList.insert(0, {"id": cabinet._id, "name": cabinet.name})
        positionList.insert(0, {"id": cabinet.position._id, "name": cabinet.position.name})
    elif level == 3:
        try:
            case = FilingCase.objects.get(_id=_id)
        except:
            return ""
        positionList.insert(0, {"id": case._id, "name": case.name})
        positionList.insert(0, {"id": case.position._id, "name": case.position.name})
        positionList.insert(0, {"id": case.position.position._id, "name": case.position.position.name})
    else:
        try:
            box = FilingBox.objects.get(_id=_id, is_active=True)
        except:
            return ""
        positionList.insert(0, {"id": box._id, "name": box.name})
        positionList.insert(0, {"id": box.position._id, "name": box.position.name})
        positionList.insert(0, {"id": box.position.position._id, "name": box.position.position.name})
        positionList.insert(0, {"id": box.position.position.position._id, "name": box.position.position.position.name})
    return positionList



# 获得指定文件的所有版本
def getAllVersionsOfFile(fileId):
    versions = list(FileVersions.objects.filter(file___id=fileId, is_active=True).annotate(id=F("_id")).values("id", "description"))
    return versions



# 获得指定文件的当前版本对象
def getFileVersion(versionId):
    version = FileVersions.objects.filter(_id=versionId, is_active=True).annotate(id=F("_id")).values("id", "description")
    if len(version) == 0:
        return {}
    else:
        return version[0]



# 将文件夹打包成zip的工具类
import os
import zipstream
class ZipUtility(object):
    """
    将文件或者文件夹打包成ZIP格式的文件，然后下载，在后台可以通过response完成下载
    """
    zip_file = None

    def __init__(self):
        self.zip_file = zipstream.ZipFile(mode='w', compression=zipstream.ZIP_DEFLATED)

    def toZip(self, file, name):
        if os.path.isfile(file):
            self.zip_file.write(file, arcname=os.path.basename(file))
        else:
            self.addFolderToZip(file, name)

    def addFolderToZip(self, folder, name):
        for file in os.listdir(folder):
            full_path = os.path.join(folder, file)
            if os.path.isfile(full_path):
                self.zip_file.write(
                    full_path,
                    arcname=os.path.join(name, os.path.basename(full_path))
                )
            elif os.path.isdir(full_path):
                self.addFolderToZip(
                    full_path,
                    os.path.join(name, os.path.basename(full_path))
                )

    def close(self):
        if self.zip_file:
            self.zip_file.close()



import win32com.client as wc   # doc转docx用
from pydocx import PyDocX      # docx转html用
import pythoncom
'''
doc文件转docx文件
fullpath:路径+文件名(不带后缀)
如：D:\\test\\文件1
'''
def doc2docx(fullpath):
    pythoncom.CoInitialize()
    word = wc.Dispatch("WORD.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    doc = word.Documents.Open(fullpath + '.doc')
    doc.SaveAs(fullpath,12, False, "", True, "", False, False, False, False)
    doc.Close()
    word.Quit()
    pythoncom.CoUninitialize()
 
'''
docx转html
fullpath:路径+文件名(不带后缀)
如：D:\\test\\文件2
'''
def docx2html(fullpath):
    html = PyDocX.to_html(fullpath + ".docx")
    return html

def doc2html(fullpath):
    doc2docx(fullpath)
    html = docx2html(fullpath)
    os.remove(fullpath + ".docx")
    return html

def word2html(fileName):
    ext = fileName.split('.')[-1].lower()
    print(ext)
    if ext != "doc" and ext != "docx":
        print("yes")
        return None
    else:
        if ext == "doc":
            return doc2html(os.path.splitext(fileName)[0])
        else:
            return docx2html(os.path.splitext(fileName)[0])
    
    

# from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
# from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer,Table,TableStyle,PageBreak
# from reportlab.pdfbase import pdfmetrics
# from reportlab.lib import colors
# from reportlab.pdfbase.ttfonts import TTFont
# pdfmetrics.registerFont(TTFont('hei', 'SIMHEI.TTF'))
# from reportlab.lib.pagesizes import A4
# # excel文件转换成pdf格式的文件
# def excel2pdf(fileFullName):
    ext = fileFullName.split('.')[-1].lower()
    df = None
    if ext == "xls":
        df = pd.read_excel(fileFullName, keep_default_na=False)
    elif ext == "xlsx":
        df = pd.read_excel(fileFullName, keep_default_na=False, engine='openpyxl')
    else:
        return None
    
    tableShape = df.shape
    arrList = df.values.tolist()
    print(tableShape)
    print(arrList)
    print(type(arrList))

    doc = SimpleDocTemplate(
        os.path.split(fileFullName)[1].split('.')[0] + ".pdf",
        pagesize=(A4[1],A4[0]),
        topMargin = 15,
        bottomMargin = 15
    )
    elements = []

    #定义样式列表，其中每元组包括样式命令词、样式应用起始单元坐标、样式应用结束单元坐标和样式值。（具体样式命令词请叁阅官方文档）
    style_list = [
        ('BOTTOMPADDING',(0,0),(-1,-1),2),
        ('TOPPADDING',(0,0),(-1,-1),2),
        ('FONTNAME', (0, 0), (-1, -1), 'hei'),  # 字体
        # ('FONTSIZE', (0, 0), (2, 0), 8),  # 第一行的字体大小
        ('FONTSIZE', (0, 1), (-1, -1), 8),  # 第二行到最后一行的字体大小
        # ('ALIGN', (0, 0), (2, 0), 'CENTER'),  # 第一行左右中间对齐
        ('ALIGN', (0, 1), (-1, -1), 'LEFT'),  # 第二行到最后一行左右左对齐
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # 所有表格上下居中对齐
        # ('SPAN', (0, 1), (0, 2)),  # 合并第一列二三行
        # ('SPAN', (0, 3), (0, 4)),  # 合并第一列三四行
        # ('SPAN', (0, 5), (0, 6)),  # 合并第一列五六行
        # ('SPAN', (0, 7), (0, 8)),  # 合并第一列五六行
        # ('BACKGROUND', (0, 0), (2, 0), colors.lightslategray),  # 设置第一行背景颜色
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.darkslategray),  # 设置表格内文字颜色
        ('GRID', (0, 0), (-1, -1), 0.1, colors.slategray)  # 设置表格框线为灰色，线宽为0.1   
    ]
    #创建表格样式对象
    mytab_style = TableStyle(style_list)
    #创建表格
    mytable = Table(arrList, colWidths=[150]*tableShape[1])
    # 将样式应用到表格
    mytable.setStyle(mytab_style)
    # 将表格添加到list：elements中
    elements.append(mytable)
    # 生成文档
    doc.build(elements)
    print(doc)
    print(type(doc))
    print(dir(doc))
    return doc




# excel文件转换成html格式的文件
def excel2pdf(fileFullName):
    ext = fileFullName.split('.')[-1].lower()
    df = None
    if ext == "xls":
        df = pd.read_excel(fileFullName, keep_default_na=False)
    elif ext == "xlsx":
        df = pd.read_excel(fileFullName, keep_default_na=False, engine='openpyxl')
    else:
        return None

    file = df.to_html(index=False, justify='center', bold_rows=True, border=1, col_space=100)
    file = file.replace('class', 'cellspacing=\"0\" class')
    title = "Excel文件预览"
    file = file.replace(
        'class="dataframe">',
        'class="dataframe"><caption>{}</caption>'.format(title)
    )
    file = file.replace('<td>', '<td align="center">')
    pattern = re.compile(r'>Unnamed:.*</th>')
    file = re.sub(pattern, '></th>', file)
    return file




# import os
# from win32com.client import Dispatch,DispatchEx
# from win32com.client import constants
# from win32com.client import gencache
# import re
# import pythoncom
# import shutil
# #class类封装方法，面向对象开发
# class PDFConverter:
    #每个类中都会有的 __init__()这里是指本类的构造方法
    #将一些需要的代码和数据在类对象创建的时候进行处理操作
    def __init__(self):
        #这里是提供的可以识别的文件，后缀名分别为 doc，docx，xls，xlsx
        self._handle_postfix = ['doc', 'docx', 'xls', 'xlsx']
 
    #分离判断文件后缀名的方法
    def _is_legal_postfix(self, filename):
        return filename.split('.')[-1].lower() in self._handle_postfix and not os.path.basename(filename).startswith('~')

    
    def run(self, filename):
        if self._is_legal_postfix(filename):
            ext = filename.split('.')[-1].lower()
            if ext == "doc":
                return self.doc(filename)
            elif ext == "docx":
                return self.docx(filename)
            elif ext == "xls":
                return self.xls(filename)
            elif ext == "xlsx":
                return self.xlsx(filename)
        else:
            return None
 
    #这里是主要的转换的方法是针对于doc或者是docx文件
    def doc(self, filename):
        '''
        doc 和 docx 文件转换
        '''
        #这句话是获取文件名，具体是因为需要使用原的文件名作为新生产的文件的名称
        name = os.path.basename(filename).split('.')[0] + '.pdf'
        #设置保存的文件
        tmp_export_folder = os.path.join(os.path.split(filename)[0], "export")
        if not os.path.exists(tmp_export_folder):
            os.mkdir(tmp_export_folder, 755)
        exportfile = os.path.join(tmp_export_folder, name)

        pythoncom.CoInitialize()
        word = DispatchEx("Word.Application")
        worddoc = word.Documents.Open(filename, ReadOnly=1)
        worddoc.SaveAs(exportfile, FileFormat=17)
        worddoc.Close()
        word.Quit()
        pythoncom.CoUninitialize()

        with open(exportfile, 'rb') as f:
            file = f.read()
        return file


    #这里一样因为doc和docx同为word文档
    #self 这里看来好像和this很像，应该是代表本对象本类
    def docx(self, filename):
        self.doc(filename)
    
    #这是针对于xls的方式的转换
    def xls(self, filename):
        '''
        xls 和 xlsx 文件转换
        '''
        name = os.path.basename(filename).split('.')[0] + '.pdf'
        #设置保存的文件
        tmp_export_folder = os.path.join(os.path.split(filename)[0], "export")
        if not os.path.exists(tmp_export_folder):
            os.mkdir(tmp_export_folder, 755)
        exportfile = os.path.join(tmp_export_folder, name)

        pythoncom.CoInitialize()
        xlApp = DispatchEx("Excel.Application")
        xlApp.Visible = False
        xlApp.DisplayAlerts = 0
        books = xlApp.Workbooks.Open(filename, False)
        books.ExportAsFixedFormat(0, exportfile)
        books.Close(False)
        xlApp.Quit()

        file = open(exportfile, 'rb')
        return file
 
    def xlsx(self, filename):
        self.xls(filename)



def setOverTime():
    now = datetime.datetime.now()

    borrowRecords = BorrowRecords.objects.filter(status=1, betime__lte=now, show_user=True)
    borrowRecords.update(status=3)



def addNewFilingAudit(level, operateUser, operation, newFilingObj=None, oldFilingObj=None, newPermitUsers=[], oldPermitUsers=[]):
    if operation == "新增":
        target = ""
        if level == 1:
            target = getFolderPositionUtil(0, 0) + newFilingObj.name
        else:
            target = getFolderPositionUtil(level-1, newFilingObj.position._id) + newFilingObj.name
        
        FilingAudit.objects.create(
            level = level,
            filing_id = newFilingObj._id,
            operate_user = operateUser,
            operation = operation,
            target = target
        )    

    elif operation == "删除":
        target = ""
        if level == 1:
            target = getFolderPositionUtil(0, 0) + oldFilingObj.name
        else:
            target = getFolderPositionUtil(level-1, oldFilingObj.position._id) + oldFilingObj.name
        
        FilingAudit.objects.create(
            level = level,
            filing_id = oldFilingObj._id,
            operate_user = operateUser,
            operation = operation,
            target = target
        ) 

    elif operation == "修改":
        nameVary = None
        remarkVary = None
        permitUsersVary = None
        positionVary = None
        target = ""
        if level == 1:
            target = getFolderPositionUtil(0, 0) + oldFilingObj.name
        else:
            target = getFolderPositionUtil(level-1, oldFilingObj.position._id) + oldFilingObj.name
        
        if level == 1:
            if newFilingObj.name != oldFilingObj.name:
                nameVary = oldFilingObj.name + "  ————>  " + newFilingObj.name
            if newFilingObj.remark != oldFilingObj.remark:
                remarkVary = str(oldFilingObj.remark) + "  ————>  " + str(newFilingObj.remark)
        elif level == 2:
            if newFilingObj.name != oldFilingObj.name:
                nameVary = oldFilingObj.name + "  ————>  " + newFilingObj.name
            if newFilingObj.remark != oldFilingObj.remark:
                remarkVary = str(oldFilingObj.remark) + "  ————>  " + str(newFilingObj.remark)
        elif level == 3:
            print("filingAudit 3")
            if newFilingObj.name != oldFilingObj.name:
                nameVary = oldFilingObj.name + "  ————>  " + newFilingObj.name
            if newFilingObj.remark != oldFilingObj.remark:
                remarkVary = str(oldFilingObj.remark) + "  ————>  " + str(newFilingObj.remark)

            if newPermitUsers != oldPermitUsers:
                permitUsersVary = ",".join(oldPermitUsers) + "  ————>  " + ",".join(newPermitUsers)
        elif level == 4:
            if newFilingObj.name != oldFilingObj.name:
                nameVary = oldFilingObj.name + "  ————>  " + newFilingObj.name
            if newFilingObj.remark != oldFilingObj.remark:
                remarkVary = str(oldFilingObj.remark) + "  ————>  " + str(newFilingObj.remark)
            if newFilingObj.position != oldFilingObj.position:
                positionVary = getFolderPositionUtil(level-1, oldFilingObj.position._id) + "  ————>  " + getFolderPositionUtil(level-1, newFilingObj.position._id)

        FilingAudit.objects.create(
            level = level,
            filing_id = newFilingObj._id,
            operate_user = operateUser,
            operation = operation,
            target = target,
            name_vary = nameVary,
            permit_users_vary = permitUsersVary,
            position_vary = positionVary,
            remark_vary = remarkVary
        ) 




def addNewFileAudit(operateUser, operation, newFileObj=None, oldFileObj=None):
    if operation == "新增":
        target = getFilePosition(newFileObj._id) + "/" + newFileObj.name
        FileAudit.objects.create(
            operate_file = newFileObj,
            operate_user = operateUser,
            operation = operation,
            target = target
        )    

    elif operation == "删除":
        target = getFilePosition(oldFileObj._id) + "/" + oldFileObj.name
        FileAudit.objects.create(
            operate_file = oldFileObj,
            operate_user = operateUser,
            operation = operation,
            target = target
        ) 

    elif operation == "修改":
        nameVary = None
        remarkVary = None
        versionVary = None
        positionVary = None
        target = getFilePosition(oldFileObj._id) + "/" + oldFileObj.name

        if newFileObj.name != oldFileObj.name:
            nameVary = oldFileObj.name + "  ————>  " + newFileObj.name
        if newFileObj.remark != oldFileObj.remark:
            remarkVary = str(oldFileObj.remark) + "  ————>  " + str(newFileObj.remark)
        if newFileObj.superior_type != oldFileObj.superior_type or (newFileObj.superior_type == oldFileObj.superior_type and newFileObj.position != oldFileObj.position):
            positionVary = getFilePosition(oldFileObj._id) + "  ————>  " + getFilePosition(newFileObj._id)
        if newFileObj.current_version_id != oldFileObj.current_version_id:
            try:
                oldFileVersiondescription = FileVersions.objects.get(_id=oldFileObj.current_version_id).description
            except:
                oldFileVersiondescription = ""
            try:
                newFileVersiondescription = FileVersions.objects.get(_id=newFileObj.current_version_id).description
            except:
                newFileVersiondescription = ""
            versionVary = str(oldFileVersiondescription) + "  ————>  " + str(newFileVersiondescription)

        FileAudit.objects.create(
            operate_file = newFileObj,
            operate_user = operateUser,
            operation = operation,
            target = target,
            name_vary = nameVary,
            version_vary = versionVary,
            position_vary = positionVary,
            remark_vary = remarkVary
        )


            



