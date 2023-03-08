<template>
  <div>
    <el-dialog title="编辑项目组详情" :visible.sync="showEditProjectTeamDialog" :before-close="handleCancel">
      <el-form :model="projectTeamForm">
        <el-form-item
          label="项目组名称："
          :label-width="formLabelWidth"
          class="edit-filing-item"
        >
          <el-input
            v-model="projectTeamForm.name"
            :clearable="true"
            autocomplete="off"
            size="medium"
          ></el-input>
        </el-form-item>
        <el-form-item
          label="位置："
          :label-width="formLabelWidth"
          class="edit-filing-item"
        >
          <el-input
            v-model="projectTeamForm.position"
            :disabled="true"
            autocomplete="off"
            size="medium"
          ></el-input>
        </el-form-item>
        <el-form-item
          label="负责人："
          :label-width="formLabelWidth"
          class="edit-filing-item"
        >
          <el-input
            v-model="projectTeamForm.managerNames"
            :disabled="true"
            autocomplete="off"
            size="medium"
          ></el-input>
        </el-form-item>
        <el-form-item
          label="备注："
          :label-width="formLabelWidth"
          class="edit-filing-item"
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
        <el-button @click.stop="handleCancel">取 消</el-button>
        <el-button type="primary" @click.stop="handleEdit">提交</el-button>
      </div>
    </el-dialog>

    <el-dialog title="编辑文件柜详情" :visible.sync="showEditCabinetDialog" :before-close="handleCancel">
      <el-form :model="cabinetForm">
        <el-form-item
          label="文件柜名称："
          :label-width="formLabelWidth"
          class="edit-filing-item"
        >
          <el-input
            v-model="cabinetForm.name"
            :clearable="true"
            autocomplete="off"
            size="medium"
          ></el-input>
        </el-form-item>
        <el-form-item
          label="位置："
          :label-width="formLabelWidth"
          class="edit-filing-item"
        >
          <el-input
            v-model="cabinetForm.position"
            :disabled="true"
            autocomplete="off"
            size="medium"
          ></el-input>
        </el-form-item>
        <el-form-item
          label="负责人："
          :label-width="formLabelWidth"
          class="edit-filing-item"
        >
          <el-input
            v-model="cabinetForm.managerNames"
            :disabled="true"
            autocomplete="off"
            size="medium"
          ></el-input>
        </el-form-item>
        <el-form-item
          label="备注："
          :label-width="formLabelWidth"
          class="edit-filing-item"
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
        <el-button @click.stop="handleCancel">取 消</el-button>
        <el-button type="primary" @click.stop="handleEdit">提交</el-button>
      </div>
    </el-dialog>

    <el-dialog title="编辑文件柜格详情" :visible.sync="showEditCaseDialog" :before-close="handleCancel">
      <el-form :model="caseForm">
        <el-form-item
          label="文件柜格名称："
          :label-width="formLabelWidth"
          class="edit-filing-item"
        >
          <el-input
            v-model="caseForm.name"
            :clearable="true"
            autocomplete="off"
            size="medium"
          ></el-input>
        </el-form-item>
        <el-form-item
          label="文件柜格类型："
          :label-width="formLabelWidth"
          class="edit-filing-item"
        >
          <el-input
            v-model="caseForm.type"
            :disabled="true"
            autocomplete="off"
            size="medium"
          ></el-input>
        </el-form-item>
        <el-form-item
          label="位置："
          :label-width="formLabelWidth"
          class="edit-filing-item"
        >
          <el-input
            v-model="caseForm.position"
            :disabled="true"
            autocomplete="off"
            size="medium"
          ></el-input>
        </el-form-item>
        <el-form-item
          label="负责人："
          :label-width="formLabelWidth"
          class="edit-filing-item"
        >
          <el-input
            v-model="caseForm.managerNames"
            :disabled="true"
            autocomplete="off"
            size="medium"
          ></el-input>
        </el-form-item>
        <el-form-item label="有借阅权限的用户：" class="edit-filing-item">
          <div>
            <el-tag
              v-for="tag in caseForm.permitUserList"
              :key="tag.id + tag.name"
              closable
              :disable-transitions="false"
              @close="handleClosePermitUserTag(tag)">
              {{tag.name}}
            </el-tag>
            <a @click.stop="resetPermitUser" class="reset">重置</a>
          </div>
          <div class="search-permit-user">
            <el-input
              v-model="permitUserId"
              placeholder="请输入用户工号"
              :clearable="true"
              autocomplete="off"
              size="medium"
              style="width:60% !important;"
            ></el-input>
            <el-button size="medium" type="primary" @click.stop="searchNewPermitUser">添加</el-button>
          </div>
        </el-form-item>
        <el-form-item
          label="备注："
          :label-width="formLabelWidth"
          class="edit-filing-item"
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
        <el-button @click.stop="handleCancel">取 消</el-button>
        <el-button type="primary" @click.stop="handleEdit">提交</el-button>
      </div>
    </el-dialog>

    <el-dialog title="编辑文件盒详情" :visible.sync="showEditBoxDialog" :before-close="handleCancel" class="edit-box-dialog">
      <el-form :model="boxForm">
        <el-form-item
          label="文件盒名称："
          :label-width="formLabelWidth"
          class="edit-filing-item"
        >
          <el-input
            v-model="boxForm.name"
            :clearable="true"
            autocomplete="off"
            size="medium"
          ></el-input>
        </el-form-item>
        <el-form-item label="位置：" class="edit-filing-item" :label-width="formLabelWidth">
        <div>
          <el-tag
            v-for="tag in boxForm.positions"
            :key="tag.id + tag.name"
            closable
            :disable-transitions="false"
            @close="handleClosePositionTag(tag)">
            {{tag.name}}
          </el-tag>
          <a @click.stop="resetPosition" class="reset">重置</a>
        </div>
        <el-cascader
          ref="cascaderPosition"
          @change="handleSelectionChange"
          @visible-change="handleCascaderVisible"
          :props="cascaderProps"
          :options="options"
          clearable>
        </el-cascader>
      </el-form-item>
        <el-form-item
          label="备注："
          :label-width="formLabelWidth"
          class="edit-filing-item"
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
        <el-button @click.stop="handleCancel">取 消</el-button>
        <el-button type="primary" @click.stop="handleEdit">提交</el-button>
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
    showEditDialog: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    let _this = this
    return {
      formLabelWidth:"120px",
      showEditProjectTeamDialog: false,
      showEditCabinetDialog: false,
      showEditCaseDialog: false,
      showEditBoxDialog: false,
      projectTeamForm: {
        name: "",
        managerNames: "",
        position: "",
        remark: "",
      },
      cabinetForm: {
        name: "",
        managerNames: "",
        position: "",
        remark: "",
      },
      caseForm: {
        name: "",
        type: "",
        position: "",
        managerNames: "",
        permitUserList: [],
        remark: "",
      },
      permitUserListTmp: [],
      permitUserId: "",
      boxForm: {
        name: "",
        positions: [],
        remark: "",
      },
      cascaderProps: {
        lazy: true,
        expandTrigger: 'hover',
        lazyLoad (node, resolve) {
          console.log(node)
          if (node.level == 0) return resolve([])
          request({
            url: "File/ChildPositions",
            method: "get",
            params: {
              level: _this.boxForm.positions.length + node.level,
              position: node.value,
              userid: _this.$store.state.auth.currentUser.userid,
              type: _this.$store.state.file.showFilesInfo.belongType,
            }
          }).then(res => {
            let data = res.data
            let childPositions =[]
            if (_this.boxForm.positions.length + node.level >= 2) {
              childPositions = data.res.map(item => ({
                value: item.id,
                label: item.name,
                leaf: true,
              }))
            }else {
              childPositions = data.res.map(item => ({
                value: item.id,
                label: item.name,
                leaf: false,
              }))
            }
            resolve(childPositions)
          }).catch(err => {
            alert(err)
            resolve([])
          })
        }
      },
      positionTmp:[],
      positions:[],
      options:[],
    }
  },
  methods: {
    handleCancel() {
      if (this.level == 1) {
        this.showEditProjectTeamDialog = false
        this.projectTeamForm = {}
      }
      else if (this.level == 2) {
        this.showEditCabinetDialog = false
        this.cabinetForm = {}
      }
      else if(this.level == 3) {
        this.showEditCaseDialog = false
        this.caseForm = {}
      }
      else if(this.level == 4) {
        this.showEditBoxDialog = false
        this.boxForm = {}
      }
      this.$emit("update:showEditDialog", false)
    },
    handleEdit() {
      if (this.level == 1) {
        request({
          url: "File/EditFiling",
          method: "post",
          data: {
            level: this.level,
            id: this.id,
            name: this.projectTeamForm.name,
            remark: this.projectTeamForm.remark,
            userid: this.$store.state.auth.currentUser.userid
          }
        }).then(res => {
          let data = res.data
          if (data.errcode == 0){
            alert("修改项目组成功！")
            this.handleCancel()
            this.$emit("editSuccess")
          }else {
            alert(data.errmsg)
          }
        }).catch(err => {
          alert(err)
        })
      }
      else if (this.level == 2) {
        request({
          url: "File/EditFiling",
          method: "post",
          data: {
            level: this.level,
            id: this.id,
            name: this.cabinetForm.name,
            remark: this.cabinetForm.remark,
            userid: this.$store.state.auth.currentUser.userid
          }
        }).then(res => {
          let data = res.data
          if (data.errcode == 0){
            alert("修改文件柜成功！")
            this.handleCancel()
            this.$emit("editSuccess")
          }else {
            alert(data.errmsg)
          }
        }).catch(err => {
          alert(err)
        })
      }
      else if(this.level == 3) {
        request({
          url: "File/EditFiling",
          method: "post",
          data: {
            level: this.level,
            id: this.id,
            name: this.caseForm.name,
            remark: this.caseForm.remark,
            permitUserList: this.caseForm.permitUserList,
            userid: this.$store.state.auth.currentUser.userid
          }
        }).then(res => {
          let data = res.data
          if (data.errcode == 0){
            alert("修改文件柜格成功！")
            this.handleCancel()
            this.$emit("editSuccess")
          }else {
            alert(data.errmsg)
          }
        }).catch(err => {
          alert(err)
        })
      }
      else if(this.level == 4) {
        if (this.boxForm.positions.length < 3) {
          alert("请将文件盒位置指定到文件柜格！")
          return ;
        } 
        request({
          url: "File/EditFiling",
          method: "post",
          data: {
            level: this.level,
            id: this.id,
            name: this.boxForm.name,
            remark: this.boxForm.remark,
            position_id:this.boxForm.positions[2].id,
            userid: this.$store.state.auth.currentUser.userid
          }
        }).then(res => {
          let data = res.data
          if (data.errcode == 0){
            alert("修改文件盒成功！")
            this.handleCancel()
            this.$emit("editSuccess")
          }else {
            alert(data.errmsg)
          }
        }).catch(err => {
          alert(err)
        })
      }
    },
    handleClosePermitUserTag(tag) {
      const pos = this.caseForm.permitUserList.indexOf(tag)
      this.caseForm.permitUserList.splice(pos, 1);
    },
    resetPermitUser() {
      this.caseForm.permitUserList = this.permitUserListTmp.slice(0)
    },
    searchNewPermitUser() {
      request({
        url: "User/NewPermitUser",
        method: "get",
        params: {
          userid: this.permitUserId
        }
      }).then(res => {
        let data = res.data
        if (data.errcode==0) {
          this.caseForm.permitUserList.push(data.user)
        }else {
          alert(data.errmsg)
        }
      }).catch(err => {
        alert(err)
      })
    },
    handleClosePositionTag(tag) {
      const pos = this.boxForm.positions.indexOf(tag)
      this.boxForm.positions.splice(pos, this.boxForm.positions.length-pos);
    },
    resetPosition() {
      this.boxForm.positions = this.positionTmp.slice(0)
    },
    handleCascaderVisible(sta) {
      if (sta) {
        if (this.boxForm.positions.length >= 3) {
          this.options = []
          return ;
        }
        this.positions = this.boxForm.positions.slice(0)
        let level = 0;
        let position = 0;
        if (this.boxForm.positions.length > 0) {
          level = this.boxForm.positions.length
          position = this.boxForm.positions[this.boxForm.positions.length-1].id
        }
        request({
          url: "File/ChildPositions",
          method: "get",
          params: {
            level: level,
            position: position,
            userid: this.$store.state.auth.currentUser.userid,
            type: this.$store.state.file.showFilesInfo.belongType,
          }
        }).then(res => {
          let data = res.data
          let rootPositions = []
          if (this.boxForm.positions.length == 2) {
            rootPositions = data.res.map(item => ({
              value: item.id,
              label: item.name,
              leaf: true,
            }))
          }else {
            rootPositions = data.res.map(item => ({
              value: item.id,
              label: item.name,
              leaf: false,
            }))
          }
          this.options = rootPositions
        }).catch(err => {
          alert(err)
        })
      }
    },
    handleSelectionChange(val) {
      let leafObj = this.$refs["cascaderPosition"].getCheckedNodes()[0]
      this.boxForm.positions = this.positions.slice(0)
      let pos = this.boxForm.positions.length
      while(leafObj!=null) {
        this.boxForm.positions.splice(pos,0,{
          id: leafObj.value,
          name: leafObj.label
        })
        leafObj = leafObj.parent
      }  
    },
  },
  watch: {
    "showEditDialog"(newVal, OldVal) {
      if (newVal) {
        request({
          url: "File/EditFilingInfo",
          method: "get",
          params: {
            level: this.level,
            id: this.id,
          }
        }).then(res => {
          let data = res.data
          if (data.errcode == 0) {
            if (this.level == 1) {
              this.projectTeamForm = data.res
              this.showEditProjectTeamDialog = true
            }else if (this.level == 2) {
              this.cabinetForm = data.res
              this.showEditCabinetDialog  = true
            }else if (this.level == 3) {
              this.caseForm = data.res
              this.permitUserListTmp = this.caseForm.permitUserList.slice(0)
              this.showEditCaseDialog = true
            }else if (this.level == 4) {
              this.boxForm = data.res
              this.positionTmp = this.boxForm.positions.slice(0)
              this.showEditBoxDialog = true
            }
          }else {
            alert(data.errmsg)
          }
        }).catch(err => {
          alert(err)
        })
      }
    },
  }
};
</script>

<style lang="scss">

.edit-box-dialog {
  .el-dialog {
    width: 50%;
  }
} 

.edit-filing-item {
  margin-bottom: 15px !important;
  margin-right: 50px !important;
  
  .el-input {
    margin-bottom: 0 !important;
  }

  .el-cascader {
    width:70% !important;
  }
}

.search-permit-user {
  margin-left:120px;

}

.reset {
  float: right;
  margin-right: 30px;
  color:cornflowerblue;
}

.reset:hover {
  text-decoration: underline !important;
  cursor: pointer;
  color:red;
}

</style>