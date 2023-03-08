<template>
  <div class="user-table">
    <el-table
      :data="dealDataPassword"
      :max-height="450"
      :stripe="true"
      :border="true"
      :show-header="true"
      :highlight-current-row="true"
      :row-key="'id'"
      :empty-text="'暂无数据'"
      :select-on-indeterminate="true"
      style="width: 100%"
      v-loading="loading"
      tooltip-effect="light"
      @selection-change="handleSelectionChange"
    >
      <el-table-column
        v-for="column in columns"
        :key="column.prop"
        :type="column.type"
        :column-key="column.prop"
        :label="column.label"
        :prop="column.prop"
        :min-width="column.minWidth"
        :fixed="column.fixed"
        :sortable="column.sortable == null ? true : column.sortable"
        :resizable="column.resizable"
        align="center"
        header-align="center"
      >
      </el-table-column>
      <el-table-column
        :min-width="150"
        :resizable="true"
        align="center"
        header-align="center"
        label="用户状态"
      >
        <template slot-scope="scope">
          <i
            class="ri-focus-fill"
            :style="{ color: statusColorList[scope.row.active] }"
          ></i>
          {{ statusList[scope.row.active] }}
        </template>
      </el-table-column>
      <el-table-column
        :min-width="210"
        :fixed="'right'"
        :resizable="true"
        align="center"
        header-align="center"
        label="操作"
      >
        <template slot-scope="scope">
          <el-button
            v-if="
              $store.state.auth.currentUser.permissions.indexOf(72) != -1 &&
              scope.row.active == 1
            "
            size="mini"
            type="primary"
            @click.stop="handleEdit(scope.$index, scope.row)"
            >编辑</el-button
          >
          <el-button
            v-if="
              $store.state.auth.currentUser.permissions.indexOf(73) != -1 &&
              scope.row.active == 1
            "
            size="mini"
            type="danger"
            @click.stop="handleDelete(scope.$index, scope.row)"
            >删除</el-button
          >
          <el-button
            v-if="
              $store.state.auth.currentUser.permissions.indexOf(74) != -1 &&
              scope.row.active == 0
            "
            size="mini"
            type="success"
            @click.stop="handleRecover(scope.$index, scope.row)"
            >恢复账号</el-button
          >
        </template>
      </el-table-column>
    </el-table>
    <!-- 分页栏 -->
    <div class="ops">
      <el-button
        v-if="$store.state.auth.currentUser.permissions.indexOf(73) != -1"
        type="danger"
        icon="el-icon-delete"
        @click.stop="handleSelectionDelete"
        class="button-float-left"
      >
        批量删除选中用户
      </el-button>
      <el-button
        v-if="$store.state.auth.currentUser.permissions.indexOf(71) != -1"
        type="primary"
        icon="el-icon-plus"
        @click.stop="handleAddNewUser"
        class="button-float-left"
      >
        新增单个用户
      </el-button>
      <el-button
        v-if="$store.state.auth.currentUser.permissions.indexOf(71) != -1"
        type="primary"
        icon="el-icon-upload"
        @click.stop="clickImportNewUsersButton"
        class="button-float-left"
      >
        批量导入新用户
        <input
          ref="newUserInput"
          type="file"
          name="newUserInput"
          style="display: none"
          @change="handleUploadNewUsers"
        />
      </el-button>

      <el-pagination
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
        :current-page="page"
        :page-sizes="[5, 10, 20, 30]"
        :page-size="pageSize"
        layout="total, sizes, prev, pager, next, jumper"
        :total="totalSize"
        class="pagination-float-right"
      >
      </el-pagination>
    </div>
    <!-- 修改用户资料对话框 -->
    <el-dialog
      title="修改用户资料"
      :visible.sync="modifyUserDialogVisible"
      :close-on-click-modal="false"
      :destroy-on-close="true"
      :show-close="false"
      class="modify-user-dialog"
    >
      <el-form label-width="100px">
        <el-form-item class="form-item" label="工号：">
          <el-input v-model="userForm.id" :disabled="true" autocomplete="off">
          </el-input>
        </el-form-item>
        <el-form-item class="form-item" label="姓名：">
          <el-input
            v-model="userForm.name"
            :clearable="true"
            autocomplete="off"
          >
          </el-input>
        </el-form-item>
        <el-form-item class="form-item" label="密码：">
          <el-input
            type="password"
            :show-password="true"
            v-model="userForm.password"
            :clearable="true"
            autocomplete="off"
          >
          </el-input>
        </el-form-item>
        <el-form-item class="form-item" label="部门：">
          <el-select
            v-model="userForm.currentDept"
            :clearable="true"
            placeholder="请选择"
          >
            <el-option
              v-for="departmentObj in departmentList"
              :key="departmentObj.id"
              :label="departmentObj.name"
              :value="departmentObj.id"
            >
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item class="form-item" label="角色：">
          <el-select
            v-model="userForm.currentRole"
            :clearable="true"
            placeholder="请选择"
          >
            <el-option
              v-for="roleObj in roleList"
              :key="roleObj.id"
              :label="roleObj.name"
              :value="roleObj.id"
            >
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item class="form-item" label="电话号码：">
          <el-input
            v-model="userForm.phone"
            :clearable="true"
            autocomplete="off"
          >
          </el-input>
        </el-form-item>
        <el-form-item class="form-item">
          <el-button type="primary" @click.stop="submitEditUserInfo"
            >提交</el-button
          >
          <el-button
            type="info"
            @click.stop="userForm = JSON.parse(JSON.stringify(userFormBackup))"
            >重置</el-button
          >
          <el-button @click.stop="modifyUserDialogVisible = false"
            >取消</el-button
          >
        </el-form-item>
      </el-form>
    </el-dialog>
    <!-- 新增用户对话框 -->
    <el-dialog
      title="新增用户"
      :visible.sync="newUserDialogVisible"
      :close-on-click-modal="false"
      :destroy-on-close="true"
      :show-close="false"
      class="new-user-dialog"
    >
      <el-form label-width="100px">
        <el-form-item class="form-item" label="工号：">
          <el-input
            v-model="newUserForm.id"
            :clearable="true"
            autocomplete="off"
          >
          </el-input>
        </el-form-item>
        <el-form-item class="form-item" label="姓名：">
          <el-input
            v-model="newUserForm.name"
            :clearable="true"
            autocomplete="off"
          >
          </el-input>
        </el-form-item>
        <el-form-item class="form-item" label="密码：">
          <el-input
            type="password"
            :show-password="true"
            v-model="newUserForm.password"
            :clearable="true"
            autocomplete="off"
          >
          </el-input>
        </el-form-item>
        <el-form-item class="form-item" label="部门：">
          <el-select
            v-model="newUserForm.deptId"
            :clearable="true"
            placeholder="请选择"
          >
            <el-option
              v-for="departmentObj in departmentList"
              :key="departmentObj.id"
              :label="departmentObj.name"
              :value="departmentObj.id"
            >
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item class="form-item" label="角色：">
          <el-select
            v-model="newUserForm.roleId"
            :clearable="true"
            placeholder="请选择"
          >
            <el-option
              v-for="roleObj in roleList"
              :key="roleObj.id"
              :label="roleObj.name"
              :value="roleObj.id"
            >
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item class="form-item" label="电话号码：">
          <el-input
            v-model="newUserForm.phone"
            :clearable="true"
            autocomplete="off"
          >
          </el-input>
        </el-form-item>
        <el-form-item class="form-item">
          <el-button type="primary" @click.stop="submitNewUserInfo"
            >提交</el-button
          >
          <el-button @click.stop="newUserDialogVisible = false">取消</el-button>
        </el-form-item>
      </el-form>
    </el-dialog>
  </div>
</template>

<script>
import { request } from "@/network/request";

export default {
  components: {},
  name: "UserTable",
  props: {
    page: Number,
    pageSize: Number,
    totalSize: Number,
    data: Array,
    columns: Array, //列的各个属性,可设置：type,index,label,prop,minWidth,fixed,sortable,resizable,filters
    loading: Boolean,
  },
  data() {
    return {
      statusList: ["已删除", "活跃用户"],
      statusColorList: ["red", "green"],
      selectedUsers: [],

      modifyUserDialogVisible: false,
      departmentList: [],
      roleList: [],
      userFormBackup: {},
      userForm: {
        id: "",
        name: "",
        password: "",
        currentDept: "",
        currentRole: "",
        phone: "",
      },

      newUserDialogVisible: false,
      newUserForm: {
        id: "",
        name: "",
        password: "",
        deptId: "",
        roleId: "",
        phone: "",
      },
    };
  },
  computed: {
    dealDataPassword() {
      return this.data.map((user) => {
        const len = user.password.length;
        const halfLen = Math.ceil(len / 2);
        const restLen = len - halfLen;
        const finalStart = Math.floor(restLen / 2) + halfLen;
        const finalLen = len - finalStart;
        user.password =
          user.password.substr(0, Math.floor(restLen / 2)) +
          "*".repeat(halfLen) +
          user.password.substr(finalStart, finalLen);
        return user;
      });
    },
  },
  methods: {
    handleSizeChange(val) {
      this.$emit("update:pageSize", val);
      this.$emit("update:loading", true);
      this.$emit("refresh-data");
    },
    handlePageChange(val) {
      this.$emit("update:page", val);
      this.$emit("update:loading", true);
      this.$emit("refresh-data");
    },
    handleEdit(index, row) {
      request({
        url: "User/UserInfo",
        method: "get",
        params: {
          userId: row.id,
        },
      })
        .then((res) => {
          const data = res.data;
          if (data.errcode == 0) {
            this.userForm = data.userForm;
            this.departmentList = data.departmentList;
            this.roleList = data.roleList;
            this.userFormBackup = JSON.parse(JSON.stringify(this.userForm));
            this.modifyUserDialogVisible = true;
          } else {
            alert(data.errmsg);
          }
        })
        .catch((err) => {
          alert(err);
        });
    },
    submitEditUserInfo() {
      request({
        url: "User/EditUser",
        method: "post",
        data: {
          userForm: this.userForm,
        },
      })
        .then((res) => {
          const data = res.data;
          if (data.errcode == 0) {
            this.$message({
              type: "success",
              message: "修改成功!",
            });
            this.modifyUserDialogVisible = false;
            this.$emit("update:loading", true);
            this.$emit("refresh-data");
          } else {
            alert(data.errmsg);
          }
        })
        .catch((err) => alert(err));
    },
    handleDelete(index, row) {
      this.$confirm("此操作将永久删除该用户, 是否继续?", "提示", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning",
      })
        .then(() => {
          request({
            url: "User/DeleteUser",
            method: "get",
            params: {
              userid: row.id,
            },
          })
            .then((res) => {
              const data = res.data;
              if (data.errcode == 0) {
                this.$message({
                  type: "success",
                  message: "删除成功!",
                });
                this.$emit("update:loading", true);
                this.$emit("refresh-data");
              } else {
                alert(data.errmsg);
              }
            })
            .catch((err) => {
              alert(err);
            });
        })
        .catch(() => {
          this.$message({
            type: "info",
            message: "已取消删除",
          });
        });
    },
    handleRecover(index, row) {
      this.$confirm("此操作将恢复该已被删除的用户的账号, 是否继续?", "提示", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning",
      })
        .then(() => {
          request({
            url: "User/RecoverUser",
            method: "get",
            params: {
              userId: row.id,
            },
          })
            .then((res) => {
              const data = res.data;
              if (data.errcode == 0) {
                this.$message({
                  type: "success",
                  message: "恢复账号成功!",
                });
                this.$emit("update:loading", true);
                this.$emit("refresh-data");
              } else {
                alert(data.errmsg);
              }
            })
            .catch((err) => alert(err));
        })
        .catch(() => {
          this.$message({
            type: "info",
            message: "已取消恢复账号",
          });
        });
    },
    handleSelectionChange(selectedRows) {
      this.selectedUsers = selectedRows;
    },
    handleSelectionDelete() {
      if (this.selectedUsers.length == 0) {
        alert("请至少选中一项记录！");
        return;
      }
      this.$confirm("此操作将批量删除选中用户, 是否继续?", "批量删除选中用户", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning",
      })
        .then(() => {
          let allMeetCondition = this.selectedUsers.every((val) => {
            return val.active == 1;
          });
          if (allMeetCondition == true) {
            request({
              url: "User/DeleteSelectionUsers",
              method: "post",
              data: {
                useridList: this.selectedUsers.map((val) => val.id),
              },
            })
              .then((res) => {
                const data = res.data;
                if (data.errcode == 0) {
                  this.$message({
                    type: "success",
                    message: "批量删除选中用户成功!",
                  });
                  this.$emit("update:loading", true);
                  this.$emit("refresh-data");
                } else alert(data.errmsg);
              })
              .catch((err) => {
                alert(err);
              });
          } else {
            alert("只能删除处于活跃状态的用户！");
          }
        })
        .catch(() => {
          this.$message({
            type: "info",
            message: "已取消批量删除选中用户",
          });
        });
    },
    handleAddNewUser() {
      request({
        url: "User/DepartmentsAndRolesList",
        method: "get",
      })
        .then((res) => {
          const data = res.data;
          if (data.errcode == 0) {
            (this.newUserForm = {
              id: "",
              name: "",
              password: "",
              deptId: "",
              roleId: "",
              phone: "",
            }),
              (this.departmentList = data.departmentList);
            this.roleList = data.roleList;
            this.newUserDialogVisible = true;
          } else {
            alert(data.errmsg);
          }
        })
        .catch((err) => {
          alert(err);
        });
    },
    submitNewUserInfo() {
      request({
        url: "User/NewUser",
        method: "post",
        data: {
          newUserForm: this.newUserForm,
        },
      })
        .then((res) => {
          const data = res.data;
          if (data.errcode == 0) {
            this.$message({
              type: "success",
              message: "新增用户成功!",
            });
            this.newUserDialogVisible = false;
            this.$emit("update:loading", true);
            this.$emit("refresh-data");
          } else {
            alert(data.errmsg);
          }
        })
        .catch((err) => alert(err));
    },
    clickImportNewUsersButton() {
      let newUserInput = this.$refs.newUserInput;
      newUserInput.value = "";
      newUserInput.click();
    },
    handleUploadNewUsers(e) {
      let file = e.target.files[0];
      if (file == null) return;
      this.$confirm("确定要从该文件批量导入新用户?", "批量导入用户", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning",
      })
        .then(() => {
          let xlsType = new RegExp("^application/vnd.ms-excel");
          let xlsxType = new RegExp(
            "^application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
          );
          if (!xlsType.test(file.type) && !xlsxType.test(file.type)) {
            alert("请上传excel类型的文件！");
            return;
          }
          let usersFile = new FormData();
          usersFile.append("newUsersFile", file);
          request({
            url: "User/ImportNewUsers",
            method: "post",
            headers: {
              "Content-Type": "multipart/form-data",
            },
            data: usersFile,
          })
            .then((res) => {
              const data = res.data;
              if (data.errcode == 0) {
                this.$message({
                  type: "success",
                  message: `成功导入${data.sum}个新用户！`,
                });
                this.$emit("update:loading", true);
                this.$emit("refresh-data");
              } else {
                alert(data.errmsg);
              }
            })
            .catch((err) => alert(err));
        })
        .catch(() => {
          this.$message({
            type: "info",
            message: "已取消批量导入用户",
          });
        });
    },
  },
};
</script>

<style lang="scss">

.user-table {
  .ops {
    margin: 40px;
    height:50px;
    font-size: 1.5rem;
  }

  .button-float-left {
    float: left;
  }

  .pagination-float-right {
    float:right;
  }

  .modify-user-dialog {
    .el-dialog {
      width: 40% !important;
    }

    .form-item {
      width: 80%;
    }
  }

  .new-user-dialog {
    .el-dialog {
      width: 40% !important;
    }

    .form-item {
      width: 80%;
    }
  }
}


</style>