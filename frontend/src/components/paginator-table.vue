<template>
  <div>
    <el-table
      :data="data"
      :max-height="tableMaxHeight"
      :stripe="true"
      :border="true"
      :show-header="true"
      :highlight-current-row="true"
      :row-key="rowKey"
      :empty-text="'暂无数据'"
      :select-on-indeterminate="selectOnIndeterminate"
      style="width:100%;"
      v-loading="loading"
      tooltip-effect="light"
      @selection-change="handleSelectionChange"
    >
    
      <el-table-column v-for="column in columns"
        :key="column.prop"
        :type="column.type"
        :column-key="column.prop"
        :label="column.label"
        :prop="column.prop"
        :min-width="column.minWidth"
        :fixed="column.fixed"
        :sortable="column.sortable==null?true:column.sortable"
        :resizable="column.resizable"
        align="center"
        header-align="center"
        :show-overflow-tooltip="column.prop=='remark'||column.prop=='position'"
      ></el-table-column>
      <el-table-column
        :min-width="210"
        :fixed="'right'"
        :resizable="true"
        align="center"
        header-align="center"
        label="操作">
        <template slot-scope="scope">
          <el-button
            v-if="$store.state.auth.currentUser.permissions.indexOf(30)!=-1&&(havePermission || showfileDetails || scope.row.permit==1)"
            size="mini"
            type="primary"
            @click.stop="handleLook(scope.$index, scope.row)">查看</el-button>
          <el-button
            v-if="$store.state.auth.currentUser.permissions.indexOf(32)!=-1&&havePermission"
            size="mini"
            type="info"
            @click.stop="handleEdit(scope.$index, scope.row)">编辑</el-button>
          <el-button
            v-if="$store.state.auth.currentUser.permissions.indexOf(33)!=-1&&havePermission"
            size="mini"
            type="danger"
            @click.stop="handleDelete(scope.$index, scope.row)">删除</el-button>
          <el-button
            v-if="$store.state.auth.currentUser.permissions.indexOf(30)!=-1&&(!havePermission && !showfileDetails && scope.row.permit==0)"
            size="mini"
            type="success"
            @click.stop="handleBorrow(scope.$index, scope.row)">借阅</el-button>
          <span style="margin-left=2px; color:blue;" v-if="!havePermission && !showfileDetails && scope.row.permit==2">等待审核</span>
          <span style="margin-left=2px; color:red;" v-if="!havePermission && !showfileDetails && scope.row.permit==3">借阅已超时</span>
          <span style="margin-left=2px; color:yellow;" v-if="!havePermission && !showfileDetails && scope.row.permit==4">等待确认归还</span>
        </template>
      </el-table-column>
    </el-table>
    <!-- 分页栏 -->
    <div class="ops">
      <el-button
        v-if="$store.state.auth.currentUser.permissions.indexOf(33)!=-1&&havePermission"
        type="danger" 
        icon="el-icon-delete"
        @click.stop="handleSelectionDelete"
        class="button-float-left">
        删除选中文件
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
    <DownLoadFileDialog
      :fileId="fileId"
      :fileInfo="fileInfo"
      :dialogFormVisibleProp.sync="dialogFormVisibleProp"
    ></DownLoadFileDialog>
    <EditFileDialog
      :editFileId="editFileId"
      :editFileInfo="editFileInfo"
      :editDialogFormVisibleProp.sync="editDialogFormVisibleProp"
    ></EditFileDialog>
    <BorrowFileDialog
      :borrowFile="borrowFile"
      :borrowUser="borrowUser"
      :showBorrowFileDialog.sync="showBorrowFileDialog"
    ></BorrowFileDialog>
  </div>
</template>

<script>
import { request } from "@/network/request";
import DownLoadFileDialog from "@/components/download-file-dialog";
import EditFileDialog from "@/components/edit-file-dialog";
import BorrowFileDialog from "@/components/borrow-file-dialog";

export default {
  components: {DownLoadFileDialog, EditFileDialog, BorrowFileDialog},
  name: "PaTable",
  props: {
    data: {
      type: Array,
      default: [],
    },
    tableMaxHeight: { // 表的最大高度
      type: Number,
      default: 600,
    },
    highlightCurrentRow: { //是否高亮显示点击的行
      type: Boolean,
      default: true
    },
    rowKey: { //行数据的key
      type: String,
      default: "id"
    },
    selectOnIndeterminate: { //表头多选框的作用，true:全选，false:全取消
      type: Boolean,
      default: true
    },
    columns: { //列的各个属性,可设置：type,index,label,prop,minWidth,fixed,sortable,resizable,filters
      type: Array,
      default: []
    },
    loading: {
      type:Boolean,
      default:true
    },
    havePermission: Boolean,
    showfileDetails: Boolean,
    page: {
      type: Number,
      default: 1
    },
    pageSize: {
      type: Number,
      default: 5
    },
    totalSize: {
      type: Number,
      default: 0
    }
  },
  data() {
    return {
      selectedFilesIds: [],
      fileId: 0,
      fileInfo: [],
      dialogFormVisibleProp: false,
      editFileId: 0,
      editFileInfo: {
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
      editDialogFormVisibleProp: false,
      borrowFile: {},
      borrowUser: {},
      showBorrowFileDialog: false,
    }
  },
  methods:{
    handleSizeChange(val) {
      let newShowFilesInfo = {
        level: this.$store.state.file.showFilesInfo.level,
        id: this.$store.state.file.showFilesInfo.id,
        page: this.$store.state.file.showFilesInfo.page,
        pageSize: val,
        showfileDetails: this.$store.state.file.showFilesInfo.showfileDetails,
        havePermisson: this.$store.state.file.showFilesInfo.havePermisson,
        fileName: this.$store.state.file.showFilesInfo.fileName,
        creator: this.$store.state.file.showFilesInfo.creator,
        belongType: this.$store.state.file.showFilesInfo.belongType,
        fileHaveChange:this.$store.state.file.showFilesInfo.fileHaveChange
      }
      this.$store.commit('file/SET_SHOW_FILES_INFO',newShowFilesInfo)
    },
    handlePageChange(val) {
      let newShowFilesInfo = {
        level: this.$store.state.file.showFilesInfo.level,
        id: this.$store.state.file.showFilesInfo.id,
        page: val,
        pageSize: this.$store.state.file.showFilesInfo.pageSize,
        showfileDetails: this.$store.state.file.showFilesInfo.showfileDetails,
        havePermission: this.$store.state.file.showFilesInfo.havePermission,
        fileName: this.$store.state.file.showFilesInfo.fileName,
        creator: this.$store.state.file.showFilesInfo.creator,
        belongType: this.$store.state.file.showFilesInfo.belongType,
        fileHaveChange:this.$store.state.file.showFilesInfo.fileHaveChange
      }
      this.$store.commit('file/SET_SHOW_FILES_INFO',newShowFilesInfo)
    },
    handleLook(index, row) {
      request({
        url: "File/FileBasicInfo",
        method: "get",
        params: {
          fileId: row.id
        }
      }).then(res => {
        let data = res.data
        if (data.errcode!=0) {
          alert(data.errmsg)
          return ;
        }
        data = data.res
        let fileInfo = [
          {label:"文件名：", value:data.name},
          {label:"位置：", value:data.position},
          {label:"创建人：", value:data.creator},
          {label:"创建时间：", value:data.createTime},
          {label:"类型：", value:data.type},
          {label:"备注：", value:data.remark},
          {label:"附件：", value:data.childFileNames}
        ]
        this.fileInfo = fileInfo
        this.fileId = row.id,
        this.dialogFormVisibleProp = true
      })
    },
    handleEdit(index, row) {
      request({
        url: "File/FileEditInfo",
        method: "get",
        params: {
          fileId: row.id
        }
      }).then(res => {
        let data = res.data
        if (data.errcode == 0) {
          this.editFileInfo = data.res
          console.log(this.editFileInfo)
          this.editFileId = row.id
          this.editDialogFormVisibleProp = true
        }
        else {
          alert(data.errmsg)
        }
      }).catch(err => {
        alert(err)
      })
    },
    handleDelete(index, row) {
      this.$confirm('此操作将永久删除该文件, 是否继续?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        request({
          url: "File/DeleteFile",
          method: "get",
          params: {
            fileId: row.id,
            userid: this.$store.state.auth.currentUser.userid
          }
        }).then(res => {
          let data = res.data
          if (data.errcode==0){
            this.$message({
              type: 'success',
              message: '删除成功!'
            });
            this.$store.commit("file/SET_FILE_CHANGE", !this.$store.state.file.showFilesInfo.fileHaveChange)
          }
          else alert(data.errmsg)
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
    handleBorrow(index, row) {
      this.borrowFile = {id: row.id, name: row.name}
      this.borrowUser = {
        id: this.$store.state.auth.currentUser.userid,
        name: this.$store.state.auth.currentUser.username,
      }
      this.showBorrowFileDialog = true
    },
    handleSelectionChange(selectedRows) {
      this.selectedFilesIds = selectedRows.map(val => val.id)
    },
    handleSelectionDelete() {
      this.$confirm('此操作将永久删除该文件, 是否继续?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        request({
          url: "File/DeleteSelectionFiles",
          method: "post",
          data: {
            fileIds: this.selectedFilesIds,
            userid: this.$store.state.auth.currentUser.userid
          }
        }).then(res => {
          let data = res.data
          if (data.errcode==0){
            this.$message({
              type: 'success',
              message: '删除成功!'
            });
            this.$store.commit("file/SET_FILE_CHANGE", !this.$store.state.file.showFilesInfo.fileHaveChange)
          }
          else alert(data.errmsg)
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
  }
};
</script>

<style lang="scss">
.box-card {
  width: 100%;
}

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
</style>