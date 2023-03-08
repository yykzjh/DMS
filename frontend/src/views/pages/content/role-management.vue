<template>
  <div class="role-management-page">
      <PageHeader :title="title" :items="items" />
      <el-card class="role-management-card">
        <el-table
          :data="roleData"
          :max-height="700"
          :stripe="false"
          :border="false"
          :show-header="true"
          :highlight-current-row="true"
          :row-key="'id'"
          :empty-text="'暂无数据'"
          style="width:100%;"
          v-loading="loading">
          <el-table-column
            :min-width="150"
            align="center"
            header-align="center"
            label="角色名称"
            prop="name">
          </el-table-column>
          <el-table-column
            :min-width="100"
            align="center"
            header-align="center"
            label="可借阅总量"
            prop="borrowTotalCount">
          </el-table-column>
          <el-table-column
            :min-width="500"
            align="left"
            header-align="center"
            label="具有的权限">
            <template slot-scope="scope">
              <div class="permission-tags-div">
                <el-tag 
                  v-for="permission in scope.row.currentPermissions"
                  :key="permission.id">
                  {{permission.description}}
                </el-tag>
              </div>
            </template>
          </el-table-column>
          <el-table-column
            :min-width="210"
            align="center"
            header-align="center"
            label="操作">
            <template slot-scope="scope">
              <el-button
                size="mini"
                type="warning"
                @click.stop="handleModifyPermissions(scope.$index, scope.row)">修改权限</el-button>
              <el-button
                size="mini"
                type="primary"
                @click.stop="handleModifyBorrowTotalCount(scope.$index, scope.row)">修改借阅总量</el-button>
            </template>
          </el-table-column>
        </el-table>
        <!-- 分页栏 -->
        <div class="ops">
           <el-button
            type="primary" 
            icon="el-icon-plus" 
            @click.stop="handleAddNewRole"
            class="button-float-left">
            新增角色
          </el-button>

          <el-pagination
            @size-change="handleSizeChange"
            @current-change="handlePageChange"
            :current-page="page"
            :page-sizes="[5, 10, 20, 30]"
            :page-size="pageSize"
            layout="total, sizes, prev, pager, next, jumper"
            :total="totalSize"
            class="pagination-float-right">
          </el-pagination>
        </div>

        <!-- 修改权限对话框 -->
        <el-dialog
          title="修改角色权限"
          :visible.sync="modifyRolePermissionsDialogVisible"
          :close-on-click-modal="false"
          :destroy-on-close="true"
          :show-close="false"
          class="modify-role-permission-dialog">
          <el-transfer v-model="modifyPermissions" :data="newAllPermissions"></el-transfer>
          <div slot="footer">
            <el-button type="primary" @click.stop="submitRolePermissions">提交</el-button>
            <el-button @click.stop="modifyRolePermissionsDialogVisible = false">取消</el-button>
          </div>
        </el-dialog>
        <!-- 新增角色对话框 -->
        <el-dialog
          title="新增角色"
          :visible.sync="newRoleDialogVisible"
          :close-on-click-modal="false"
          :destroy-on-close="true"
          :show-close="false"
          class="new-role-dialog">
          <el-form label-width="100px">
            <el-form-item class="form-item" label="角色名称：">
              <el-input
                v-model="newRoleName"
                :clearable="true"
                autocomplete="off">
              </el-input>
            </el-form-item>
            <el-form-item class="form-item" label="可借阅总量：">
              <el-input
                v-model="newRoleBorrowTotalCount"
                :clearable="true"
                autocomplete="off">
              </el-input>
            </el-form-item>
            <el-form-item class="form-item" label="分配权限：" style="width:100% !important;">
              <el-transfer v-model="newRolePermissions" :data="newAllPermissions"></el-transfer>
            </el-form-item>
            <el-form-item class="form-item">
              <el-button type="primary" @click.stop="submitNewRole">提交</el-button>
              <el-button @click.stop="newRoleDialogVisible = false">取消</el-button>
            </el-form-item>
          </el-form>
        </el-dialog>
      </el-card>
  </div>
</template>

<script>
import { request } from "@/network/request";
import PageHeader from "@/components/page-header";

export default {
  components: {
    PageHeader
  },
  data() {
    return {
      title: "Role Management",
      items:[
        {
          text: "DMS"
        },
        {
          text: "角色管理",
          active: true
        }
      ],

      page: 1,
      pageSize: 5,
      totalSize: 0,
      loading: false,
      roleData: [],
      allPermissions: [],

      modifyRolePermissionsDialogVisible: false,
      modifyPermissions: [],
      roleId: null,

      newRoleDialogVisible: false,
      newRoleName: "",
      newRoleBorrowTotalCount: "",
      newRolePermissions: []
    }
  },
  computed: {
    newAllPermissions() {
      return this.allPermissions.map((val) => {
        return {
          key: val.id,
          label: val.description
        }
      })
    },
  },
  methods: {
    getRoleData() {
      request({
        url: "User/Roles",
        method: "get",
        params: {
          page: this.page,
          pageSize: this.pageSize
        }
      }).then(res => {
        const data = res.data
        if (data.errcode == 0) {
          this.totalSize = data.totalSize
          this.roleData = data.res
          this.allPermissions = data.allPermissions,
          this.loading = false
          console.log(this.allPermissions)
        }
        else alert(data.errmsg)
      }).catch(err => alert(err))
    },
    handleSizeChange(val) {
      this.pageSize = val
      this.loading = true
      this.getRoleData()
    },
    handlePageChange(val) {
      this.page = val
      this.loading = true
      this.getRoleData()
    },
    handleModifyPermissions(index, row) {
      this.modifyPermissions = row.currentPermissions.map(value => {
        return value.id
      })
      this.roleId = row.id
      this.modifyRolePermissionsDialogVisible = true
    },
    submitRolePermissions() {
      request({
        url: "User/ModifyRolePermissions",
        method: "post",
        data: {
          roleId: this.roleId,
          rolePermissions: this.modifyPermissions,
        }
      }).then(res => {
        const data = res.data
        if (data.errcode == 0) {
          this.$message.success("权限修改成功！")
          this.modifyRolePermissionsDialogVisible = false
          this.loading = true
          this.getRoleData()
        }else alert(data.errmsg)
      }).catch(err=>alert(err))
    },
    handleModifyBorrowTotalCount(index, row) {
      this.$prompt('请输入新的借阅总量', '修改角色的借阅总量', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        inputPattern: /^[0-9]+$/,
        inputErrorMessage: '借阅总量格式不正确！'
      }).then(({ value }) => {
        request({
          url: "User/ModifyBorrowTotalCount",
          method: "get",
          params: {
            roleId: row.id,
            newBorrowTotalCount: value,
          }
        }).then(res => {
          const data = res.data
          if (data.errcode == 0) {
            this.$message.success("借阅总量修改成功！")
            this.loading = true
            this.getRoleData()
          }else alert(data.errmsg)
        }).catch(err => alert(err))
      }).catch(() => {
        this.$message({
          type: 'info',
          message: '取消修改借阅总量'
        });       
      });
    },
    handleAddNewRole() {
      this.newRoleName = ""
      this.newRoleBorrowTotalCount = ""
      this.newRolePermissions = []
      this.newRoleDialogVisible = true
    },
    submitNewRole() {
      request({
        url: "User/NewRole",
        method: "post",
        data: {
          name: this.newRoleName,
          borrowTotalCount: this.newRoleBorrowTotalCount,
          permissions: this.newRolePermissions
        }
      }).then(res => {
        const data = res.data
        if (data.errcode == 0) {
          this.$message.success("新增角色成功！")
          this.newRoleDialogVisible = false
          this.loading = true
          this.getRoleData()
        }else alert(data.errmsg)
      }).catch(err => alert(err))
    },
  },
  mounted:function() {
    this.loading = true
    this.getRoleData()
  },
}
</script>

<style lang="scss">

.role-management-page {

  .role-management-card {
    min-height: 600px;

    .permission-tags-div {
      width: 100%;
      padding: 10px 15px;
      border-radius: 10px;
      border: 1px solid #dcdfe6;
      transition: border-color .2s cubic-bezier(.645,.045,.355,1);

      .el-tag {
        margin-left: 5px;
      }
    }

    .ops {
      margin: 40px;
      height:50px;
      font-size: 1.5rem;

      .button-float-left {
        float: left;
      }

      .pagination-float-right {
        float:right;
      }
    }

    .modify-role-permission-dialog {
      .el-dialog {
        width: 40% !important;

        .el-dialog__body {
          padding: 30px 50px !important;
        }

        .el-dialog__footer {
          display: flex;
          justify-content: center;
        }
      }
    }

    .new-role-dialog {
      .el-dialog {
        width: 50% !important;
      }

      .form-item {
        width: 60%;
      }
    }
  }
}

</style>