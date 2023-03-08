<template>
  <el-dialog title="借阅文件申请详情" :visible.sync="showBorrowFileDialog" :before-close="handleCancel">
    <el-form :model="borrowRecord" ref="borrowRecordForm" label-width="120px" class="borrow-record-form">
      <el-form-item
        label="借阅人："
        class="borrow-record-item"
      >
        <el-input
          v-model="borrowRecord.borrowUser.name"
          :disabled="true"
          autocomplete="off"
          size="medium"
        ></el-input>
      </el-form-item>
      <el-form-item
        label="借阅文件名："
        class="borrow-record-item"
      >
        <el-input
          v-model="borrowRecord.borrowFile.name"
          :disabled="true"
          autocomplete="off"
          size="medium"
        ></el-input>
      </el-form-item>
      <el-form-item
        label="借阅时间段："
        class="borrow-record-item"
        prop="btime"
        :rules="[
          { required: true, message: '时间段不能为空', trigger: 'blur'}
        ]"
      >
        <el-date-picker
          value-format="yyyy-MM-dd HH:mm:ss"
          v-model="borrowRecord.btime"
          type="datetimerange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期">
        </el-date-picker>
      </el-form-item>
      <el-form-item
        label="借阅事由："
        class="borrow-record-item"
        prop="reason"
        :rules="[
          { required: true, message: '借阅事由不能为空', trigger: 'blur'}
        ]"
      >
        <el-input
          v-model="borrowRecord.reason"
          :clearable="true"
          autocomplete="off"
          size="medium"
        ></el-input>
      </el-form-item>
      <el-form-item
        label="审批人："
        class="borrow-record-item"
        prop="approvers"
        :rules="[
          { required: true, message: '审批人不能为空', trigger: 'blur'}
        ]"
      >
        <div>
          <el-tag
            v-for="tag in borrowRecord.approvers"
            :key="tag.id + tag.name"
            closable
            :disable-transitions="false"
            @close="handleCloseApproverTag(tag)">
            {{tag.name}}
          </el-tag>
        </div>
        <div>
          <el-select @change="handleAddApprover" v-model="borrowRecord.selectApprover" placeholder="请选择">
            <el-option
              v-for="approver in borrowRecord.allManagers"
              :key="approver.id"
              :label="approver.name"
              :value="approver">
            </el-option>
          </el-select>
        </div>
      </el-form-item>
      <el-form-item
        label="抄送人："
        class="borrow-record-item"
        prop="notifyers"
        :rules="[
          { required: true, message: '抄送人不能为空', trigger: 'blur'}
        ]"
      >
        <div>
          <el-tag
            v-for="tag in borrowRecord.notifyers"
            :key="tag.id + tag.name"
            closable
            :disable-transitions="false"
            @close="handleCloseNotifyerTag(tag)">
            {{tag.name}}
          </el-tag>
        </div>
        <div>
          <el-select @change="handleAddNotifyer" v-model="borrowRecord.selectNotifyer" placeholder="请选择">
            <el-option
              v-for="notifyer in borrowRecord.allManagers"
              :key="notifyer.id"
              :label="notifyer.name"
              :value="notifyer">
            </el-option>
          </el-select>
        </div>
      </el-form-item>
      <el-form-item
        label="备注："
        class="borrow-record-item"
      >
        <el-input
          type="textarea"
          v-model="borrowRecord.remark"
          :clearable="true"
          autocomplete="off"
          size="medium"
        ></el-input>
      </el-form-item>
    </el-form>
    <div slot="footer">
      <el-button @click.stop="handleCancel">取 消</el-button>
      <el-button type="primary" @click.stop="handleBorrow('borrowRecordForm')">申请借阅</el-button>
    </div>
  </el-dialog>
</template>

<script>
import { request } from "@/network/request";

export default {
  props: {
    borrowFile: Object,
    borrowUser: Object,
    showBorrowFileDialog: {
      type: Boolean,
      default: false,
    }
  },
  data() {
    return {
      borrowRecord: {
        borrowUser: {},
        borrowFile: {},
        btime: "",
        reason: "",
        allManagers: [],
        selectApprover: "",
        approvers: [],
        selectNotifyer: "",
        notifyers: [],
        remark: "",
      }
    }
  },
  methods: {
    handleCancel() {
      this.borrowRecord = {
        borrowUser: {},
        borrowFile: {},
        btime: "",
        reason: "",
        allManagers: [],
        selectApprover: {},
        approvers: [],
        selectNotifyer: {},
        notifyers: [],
        remark: "",
      }
      this.$emit("update:showBorrowFileDialog", false)
    },
    handleBorrow(formName) {
      this.$refs[formName].validate((valid) => {
        if (valid) {
          request({
            url: "File/NewBorrowRecord",
            method: "post",
            data: {
              borrowUser: this.borrowRecord.borrowUser,
              borrowFile: this.borrowRecord.borrowFile,
              reason: this.borrowRecord.reason,
              bstime: this.borrowRecord.btime[0],
              betime: this.borrowRecord.btime[1],
              approvers: this.borrowRecord.approvers,
              notifyers: this.borrowRecord.notifyers,
              remark: this.borrowRecord.remark,
            }
          }).then(res => {
            let data = res.data
            if (data.errcode == 0) {
              alert("借阅已提交，请等待审批")
              this.handleCancel()
              this.$store.commit("file/SET_FILE_CHANGE", !this.$store.state.file.showFilesInfo.fileHaveChange)
            }else {
              alert(data.errmsg)
            }
          }).catch(err => {
            alert(err)
          })
        } else {
          console.log('请按要求填写申请信息！');
          return ;
        }
      });
    },
    handleCloseApproverTag(tag) {
      const pos = this.borrowRecord.approvers.indexOf(tag)
      this.borrowRecord.approvers.splice(pos, 1);
    },
    handleCloseNotifyerTag(tag) {
      const pos = this.borrowRecord.notifyers.indexOf(tag)
      this.borrowRecord.notifyers.splice(pos, 1);
    },
    handleAddApprover(approver) {
      if (this.borrowRecord.approvers.indexOf(approver) == -1) {
        this.borrowRecord.approvers.push(approver)
      }else {
        alert("该审批人已存在！")
      }
    },
    handleAddNotifyer(notifyer) {
      if (this.borrowRecord.notifyers.indexOf(notifyer) == -1) {
        this.borrowRecord.notifyers.push(notifyer)
      }else {
        alert("该审批人已存在！")
      }
    }
  },
  watch: {
    "showBorrowFileDialog"(newVal, oldVal) {
      if (newVal) {
        this.borrowRecord.borrowFile = this.borrowFile
        this.borrowRecord.borrowUser = this.borrowUser
        request({
          url: "File/FileApprovers",
          method: "get",
          params: {
            fileId: this.borrowRecord.borrowFile.id
          }
        }).then(res => {
          let data = res.data
          if (data.errcode == 0) {
            this.borrowRecord.allManagers = data.res
          }else {
            alert(data.errmsg)
            this.handleCancel()
            this.$store.commit("file/SET_FILE_CHANGE", !this.$store.state.file.showFilesInfo.fileHaveChange)
          }
        }).catch(err => {
          alert(err)
          this.handleCancel()
          this.$store.commit("file/SET_FILE_CHANGE", !this.$store.state.file.showFilesInfo.fileHaveChange)
        })
      }
    }
  }
}
</script>

<style lang="scss">

.borrow-record-form {
  .el-dialog {
    width: 60%;
  }
} 

.borrow-record-item {
  margin-bottom: 15px !important;
  margin-right: 50px !important;
  
  .el-input {
    margin-bottom: 0 !important;
  }
}

.select-approver {
  margin-left:120px;
}

</style>