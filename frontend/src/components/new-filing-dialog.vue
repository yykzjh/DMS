<template>
  <div>
    <el-dialog title="新增项目组详情" :visible.sync="showAddProjectTeamDialog" :before-close="handleCancel">
      <el-form :model="projectTeamForm">
        <el-form-item
          label="项目组名称："
          :label-width="formLabelWidth"
          class="new-filing-item"
        >
          <el-input
            v-model="projectTeamForm.name"
            :clearable="true"
            autocomplete="off"
            size="medium"
          ></el-input>
        </el-form-item>
        <el-form-item
          label="负责人："
          :label-width="formLabelWidth"
          class="new-filing-item"
          style="width:50% !important"
        >
          <el-input
            v-model="projectTeamForm.manager"
            :disabled="true"
            autocomplete="off"
            size="medium"
          ></el-input>
        </el-form-item>
        <el-form-item
          label="备注："
          :label-width="formLabelWidth"
          class="new-filing-item"
        >
          <el-input
            type="textarea"
            v-model="projectTeamForm.remark"
            :clearable="true"
            autocomplete="off"
            size="medium"
          ></el-input>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="handleCancel">取 消</el-button>
        <el-button type="primary" @click="handleAdd">新建</el-button>
      </div>
    </el-dialog>

    <el-dialog title="新增文件柜详情" :visible.sync="showAddCabinetDialog" :before-close="handleCancel">
      <el-form :model="cabinetForm">
        <el-form-item
          label="文件柜名称："
          :label-width="formLabelWidth"
          class="new-filing-item"
        >
          <el-input
            v-model="cabinetForm.name"
            :clearable="true"
            autocomplete="off"
            size="medium"
          ></el-input>
        </el-form-item>
       <el-form-item
          label="负责人："
          :label-width="formLabelWidth"
          class="new-filing-item"
          style="width:50% !important"
        >
          <el-input
            v-model="cabinetForm.manager"
            :disabled="true"
            autocomplete="off"
            size="medium"
          ></el-input>
        </el-form-item>
        <el-form-item
          label="备注："
          :label-width="formLabelWidth"
          class="new-filing-item"
        >
          <el-input
            type="textarea"
            v-model="cabinetForm.remark"
            :clearable="true"
            autocomplete="off"
            size="medium"
          ></el-input>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="handleCancel">取 消</el-button>
        <el-button type="primary" @click="handleAdd">新建</el-button>
      </div>
    </el-dialog>

    <el-dialog title="新增文件柜格详情" :visible.sync="showAddCaseDialog" :before-close="handleCancel">
      <el-form :model="caseForm">
        <el-form-item
          label="文件柜格名称："
          :label-width="formLabelWidth"
          class="new-filing-item"
        >
          <el-input
            v-model="caseForm.name"
            :clearable="true"
            autocomplete="off"
            size="medium"
          ></el-input>
        </el-form-item>
        <el-form-item
          label="文件类型："
          :label-width="formLabelWidth"
          class="new-filing-item"
        >
          <el-select v-model="caseForm.type">
            <el-option
              v-for="fileType in fileTypes"
              :key="fileType"
              :label="fileType"
              :value="fileType">
            </el-option>
          </el-select>
        </el-form-item>
       <el-form-item
          label="负责人："
          :label-width="formLabelWidth"
          class="new-filing-item"
          style="width:50% !important"
        >
          <el-input
            v-model="caseForm.manager"
            :disabled="true"
            autocomplete="off"
            size="medium"
          ></el-input>
        </el-form-item>
        <el-form-item
          label="备注："
          :label-width="formLabelWidth"
          class="new-filing-item"
        >
          <el-input
            type="textarea"
            v-model="caseForm.remark"
            :clearable="true"
            autocomplete="off"
            size="medium"
          ></el-input>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="handleCancel">取 消</el-button>
        <el-button type="primary" @click="handleAdd">新建</el-button>
      </div>
    </el-dialog>

    <el-dialog title="新增文件盒详情" :visible.sync="showAddBoxDialog" :before-close="handleCancel">
      <el-form :model="boxForm">
        <el-form-item
          label="文件盒名称："
          :label-width="formLabelWidth"
          class="new-filing-item"
        >
          <el-input
            v-model="boxForm.name"
            :clearable="true"
            autocomplete="off"
            size="medium"
          ></el-input>
        </el-form-item>
        <el-form-item
          label="备注："
          :label-width="formLabelWidth"
          class="new-filing-item"
        >
          <el-input
            type="textarea"
            v-model="boxForm.remark"
            :clearable="true"
            autocomplete="off"
            size="medium"
          ></el-input>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="handleCancel">取 消</el-button>
        <el-button type="primary" @click="handleAdd">新建</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import {request} from "@/network/request";

export default {
  props: {
    level: Number,
    id: Number,
    showAddDialog: {
      type: Boolean,
      default: false,
    }
  },
  data() {
    return {
      formLabelWidth:"120px",
      fileTypes: ["文件", "印章"],
      showAddProjectTeamDialog: false,
      showAddCabinetDialog: false,
      showAddCaseDialog: false,
      showAddBoxDialog: false,
      projectTeamForm: {
        name: "",
        remark: "",
        manager: "",
      },
      cabinetForm: {
        name: "",
        remark: "",
        manager: "",
      },
      caseForm: {
        name: "",
        type: "",
        remark: "",
        manager: "",
      },
      boxForm: {
        name: "",
        remark: "",
      }
    }
  },
  methods: {
    handleCancel() {
      if (this.level == 0) {
        this.showAddProjectTeamDialog = false
        this.projectTeamForm = {}
      }
      else if (this.level == 1) {
        this.showAddCabinetDialog = false
        this.cabinetForm = {}
      }
      else if(this.level == 2) {
        this.showAddCaseDialog = false
        this.caseForm = {}
      }
      else if(this.level == 3) {
        this.showAddBoxDialog = false
        this.boxForm = {}
      }
      this.$emit("update:showAddDialog", false)
    },
    handleAdd() {
      if (this.level == 0) {
        request({
          url: 'File/NewFiling',
          method: "get",
          params: {
            level: this.level,
            name: this.projectTeamForm.name,
            remark: this.projectTeamForm.remark,
            manager_id: this.$store.state.auth.currentUser.userid,
            userid: this.$store.state.auth.currentUser.userid
          }
        }).then(res => {
          let data = res.data
          if (data.errcode == 0){
            alert("新建项目组成功！")
            this.handleCancel()
            this.$emit("addSuccess")
          }else {
            alert(data.errmsg)
          }
        }).catch(err => {
          alert(err)
        })
      }
      else if (this.level == 1) {
        request({
          url: 'File/NewFiling',
          method: "get",
          params: {
            level: this.level,
            position_id: this.id,
            name: this.cabinetForm.name,
            remark: this.cabinetForm.remark,
            manager_id: this.$store.state.auth.currentUser.userid,
            userid: this.$store.state.auth.currentUser.userid
          }
        }).then(res => {
          let data = res.data
          if (data.errcode == 0){
            alert("新建文件柜成功！")
            this.handleCancel()
            this.$emit("addSuccess")
          }else {
            alert(data.errmsg)
          }
        }).catch(err => {
          alert(err)
        })
      }
      else if(this.level == 2) {
        request({
          url: 'File/NewFiling',
          method: "get",
          params: {
            level: this.level,
            position_id: this.id,
            name: this.caseForm.name,
            type: this.caseForm.type,
            remark: this.caseForm.remark,
            manager_id: this.$store.state.auth.currentUser.userid,
            userid: this.$store.state.auth.currentUser.userid
          }
        }).then(res => {
          let data = res.data
          if (data.errcode == 0){
            alert("新建文件柜格成功！")
            this.handleCancel()
            this.$emit("addSuccess")
          }else {
            alert(data.errmsg)
          }
        }).catch(err => {
          alert(err)
        })
      }
      else if(this.level == 3) {
        request({
          url: 'File/NewFiling',
          method: "get",
          params: {
            level: this.level,
            position_id: this.id,
            name: this.boxForm.name,
            remark: this.boxForm.remark,
            userid: this.$store.state.auth.currentUser.userid
          }
        }).then(res => {
          let data = res.data
          if (data.errcode == 0){
            alert("新建文件盒成功！")
            this.handleCancel()
            this.$emit("addSuccess")
          }else {
            alert(data.errmsg)
          }
        }).catch(err => {
          alert(err)
        })
      }
    }
  },
  watch: {
    "showAddDialog"(newVal, OldVal) {
      if (newVal) {
        if (this.level == 0) {
          this.projectTeamForm.manager = this.$store.state.auth.currentUser.username
          this.showAddProjectTeamDialog = true
        }else if (this.level == 1) {
          this.cabinetForm.manager = this.$store.state.auth.currentUser.username
          this.showAddCabinetDialog  = true
        }else if (this.level == 2) {
          this.caseForm.manager = this.$store.state.auth.currentUser.username
          this.caseForm.type = "文件"
          this.showAddCaseDialog = true
        }else if (this.level == 3) {
          this.showAddBoxDialog = true
        }
      }
    },
  }
};
</script>

<style lang="scss">

.new-filing-item {
  margin-bottom: 15px !important;
  margin-right: 50px !important;
  .el-input {
    margin-bottom: 0 !important;
  }
}

</style>