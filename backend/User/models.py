from django.db.backends.mysql.base import DatabaseFeatures # 关键设置
DatabaseFeatures.supports_microsecond_precision = False # 关键设置
from django.db import models
from django.db.models import *

# Create your models here.
class Permission(models.Model):
    _id = IntegerField("权限编号", primary_key=True, db_column="id")
    description = CharField("权限描述", max_length=255)

    def __str__(self):
        return str(self._id) + "——" + self.description

    class Meta:
        db_table = "dms_permissions"



class Role(models.Model):
    _id = AutoField("角色编号", primary_key=True, db_column="id")
    name = CharField("角色名称", max_length=255)
    borrow_total_count = IntegerField("该角色可借阅总量", default=0)
    permissions = ManyToManyField(
        Permission,
        related_name="roles",
        through='PermissionAssignment',
        through_fields=('role', 'permission')
    )

    def __str__(self):
        return str(self._id) + "——" + self.name

    class Meta:
        db_table = "dms_roles"



class PermissionAssignment(models.Model):
    _id = AutoField("权限分配映射编号", primary_key=True, db_column="id")
    role = ForeignKey(Role, on_delete=models.CASCADE, null=True)
    permission = ForeignKey(Permission, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.role.name + "——" + self.permission.description

    class Meta:
        db_table = "dms_permission_assignment"



class Department(models.Model):
    _id = AutoField("部门编号", primary_key=True, db_column="id")
    name = name = CharField("部门名称", max_length=255)

    def __str__(self):
        return self._id + " " + self.name

    class Meta:
        db_table = "dms_departments"



class User(models.Model):
    _id = CharField("工号", max_length=255, primary_key=True, db_column="id")
    password = CharField("密码", max_length=255)
    wechat = CharField("微信号", max_length=255, null=True)
    wechat_id = CharField("微信唯一编号", max_length=255, null=True)
    name = CharField("姓名", max_length=255, null=True)
    dept = ForeignKey(Department, related_name='workers', on_delete=models.CASCADE, null=True)
    role = ForeignKey(Role, related_name='users', on_delete=models.CASCADE, null=True)
    phone = CharField("电话号码", max_length=255, null=True)
    email = CharField("电子邮箱", max_length=255, null=True)
    borrow_count = IntegerField("可借阅次数", default=0)
    avatar_url = CharField("头像地址", max_length=255, null=True)
    face_verification = BooleanField("是否人脸认证了", default=0)
    is_active = BooleanField("是否存活", default=1)

    def __str__(self):
        return "工号：" + str(self._id) + ", 姓名：" + self.name

    class Meta:
        db_table = "dms_users"



class EmailVerificationCode(models.Model):
    _id = AutoField("邮箱分配验证码记录的编号", primary_key=True, db_column="id")
    apply_user = ForeignKey(User, related_name='apply_verification_codes', on_delete=models.CASCADE, null=True)
    email = CharField("电子邮件", max_length=255, null=True)
    code = CharField("电子邮件", max_length=255, null=True)
    is_used = BooleanField("是否被用过", default=0)
    expire = DateTimeField("验证码失效时间", null=True)

    def __str__(self):
        return "邮箱：" + self.email + ", 验证码：" + self.code

    class Meta:
        db_table = "dms_email_verification_code"