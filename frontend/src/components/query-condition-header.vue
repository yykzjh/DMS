<template>
  <div style="margin-top: 20px">
    <label for="creator" style="padding-left: 20px">创建人：</label>
    <el-input
      id="creator"
      :clearable="true"
      class="query-condition-item"
      placeholder="创建人姓名"
      v-model="creator">
    </el-input>
    <label for="filename" style="padding-left: 20px">文件名：</label>
    <el-input
      id="filename"
      :clearable="true"
      class="query-condition-item"
      placeholder="文件名关键词"
      v-model="fileName"
    >
      <el-button
        slot="append"
        icon="el-icon-search"
        @click="handleConditionSearch"
      ></el-button>
    </el-input>
    <el-button
      v-if="$store.state.auth.currentUser.permissions.indexOf(31)!=-1&&havePermission"
      type="primary"
      style="position: absolute; right: 20px"
      @click="handleAddFile"
    >
      <i class="ri-add-line"></i>
      新增文件
    </el-button>

    <!-- 弹出新增文件表单 -->
    <el-dialog
      title="新增文件详情"
      :close-on-click-modal="false"
      :destroy-on-close="true"
      :visible.sync="dialogFormVisible">
      <el-form :model="fileForm">
        <el-form-item
          label="文件名："
          :label-width="formLabelWidth"
          class="new-file-item"
        >
          <el-input
            v-model="fileForm.name"
            autocomplete="off"
            size="medium"
          ></el-input>
        </el-form-item>
        <el-form-item
          label="位置："
          :label-width="formLabelWidth"
          class="new-file-item"
        >
          <el-input
            v-model="fileForm.position"
            autocomplete="off"
            :disabled="true"
            size="medium"
          ></el-input>
        </el-form-item>
        <el-form-item
          label="创建者："
          :label-width="formLabelWidth"
          class="new-file-item"
        >
          <el-input
            v-model="fileForm.creatorName"
            autocomplete="off"
            :disabled="true"
            size="medium"
          ></el-input>
        </el-form-item>
        <el-form-item
          label="种类："
          :label-width="formLabelWidth"
          class="new-file-item"
        >
          <el-input
            v-model="fileForm.type"
            autocomplete="off"
            :disabled="true"
            size="medium"
          ></el-input>
        </el-form-item>
        <el-form-item
          label="选择文件："
          :label-width="formLabelWidth"
          class="new-file-item"
        >
          <el-upload
            class="upload-file"
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
        <el-form-item
          label="版本描述："
          :label-width="formLabelWidth"
          class="new-file-item"
        >
          <el-input
            v-model="fileForm.versionDescription"
            autocomplete="off"
            size="medium"
          ></el-input>
        </el-form-item>
        <el-form-item
          label="备注："
          :label-width="formLabelWidth"
          class="new-file-item"
        >
          <el-input
            type="textarea"
            :rows="2"
            placeholder="请输入备注"
            v-model="fileForm.remark"
            autocomplete="off"
            size="medium"
          ></el-input>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogFormVisible = false">取 消</el-button>
        <el-button type="primary" @click="submitUploadFile">上 传</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { request } from "@/network/request";

export default {
  props: {
    fileNameProp: {
      type: String,
      default: "",
    },
    creatorProp: {
      type: String,
      default: "",
    },
    havePermission: Boolean,
  },
  data() {
    return {
      fileName: this.fileNameProp,
      creator: this.creatorProp,
      dialogFormVisible: false,
      fileForm: {
        name: "",
        level: 0,
        id: 0,
        position: "",
        creatorId: "",
        creatorName: "",
        creator: "",
        versionDescription: "",
        remark: "",
      },
      formLabelWidth: "100px",
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
    };
  },
  methods: {
    handleConditionSearch() {
      let newShowFilesInfo = {
        level: this.$store.state.file.showFilesInfo.level,
        id: this.$store.state.file.showFilesInfo.id,
        page: 1,
        pageSize: this.$store.state.file.showFilesInfo.pageSize,
        showfileDetails: this.$store.state.file.showFilesInfo.showfileDetails,
        havePermission: this.$store.state.file.showFilesInfo.havePermission,
        fileName: this.fileName,
        creator: this.creator,
        belongType: this.$store.state.file.showFilesInfo.belongType,
        fileHaveChange:this.$store.state.file.showFilesInfo.fileHaveChange
      };
      this.$store.commit("file/SET_SHOW_FILES_INFO", newShowFilesInfo);
    },
    handleAddFile() {
      this.fileForm.level = this.$store.state.file.showFilesInfo.level;
      this.fileForm.id = this.$store.state.file.showFilesInfo.id;
      request({
        url: "File/FolderPosition",
        method: "get",
        params: {
          level: this.fileForm.level,
          id: this.fileForm.id,
        },
      }).then((res) => {
        let data = res.data;
        this.fileForm.position = data.position;
      }).catch((err) => {
        alert(err);
      });
      this.fileForm.creatorId = this.$store.state.auth.currentUser.userid;
      this.fileForm.creatorName = this.$store.state.auth.currentUser.username;
      this.fileForm.type = this.$store.state.file.showFilesInfo.belongType;
      this.dialogFormVisible = true;
    },
    submitUploadFile() {
      if (this.fileList.length == 0) {
        alert("请选择要上传的文件！")
        return ;
      }
      console.log(this.fileList)
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
      this.dialogFormVisible = false;
      this.fileData = new FormData();
      this.$refs.upload.submit();
      this.fileData.append("name", this.fileForm.name);
      this.fileData.append("level", this.fileForm.level);
      this.fileData.append("position_id", this.fileForm.id);
      this.fileData.append("creator_id", this.fileForm.creatorId);
      this.fileData.append("type", this.fileForm.type);
      this.fileData.append(
        "version_description",
        this.fileForm.versionDescription
      );
      this.fileData.append("remark", this.fileForm.remark);
      request({
        url: "File/NewFile",
        method: "post",
        headers: {
          "Content-Type": "multipart/form-data",
        },
        data: this.fileData,
      }).then((res) => {
        const data = res.data
        if (data.errcode == 0) {
          this.$message({
            type: 'success',
            message: '新建文件成功！!'
          });
          this.fileData = ""
          this.fileList = []
          this.fileForm.name = ""
          this.fileForm.versionDescription = ""
          this.fileForm.remark = ""
          this.$store.commit("file/SET_FILE_CHANGE", !this.$store.state.file.showFilesInfo.fileHaveChange)
        }else {
          alert(data.errmsg)
        }
      }).catch((err) => {
        alert(err);
      });
    },
    commitFilesToFormData(file) {
      this.fileData.append("files", file.file);
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
  },
};
</script>

<style lang="scss" scoped>

.query-condition-item {
  width: 200px;
  font-size: 0.8rem;
}

.el-select {
  width: 120px;
}

.el-dialog {
  width: 40%;
  margin-top: 10vh !important;
}

.new-file-item {
  margin-bottom: 15px !important;
  margin-right: 50px !important;
  .el-input {
    margin-bottom: 0 !important;
  }
}

.el-upload__tip {
  display: inline-block;
  margin-left: 10px;
}

.el-upload-list__item {
  margin-top: 2px !important;
}

.el-upload-list__item:first-child {
  margin-top: 0 !important;
}

.upload-file {
  position: relative;
  top: -8px;
}
</style>