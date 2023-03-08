<template>
  <div class="user-management-page">
    <PageHeader :title="title" :items="items" />
    <el-card class="user-management-card">
      <div class="query-header">
        <label for="userId" class="query-item-label">用户工号：</label>
        <el-input
          id="userId"
          clearable
          class="query-condition-item"
          placeholder="用户工号"
          v-model="userId">
        </el-input>
        <label for="userName" class="query-item-label">用户姓名：</label>
        <el-input
          id="userName"
          clearable
          class="query-condition-item"
          placeholder="用户姓名"
          v-model="userName">
        </el-input>
        <label for="department-list" class="query-item-label">部门：</label>
        <el-select id="department-list" v-model="selectedDepartments" clearable multiple placeholder="请选择">
          <el-option
            v-for="department in departmentList"
            :key="department.id"
            :label="department.name"
            :value="department.id">
          </el-option>
        </el-select>
        <label for="role-list" class="query-item-label">用户角色：</label>
        <el-select id="role-list" v-model="selectedRoles" clearable multiple placeholder="请选择">
          <el-option
            v-for="role in roleList"
            :key="role.id"
            :label="role.name"
            :value="role.id">
          </el-option>
        </el-select>
        <br />
        <label for="user-status" class="query-item-label">用户状态：</label>
        <el-select id="user-status" v-model="selectedStatus" clearable placeholder="请选择">
          <el-option
            v-for="status in statusList"
            :key="status.value"
            :label="status.label"
            :value="status.value">
          </el-option>
        </el-select>
        <label for="whether-face-verification" class="query-item-label">是否已人脸认证：</label>
        <el-select id="whether-face-verification" v-model="selectedWhetherFaceVerification" clearable placeholder="请选择">
          <el-option
            v-for="whetherFaceVerification in whetherFaceVerificationList"
            :key="whetherFaceVerification.value"
            :label="whetherFaceVerification.label"
            :value="whetherFaceVerification.value">
          </el-option>
        </el-select>
        <el-button
          icon="el-icon-search"
          class="search-button"
          type="primary"
          @click="handleConditionSearch"></el-button>
      </div>

      <UserTable
        :page.sync="page"
        :pageSize.sync="pageSize"
        :totalSize="totalSize"
        :data="tableData"
        :columns="columns"
        :loading.sync="loading"
        @refresh-data="getUsers"
      ></UserTable>
    </el-card>
  </div>
</template>

<script>
import { request } from "@/network/request";
import PageHeader from "@/components/page-header";
import UserTable from "@/components/user-table";

export default {
  components: {
    PageHeader,
    UserTable,
  },
  data() {
    return {
      title: "User Management",
      items:[
        {
          text: "DMS"
        },
        {
          text: "用户管理",
          active: true
        }
      ],

      userId: "",
      userName: "",
      departmentList: [],
      selectedDepartments: [],
      roleList: [],
      selectedRoles: [],
      statusList: [{label: "活跃用户", value: true},{label: "已删除", value: false}],
      selectedStatus: "",
      whetherFaceVerificationList: [{label: "已认证", value: true},{label: "未认证", value: false}],
      selectedWhetherFaceVerification: "",

      page: 1,
      pageSize: 5,
      totalSize: 0,
      tableData: [],
      columns: [
        {type:"selection", minWidth:60, fixed:"left", resizable:false},
        {label:"工号", prop:"id", minWidth:200, fixed:"left", resizable:false},
        {label:"姓名", prop:"name", minWidth:120, fixed:"left", resizable:true},
        {label:"密码", prop:"password", minWidth:200, resizable:true},
        {label:"部门", prop:"department", minWidth:200, resizable:true},
        {label:"用户角色", prop:"roleName", minWidth:150, resizable:true},
        {label:"可借阅次数", prop:"borrowCount", minWidth:100, resizable:true},
        {label:"电话号码", prop:"phone", minWidth:150, resizable:true},
        {label:"电子邮箱", prop:"email", minWidth:200, resizable:true},
        {label:"微信号", prop:"wechat", minWidth:200, resizable:true},
        {label:"人脸认证", prop:"faceVerification", minWidth:120, resizable:true},
      ],
      loading:false,
    }
  },
  methods: {
    getUsers() {
      request({
        url: "User/Users",
        method: "post",
        data: {
          userId: this.userId,
          userName: this.userName,
          selectedDepartments: this.selectedDepartments,
          selectedRoles: this.selectedRoles,
          selectedStatus: this.selectedStatus,
          selectedWhetherFaceVerification: this.selectedWhetherFaceVerification,
          page: this.page,
          pageSize: this.pageSize
        }
      }).then(res => {
        const data = res.data
        if (data.errcode == 0) {
          this.totalSize = data.totalSize
          this.tableData = data.res
          this.departmentList = data.departmentList,
          this.roleList = data.roleList
          this.loading = false
        }
        else{
          alert(data.errmsg)
        }
      }).catch(err => {
        alert(err)
      })
    },
    handleConditionSearch() {
      this.loading = true
      this.getUsers()
    },
  },
  mounted:function() {
    this.getUsers()
  },
}
</script>

<style lang="scss">

.user-management-page {

  .user-management-card {
    min-height: 600px;

    .query-header {
      width: 100%;
      margin-bottom: 20px;

      .query-item-label {
        margin-left: 20px;
        min-width: 80px;
        text-align: right;
      }

      .query-condition-item {
        width: 200px;
        font-size: 0.8rem;
      }

      .search-button {
        position:relative;
        top:1px;
      }
    }
  } 
}

</style>