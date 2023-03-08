from django.db.backends.mysql.base import DatabaseFeatures # 关键设置
DatabaseFeatures.supports_microsecond_precision = False # 关键设置
from django.db import models
from django.db.models import *
from User.models import User

# Create your models here.

class ProjectTeam(models.Model):
    _id = AutoField("项目组编号", primary_key=True, db_column="id")
    name = CharField("项目组名称", max_length=255)
    remark = CharField("备注", max_length=255, null=True)
    managers = ManyToManyField(
        User,
        related_name='manage_project_team',
        through='ProjectTeamManagers',
        through_fields=('project_team', 'manager')
    )

    def __str__(self):
        return self._id + "——" + self.name

    class Meta:
        db_table = "dms_project_teams"



class ProjectTeamManagers(models.Model):
    _id = AutoField("项目组管理员映射编号", primary_key=True, db_column="id")
    project_team = ForeignKey(ProjectTeam, on_delete=models.CASCADE, null=True)
    manager = ForeignKey(User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.project_team.name + "项目组的管理员是：" + self.manager.name

    class Meta:
        db_table = "dms_project_team_managers"



class FilingCabinet(models.Model):
    _id = AutoField("文件柜编号", primary_key=True, db_column="id")
    name = CharField("文件柜名称", max_length=255)
    position = ForeignKey(ProjectTeam, related_name="filingcabinets", on_delete=models.CASCADE, null=True)
    remark = CharField("备注", max_length=255, null=True)
    managers = ManyToManyField(
        User,
        related_name='manage_cabinets',
        through='CabinetsManagers',
        through_fields=('cabinet', 'manager')
    )

    def __str__(self):
        return self.position.name + "/" + self.name

    class Meta:
        db_table = "dms_filing_cabinets"



class CabinetsManagers(models.Model):
    _id = AutoField("文件柜管理员映射编号", primary_key=True, db_column="id")
    cabinet = ForeignKey(FilingCabinet, on_delete=models.CASCADE, null=True)
    manager = ForeignKey(User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.cabinet.name + "文件柜的管理员是：" + self.manager.name

    class Meta:
        db_table = "dms_cabinets_managers"



class FilingCase(models.Model):
    _id = AutoField("文件柜格编号", primary_key=True, db_column="id")
    name = CharField("文件柜格名称", max_length=255)
    _type = CharField("柜格类型", max_length=255, db_column="type")
    position = ForeignKey(FilingCabinet, related_name="filingcases", on_delete=models.CASCADE, null=True)
    remark = CharField("备注", max_length=255, null=True)
    managers = ManyToManyField(
        User,
        related_name='manage_cases',
        through='CasesManagers',
        through_fields=('case', 'manager')
    )
    permission_users = ManyToManyField(
        User,
        related_name="permit_cases",
        through='CasesPermissions',
        through_fields=('case', 'user')
    )

    def __str__(self):
        return self.position.name + "/" + self.name + " , type:" + self._type

    class Meta:
        db_table = "dms_filing_cases"



class CasesManagers(models.Model):
    _id = AutoField("文件柜格管理员映射编号", primary_key=True, db_column="id")
    case = ForeignKey(FilingCase, on_delete=models.CASCADE, null=True)
    manager = ForeignKey(User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.case.name + "文件柜格的管理员是：" + self.manager.name

    class Meta:
        db_table = "dms_cases_managers"



class CasesPermissions(models.Model):
    _id = AutoField("文件柜格和开放权限用户映射编号", primary_key=True, db_column="id")
    case = ForeignKey(FilingCase, on_delete=models.CASCADE, null=True)
    user = ForeignKey(User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.user.name + "可以免审批借阅" + self.case.name + "文件柜格中的文件"

    class Meta:
        db_table = "dms_cases_permissions"



class FilingBox(models.Model):
    _id = AutoField("文件盒编号", primary_key=True, db_column="id")
    name = CharField("文件盒名称", max_length=255)
    position = ForeignKey(FilingCase, related_name="filingboxes", on_delete=models.CASCADE, null=True)
    remark = CharField("备注", max_length=255, null=True)
    is_active = BooleanField("是否存活", default=1)

    def __str__(self):
        return self.position.name + "/" + self.name

    class Meta:
        db_table = "dms_filing_boxes"



class File(models.Model):
    _id = AutoField("文件编号", primary_key=True, db_column="id")
    name = CharField("文件名称", max_length=255)
    superior_type = BooleanField("上层位置类型", default=0)
    position = IntegerField("上层位置编号", null=True)
    creator = ForeignKey(User, related_name="files", on_delete=models.CASCADE, null=True)
    datetime = DateTimeField("创建时间", auto_now_add=True)
    remark = CharField("备注", max_length=255, null=True)
    _type = CharField("文件类型", max_length=255, db_column="type")
    url = CharField("存放路径", max_length=255, null=True)
    current_version_id = IntegerField("版本编号", null=True)
    is_active = BooleanField("是否存活", default=1)

    def __str__(self):
        return self.creator.name + "在" + str(self.datetime) + "时刻创建了:" + self.name + "(" + self._type + ")"

    class Meta:
        db_table = "dms_files"



class FileVersions(models.Model):
    _id = AutoField("版本编号", primary_key=True, db_column="id")
    file = ForeignKey(File, related_name="versions", on_delete=models.CASCADE, null=True)
    description = CharField("版本描述", max_length=255, null=True)
    is_active = BooleanField("是否存活", default=1)

    def __str__(self):
        return self.file.name + "文件的一个版本：" + self.description

    class Meta:
        db_table = "dms_file_versions"



class BorrowRecords(models.Model):
    _id = AutoField("借阅编号", primary_key=True, db_column="id")
    borrow_user = ForeignKey(User, related_name="borrowrecords", on_delete=models.CASCADE, null=True)
    borrow_file = ForeignKey(File, related_name="borrowrecords", on_delete=models.CASCADE, null=True)
    borrow_version_id = IntegerField("借阅时的版本编号", null=True)
    reason = CharField("借阅事由", max_length=255, null=True)
    bstime = DateTimeField("借阅起始时间", null=True)
    betime = DateTimeField("借阅结束时间", null=True)
    stime = DateTimeField("借阅记录创建时间", auto_now_add=True)
    real_approver = ForeignKey(User, related_name="approverecords", on_delete=models.CASCADE, null=True)
    ptime = DateTimeField("审批时间", null=True)
    etime = DateTimeField("归还时间", null=True)
    remark = CharField("备注", max_length=255, null=True)
    opinion = CharField("审批意见", max_length=255, null=True)
    status = IntegerField("借阅记录状态", default=0)
    urge = BooleanField("是否催办", default=0)
    show_user = BooleanField("是否展示给员工", default=1)
    is_active = BooleanField("是否存活", default=1)
    approvers = ManyToManyField(
        User,
        related_name="approve_records",
        through='BorrowApprovers',
        through_fields=('borrow_record', 'approver')
    )
    notifyers = ManyToManyField(
        User,
        related_name="notify_records",
        through='BorrowNotifyers',
        through_fields=('borrow_record', 'notifyer')
    )

    def __str__(self):
        return self.borrow_user.name + "借了" + self.borrow_file.name + "文件, 状态：" + str(self.status)

    class Meta:
        db_table = "dms_borrow_records"



class BorrowApprovers(models.Model):
    _id = AutoField("借阅记录和审批人映射编号", primary_key=True, db_column="id")
    borrow_record = ForeignKey(BorrowRecords, on_delete=models.CASCADE, null=True)
    approver = ForeignKey(User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.borrow_record.__str__() + ", 审批人为：" + self.approver.name

    class Meta:
        db_table = "dms_borrow_approvers"



class BorrowNotifyers(models.Model):
    _id = AutoField("借阅记录和抄送人映射编号", primary_key=True, db_column="id")
    borrow_record = ForeignKey(BorrowRecords, on_delete=models.CASCADE, null=True)
    notifyer = ForeignKey(User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.borrow_record.__str__() + ", 抄送人为：" + self.notifyer.name

    class Meta:
        db_table = "dms_borrow_notifyers"



class FilingAudit(models.Model):
    _id = AutoField("文件柜台账编号", primary_key=True, db_column="id")
    level = IntegerField("文件柜结构的层次", default=1)
    filing_id = IntegerField("文件柜结构的编号", default=1)
    operate_user = ForeignKey(User, on_delete=models.CASCADE, null=True)
    datetime = DateTimeField("操作时间", auto_now_add=True)
    operation = CharField("操作类型", max_length=255, null=True)
    target = CharField("当时的操作对象", max_length=255, null=True)
    name_vary = CharField("名称的变化", max_length=255, null=True)
    permit_users_vary = CharField("开启权限用户的变化", max_length=255, null=True)
    position_vary = CharField("位置的变化", max_length=255, null=True)
    remark_vary = CharField("备注的变化", max_length=255, null=True)

    def __str__(self):
            return self.operate_user.name + self.operation + "了" + str(self.level) + "层次中的" + str(self.filing_id) + "号文件柜结构"

    class Meta:
        db_table = "dms_filing_audit"
    


class FileAudit(models.Model):
    _id = AutoField("文件台账编号", primary_key=True, db_column="id")
    operate_file = ForeignKey(File, on_delete=models.CASCADE, null=True)
    operate_user = ForeignKey(User, on_delete=models.CASCADE, null=True)
    datetime = DateTimeField("操作时间", auto_now_add=True)
    operation = CharField("操作类型", max_length=255, null=True)
    target = CharField("当时的操作对象", max_length=255, null=True)
    name_vary = CharField("名称的变化", max_length=255, null=True)
    version_vary = CharField("文件版本的变化", max_length=255, null=True)
    position_vary = CharField("位置的变化", max_length=255, null=True)
    remark_vary = CharField("备注的变化", max_length=255, null=True)

    def __str__(self):
            return self.operate_user.name + self.operation + "了" + self.operate_file.name

    class Meta:
        db_table = "dms_file_audit"
