<template>
  <div class="tree-folder" style="display: block">
    <div class="tree-folder-header">
      <i
        class="ri-folder-fill"
        :class="{ red: level == 2, orange: level == 3, blue: level == 4 }"
        v-if="!isOpen"
        @click.stop="openFile()"
      ></i>
      <i
        class="ri-folder-open-fill"
        :class="{ red: level == 2, orange: level == 3, blue: level == 4 }"
        v-else
      ></i>
      <div class="tree-folder-name" @click.stop="openFile()">{{ name }}</div>
      <span class="operation-icon" v-if="showAdd" @click.stop="handleAdd">
        <i class="ri-add-circle-fill"></i>
      </span>
      <span class="operation-icon" v-if="showEdit" @click.stop="handleEdit">
        <i class="ri-edit-2-fill"></i>
      </span>
      <span class="operation-icon" v-if="showDelete" @click.stop="handleDelete">
        <i class="ri-delete-bin-6-fill"></i>
      </span>
    </div>

    <div class="tree-folder-content" v-if="isOpen && !isLoading && level < 4">
      <tree-node
        v-for="childFile in childFiles"
        :key="childFile.id"
        :id="childFile.id"
        :name="childFile.name"
        :type="childFile.type"
        :haveBelongType="belongType"
        :position="childFile.position"
        :remark="childFile.remark"
        :managers="childFile.managers"
        :level="level + 1"
        :havePermission="currentPermission"
        :havePermitBorrow="currentPermission"
        :userid="userid"
        :permissionUsers="childFile.permission_users"
        :isOpenProp="openId==childFile.id"
        @open-file="handleOpenFile"
        @refresh-structure="handleRefreshStructure"
      >
      </tree-node>
    </div>

    <div class="tree-loader" v-if="isLoading">
      <div class="tree-loading">
        <i class="ri-refresh-line icon-spin blue"></i>
      </div>
    </div>

    <NewFilingDialog
      :level="level"
      :id="id"
      :showAddDialog.sync="showAddDialog"
      @addSuccess="handleRefreshStructure"
    ></NewFilingDialog>

    <EditFilingDialog
      :level="level"
      :id="id"
      :showEditDialog.sync="showEditDialog"
      @editSuccess="$emit('refresh-structure')"
    ></EditFilingDialog>
  </div>
</template>

<script>
import { request } from "@/network/request";
import NewFilingDialog from "./new-filing-dialog";
import EditFilingDialog from "./edit-filing-dialog";

export default {
  name: "tree-node",
  components: {
    NewFilingDialog,
    EditFilingDialog,
  },
  props: {
    id: Number,
    name: {
      type: String,
      default: "东配楼办事处第一组",
    },
    type: String,
    position: Number,
    remark: String,
    managers: Array,
    permissionUsers: Array,
    level: Number,
    havePermission: {
      type: Boolean,
      default: false,
    },
    havePermitBorrow: {
      type: Boolean,
      default: false,
    },
    haveBelongType: {
      type: String,
      default: ""
    },
    userid: String,
    isOpenProp:false,
  },
  data() {
    return {
      childFiles: [],
      isOpen: false,
      isLoading: false,
      belongType:"",
      openId: 0,
      showAddDialog: false,
      showEditDialog: false,
    };
  },
  computed: {
    currentPermission() {
      return (
        this.havePermission ||
        (this.managers != undefined && this.managers.indexOf(this.userid) != -1)
      );
    },
    currentPermitBorrow() {
      return (
        this.currentPermission ||
        this.havePermitBorrow ||
        (this.permissionUsers != undefined &&
          this.permissionUsers.indexOf(this.userid) != -1)
      );
    },
    showAdd() {
      if (this.level==1) {
        return this.$store.state.auth.currentUser.permissions.indexOf(22)!=-1 && this.currentPermission
      }
      else if (this.level == 2) {
        return this.$store.state.auth.currentUser.permissions.indexOf(23)!=-1 && this.currentPermission
      }
      else if (this.level == 3) {
        return this.$store.state.auth.currentUser.permissions.indexOf(24)!=-1 && this.currentPermission
      }
      else return false
    },
    showEdit() {
      if (this.level==1) {
        return this.$store.state.auth.currentUser.permissions.indexOf(25)!=-1 && this.currentPermission
      }
      else if (this.level == 2) {
        return this.$store.state.auth.currentUser.permissions.indexOf(26)!=-1 && this.currentPermission
      }
      else if (this.level == 3) {
        return this.$store.state.auth.currentUser.permissions.indexOf(27)!=-1 && this.currentPermission
      }
      else if (this.level == 4) {
        return this.$store.state.auth.currentUser.permissions.indexOf(28)!=-1 && this.currentPermission
      }
      else return false
    },
    showDelete() {
      if (this.level == 4) {
        return this.$store.state.auth.currentUser.permissions.indexOf(29)!=-1 && this.currentPermission
      }
      else return false
    },
  },
  methods: {
    openFile() {
      if (this.isOpen) {
        this.isOpen = false;
      } else {
        this.isOpen = true;
        this.$emit("open-file", this.id)
        if (this.level <= 3){
          this.isLoading = true;
          request({
            url: "File/ChildFolders",
            method: "get",
            params: {
              level: this.level,
              position: this.id,
            },
          }).then((res) => {
            let data = res.data;
            // console.log(data);
            this.childFiles = data.res;
            this.isLoading = false;
            if (this.level < 3)
              this.$store.commit('file/SET_OPEN_FOLDER', false)
          }).catch((err) => {
            alert(err);
          });
        }
        if (this.level==3||this.level==4){
          let newShowFilesInfo = {
            level: this.level,
            id: this.id,
            page: 1,
            pageSize: 5,
            showfileDetails: this.currentPermitBorrow,
            havePermission: this.currentPermission,
            fileName: "",
            creator: "",
            belongType: this.belongType,
            fileHaveChange:this.$store.state.file.showFilesInfo.fileHaveChange
          }
          this.$store.commit('file/SET_SHOW_FILES_INFO',newShowFilesInfo)
          this.$store.commit('file/SET_OPEN_FOLDER', true)
        }
      }
    },
    handleOpenFile(folderId) {
      this.openId = folderId
    },
    handleAdd() {
      this.showAddDialog = true
    },
    handleEdit() {
      this.showEditDialog = true
    },
    handleDelete() {
      this.$confirm('此操作将永久删除该文件, 是否继续?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        request({
          url: "File/DeleteFilingBox",
          method: "get",
          params: {
            boxId: this.id,
            userid: this.$store.state.auth.currentUser.userid
          }
        }).then( res => {
          let data = res.data
          if (data.errcode==0) {
            this.$message({
              type: 'success',
              message: '删除成功!'
            });
            this.$emit("refresh-structure")
          }else{
            alert(data.errmsg)
          }
        }).catch(err => {
          alert(err)
        })
      }).catch(() => {
        this.$message({
          type: 'info',
          message: '已取消删除'
        });          
      });
    },
    handleRefreshStructure() {
      this.isOpen = false
      this.openFile()
    }
  },
  watch: {
    "isOpenProp"(newVal, oldVal) {
      this.isOpen = newVal
    }
  },
  mounted: function(){
    this.belongType = this.haveBelongType!=""?this.haveBelongType:this.type
  }
};
</script>

<style scoped>
.operation-icon {
  color: #67b2dd;
}

.tree-folder {
  width: auto;
  min-height: 20px;
  cursor: pointer;
  position: relative;
}

.tree-folder:before {
  display: inline-block;
  content: "";
  position: absolute;
  top: 14px;
  left: -13px;
  width: 18px;
  height: 0;
  border-top: 1px dotted #67b2dd;
  z-index: 1;
}

.tree-folder .tree-folder-header {
  margin: 0;
  padding: 5px;
  border-radius: 0;
  color: #4d6878;
  position: relative;
  height: 20px;
  line-height: 20px;
  display: flex;
  justify-content: flex-start;
  -webkit-box-sizing: content-box;
  -moz-box-sizing: content-box;
  box-sizing: content-box;
}

.tree-folder .tree-folder-content {
  margin-left: 23px;
  position: relative;
}

.tree-folder .tree-folder-content:before {
  display: inline-block;
  content: "";
  position: absolute;
  z-index: 1;
  top: -10px;
  bottom: 16px;
  left: -14px;
  border: 1px dotted #67b2dd;
  border-width: 0 0 0 1px;
}

.tree-folder .tree-folder-header .tree-folder-name {
  margin-left: 4px;
  display: inline;
  z-index: 2;
}

.tree .tree-loading {
  margin-left: 36px;
}

.tree .icon-spin {
  height: auto;
}

.blue {
  color: #478fca !important;
}

.icon-spin {
  text-align: center;
  display: inline-block;
  -moz-animation: spin 2s infinite linear;
  -o-animation: spin 2s infinite linear;
  -webkit-animation: spin 2s infinite linear;
  animation: spin 2s infinite linear;
}

.operation-icon {
  margin-left: 4px;
}

.red {
  color: #dd5a43 !important;
}

.orange {
  color: #ff892a !important;
}

.blue {
  color: #478fca !important;
}
</style>