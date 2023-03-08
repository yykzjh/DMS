<template>
  <el-dialog title="编辑文件详情" :visible.sync="editDialogFormVisible" class="edit-file-info">
    <el-form ref="fileForm" :model="fileInfo" label-width="100px" class="edit-file-form">
      <el-form-item label="文件名：" class="edit-file-item" style="width:70% !important;">
        <el-input v-model="fileInfo.name"></el-input>
      </el-form-item>
      <el-form-item label="位置：" class="edit-file-item">
        <div class="show-position-box">
          <el-tag
            v-for="tag in fileInfo.position"
            :key="tag.id + tag.name"
            closable
            :disable-transitions="false"
            @close="handleCloseTag(tag)">
            {{tag.name}}
          </el-tag>
          <a @click="resetPosition" class="reset-position">重置</a>
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
      <el-form-item label="创建人：" class="edit-file-item" style="width:50% !important;">
        <el-input :disabled="true" v-model="fileInfo.creator"></el-input>
      </el-form-item>
      <el-form-item label="创建时间：" class="edit-file-item" style="width:60% !important;">
        <el-input :disabled="true" v-model="fileInfo.createTime"></el-input>
      </el-form-item>
      <el-form-item label="类型：" class="edit-file-item" style="width:40% !important;">
        <el-input :disabled="true" v-model="fileInfo.type"></el-input>
      </el-form-item>
      <el-form-item label="备注：" class="edit-file-item">
        <el-input type="textarea" v-model="fileInfo.remark"></el-input>
      </el-form-item>
      <el-form-item label="文件版本：" class="edit-file-item" style="margin-top:30px !important;">
        <el-select v-model="fileInfo.currentVersion">
          <el-option
            v-for="version in fileInfo.versions"
            :key="version.id"
            :label="version.description"
            :value="version.id">
          </el-option>
        </el-select>
        <el-button style="margin-left:30px;" type="primary" round @click.stop="handleUpdateFileVersion">版本更新</el-button>
        <el-dialog
          width="30%"
          title="新版本描述和附件:"
          :visible.sync="innerVisible"
          append-to-body>
          <el-form-item
            label="版本描述："
            label-width="100px"
            class="edit-file-item">
            <el-input
              v-model="newVersionDescription"
              autocomplete="off"
              size="medium"
            ></el-input>
          </el-form-item>
          <el-form-item
            label="选择文件："
            label-width="100px"
            class="edit-file-item">
            <el-upload
              class="version-upload-file"
              ref="upload"
              multiple
              :limit="5"
              action="javascript:void(0)"
              :http-request="commitFilesToFormData"
              :file-list="fileList"
              :on-preview="handlePreview"
              :on-change="handleChange"
              :on-remove="handleRemoveFile"
              :auto-upload="false"
            >
              <el-button slot="trigger" size="small" type="primary"
                >选取文件</el-button
              >
              <div slot="tip" class="el-upload__tip">
                只能上传jpg/jpeg/png/txt/doc/docx/pdf/xls/xlsx文件，且最多5个文件，总共不超过25Mb
              </div>
            </el-upload>
          </el-form-item>
          <div slot="footer" class="edit-dialog-footer">
            <el-button @click.stop="innerVisible = false">取 消</el-button>
            <el-button type="primary" @click.stop="submitUploadVersion">上 传</el-button>
          </div>
        </el-dialog>
      </el-form-item>
      <el-form-item class="edit-file-item" style="margin-top:30px !important;">
        <el-button type="primary" @click.stop="onSubmitEdit">提交修改</el-button>
        <el-button @click.stop="editDialogFormVisible=false">取消</el-button>
      </el-form-item>
    </el-form>
  </el-dialog>
</template>

<script>
import { request } from "@/network/request";

export default {
  props: {
    editDialogFormVisibleProp: {
      type: Boolean,
      default: false
    },
    editFileId: {
      type: Number,
      default: 0
    },
    editFileInfo: Object,
  },
  data() {
    let _this = this
    return {
      editDialogFormVisible: false,
      fileInfo: {
        name: "",
        position: [],
        remark: "",
        id: 0,
        type: "",
        createTime: "",
        versions: [],
        currentVersion: 0,
        creator: ""
      },
      originPositions: [],
      positions: [],
      options:[],
      cascaderProps: {
        checkStrictly: true,
        lazy: true,
        expandTrigger: 'hover',
        lazyLoad (node, resolve) {
          console.log(node)
          if (node.level == 0) return resolve([])
          request({
            url: "File/ChildPositions",
            method: "get",
            params: {
              level: _this.fileInfo.position.length + node.level,
              position: node.value,
              userid: _this.$store.state.auth.currentUser.userid,
              type: _this.$store.state.file.showFilesInfo.belongType,
            }
          }).then(res => {
            let data = res.data
            let childPositions = data.res.map(item => ({
              value: item.id,
              label: item.name
            }))
            resolve(childPositions)
          }).catch(err => {
            alert(err)
            resolve([])
          })
        }
      },
      innerVisible: false,
      newVersionDescription: "",
      fileData: "", //上传的整个表单数据
      fileList: [], // 暂存的要上传的文件列表
      requireFileTypes: [
        "image/jpeg",
        "image/png",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/pdf",
        "text/plain",
      ],
    }
  },
  watch: {
    "editDialogFormVisibleProp"(newVal, oldVal) {
      this.editDialogFormVisible = newVal
    },
    editDialogFormVisible: {
      handler: "handleVisibleChange"
    },
    "editFileInfo"(newVal, oldVal) {
      this.fileInfo = newVal
      this.originPositions = this.fileInfo.position.slice(0)
    },
  },
  methods: {
    handleVisibleChange(newVal, oldVal) {
      this.$emit("update:editDialogFormVisibleProp", newVal)
    },
    handleCascaderVisible(sta) {
      if (sta) {
        this.positions = this.fileInfo.position.slice(0)
        let level = 0;
        let position = 0;
        if (this.fileInfo.position.length > 0) {
          level = this.fileInfo.position.length
          position = this.fileInfo.position[this.fileInfo.position.length-1].id
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
          let rootPositions = data.res.map(item => ({
            value: item.id,
            label: item.name
          }))
          this.options = rootPositions
        }).catch(err => {
          alert(err)
        })
      }
    },
    handleSelectionChange(val) {
      let leafObj = this.$refs["cascaderPosition"].getCheckedNodes()[0]
      this.fileInfo.position = this.positions.slice(0)
      let pos = this.fileInfo.position.length
      while(leafObj!=null) {
        this.fileInfo.position.splice(pos,0,{
          id: leafObj.value,
          name: leafObj.label
        })
        leafObj = leafObj.parent
      }  
    },
    handleCloseTag(tag) {
      const pos = this.fileInfo.position.indexOf(tag)
      this.fileInfo.position.splice(pos, this.fileInfo.position.length-pos);
    },
    resetPosition() {
      this.fileInfo.position = this.originPositions.slice(0)
    },
    handleUpdateFileVersion() {
      this.innerVisible = true
    },
    commitFilesToFormData(file) {
      this.fileData.append("files", file.file);
    },
    submitUploadVersion() {
      if (this.fileList.length == 0) {
        alert("请选择要上传的文件！")
        return ;
      }
      let totalSize = this.fileList.reduce((total, file) => {
        return total + file.size;
      },0)
      const isSizeOver = (totalSize / 1024 / 1024) < 25;
      if (!isSizeOver) {
        alert("请检查，上传文件大小不能超过25MB!");
        return;
      }
      const isTypeNotMeet = this.fileList.some((file) => 
        this.requireFileTypes.indexOf(file.raw.type) == -1
      );
      if (isTypeNotMeet) {
        alert("请检查，上传文件的格式不满足条件！");
        return;
      }
      this.innerVisible = false;
      this.fileData = new FormData();
      this.$refs.upload.submit();
      this.fileData.append(
        "version_description",
        this.newVersionDescription
      );
      this.fileData.append("fileId", this.fileInfo.id)
      request({
        url: "File/NewVersion",
        method: "post",
        headers: {
          "Content-Type": "multipart/form-data",
        },
        data: this.fileData,
      }).then((res) => {
        let data = res.data
        if (data.errcode==0){
          alert("上传成功！");
          this.fileInfo.versions.push(data.newVersion)
          this.fileInfo.currentVersion = data.newVersion.id
        }
        else{
          alert(data.errmsg)
        }
        this.fileData = ""
        this.fileList = []
        this.newVersionDescription = ""
      }).catch((err) => {
        alert("上传失败！");
      });
    },
    handlePreview(file) {
      console.log(file);
    },
    handleRemoveFile(file, fileList) {
      console.log(fileList);
    },
    handleChange(file, fileList) {
      let existFile = fileList
        .slice(0, fileList.length - 1)
        .find((f) => f.name === file.name);
      if (existFile) {
        alert("当前文件已经存在!");
        fileList.pop();
      }
      this.fileList = fileList;
    },
    onSubmitEdit() {
      if (this.fileInfo.position.length < 3) {
        alert("请把文件的存放位置确定到文件柜格、文件盒！")
        return ;
      }
      request({
        url: "File/EditFile",
        method: "post",
        data: {
          fileId: this.fileInfo.id,
          name: this.fileInfo.name,
          level: this.fileInfo.position.length,
          position: this.fileInfo.position[this.fileInfo.position.length-1].id,
          remark: this.fileInfo.remark,
          versionId: this.fileInfo.currentVersion,
          userid: this.$store.state.auth.currentUser.userid
        }
      }).then(res => {
        let data = res.data
        if (data.errcode==0) {
          alert("修改成功！")
          this.editDialogFormVisible = false
          this.$store.commit("file/SET_FILE_CHANGE", !this.$store.state.file.showFilesInfo.fileHaveChange)
        }else{
          alert(data.errmsg)
        }
      }).catch(err => {
        alert(err)
      })
    }
  }
}
</script>

<style lang="scss">

.edit-file-info {
  .el-dialog {
    width: 60%;
    margin-top: 7vh !important;
  }
}

.edit-file-form .edit-file-item {
  margin-bottom: 10px !important;

  .el-cascader {
    width:70% !important;
  }

  .el-select {
    width:70% !important;
  }
}

.version-upload-file {
  position: relative;
  top: -8px;
}

.reset-position {
  float: right;
  margin-right: 30px;
  color:cornflowerblue;
}

.reset-position:hover {
  text-decoration: underline !important;
  cursor: pointer;
  color:red;
}

</style>