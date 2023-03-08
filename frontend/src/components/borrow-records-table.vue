<template>
  <div class="borrow-records-table">
    <el-table
      :data="data"
      :max-height="450"
      :stripe="true"
      :border="true"
      :show-header="true"
      :highlight-current-row="true"
      :row-key="'id'"
      :empty-text="'暂无数据'"
      :select-on-indeterminate="true"
      style="width:100%;"
      v-loading="loading"
      tooltip-effect="light"
      @selection-change="handleSelectionChange"
      :row-style="({row, rowIndex}) => {if (type==2&&row.urge) return {color: 'red'}}"
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
        :show-overflow-tooltip="column.prop=='remark'||column.prop=='reason'||column.prop=='opinion'">
      </el-table-column>
      <el-table-column
        :min-width="120"
        :fixed="'right'"
        :resizable="true"
        align="center"
        header-align="center"
        label="状态">
        <template slot-scope="scope"> 
          <i class="ri-focus-fill" :style="{color:statusColorList[scope.row.status]}"></i>
          {{statusList[scope.row.status]}}
        </template>
      </el-table-column>
      <el-table-column
        :min-width="210"
        :fixed="'right'"
        :resizable="true"
        align="center"
        header-align="center"
        label="操作">
        <template slot-scope="scope">
          <el-button
            size="mini"
            type="info"
            @click.stop="handleLook(scope.$index, scope.row)">查看</el-button>
          <el-button
            v-if="type==1&&(scope.row.status==1||scope.row.status==3)"
            size="mini"
            type="primary"
            @click.stop="handleReturn(scope.$index, scope.row)">归还</el-button>
          <el-button
            v-if="type==1&&scope.row.urge==1"
            size="mini"
            type="warning"
            @click.stop="handleUrge(scope.$index, scope.row)">催办</el-button>
          <span v-if="type==1&&scope.row.urge==2">已催办</span>
          <span v-if="type==1&&scope.row.urge==3">等待审批</span>
          <el-button
            v-if="scope.row.status==2||scope.row.status==5"
            size="mini"
            type="danger"
            @click.stop="handleDelete(scope.$index, scope.row)">删除</el-button>
          <el-button
            v-if="type==2&&scope.row.status==0"
            size="mini"
            type="primary"
            @click.stop="handleAgree(scope.$index, scope.row)">同意</el-button>
          <el-button
            v-if="type==2&&scope.row.status==0"
            size="mini"
            type="danger"
            @click.stop="handleRefuse(scope.$index, scope.row)">拒绝</el-button>
          <el-button
            v-if="type==2&&scope.row.status==4"
            size="mini"
            type="primary"
            @click.stop="handleConfirm(scope.$index, scope.row)">确认归还</el-button>
        </template>
      </el-table-column>
    </el-table>
    <!-- 分页栏 -->
    <div class="ops">
      <el-button
        v-if="type==2"
        type="success"
        icon="el-icon-check"
        @click.stop="handleSelectionAgree"
        class="button-float-left">
        通过选中记录
      </el-button>
      <el-button
        v-if="type==2"
        type="danger" 
        icon="el-icon-close" 
        @click.stop="handleSelectionRefuse"
        class="button-float-left">
        拒绝选中记录
      </el-button>
      <el-button
        v-if="type==2"
        type="primary" 
        icon="el-icon-finished" 
        @click.stop="handleSelectionConfirm"
        class="button-float-left">
        确认归还选中记录
      </el-button>
      <el-button
        v-if="type==2"
        type="danger" 
        icon="el-icon-delete" 
        @click.stop="handleSelectionDelete"
        class="button-float-left">
        删除选中记录
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
  </div>
</template>

<script>
import { request } from "@/network/request";

export default {
  components: {},
  name: "BorrowRecordsTable",
  props: {
    page: Number,
    pageSize: Number,
    totalSize: Number,
    data: Array,
    columns: Array, //列的各个属性,可设置：type,index,label,prop,minWidth,fixed,sortable,resizable,filters
    type: Number,
    loading: Boolean,
  },
  data() {
    return {
      statusList: ["待通过", "已通过", "已拒绝", "已超时", "待归还", "已归还"],
      statusColorList: ["blue", "green", "orange", "red", "grey", "black"],
      selectedRecords: [],
    }
  },
  watch: {
    
  },
  methods:{
    handleSizeChange(val) {
      this.$emit("update:pageSize", val)
      this.$emit("update:loading", true)
      this.$emit("refresh-data")
    },
    handlePageChange(val) {
      this.$emit("update:page", val)
      this.$emit("update:loading", true)
      this.$emit("refresh-data")
    },
    handleLook(index, row) {

    },
    handleReturn(index, row) {
      request({
        url: "File/ReturnFile",
        method: "get",
        params: {
          borrowRecordId: row.id
        }
      }).then(res => {
        let data = res.data
        if (data.errcode == 0) {
          alert("归还成功！请等待审批人确认")
          this.$emit("update:loading", true)
          this.$emit("refresh-data")
        }else{
          alert(data.errmsg)
        }
      }).catch(err => {
        alert(err)
      })
    },
    handleUrge(index, row) {
      request({
        url: "File/UrgeFile",
        method: "get",
        params: {
          borrowRecordId: row.id
        }
      }).then(res => {
        let data = res.data
        if (data.errcode == 0) {
          alert("已催办，请等待审批！")
          this.$emit("update:loading", true)
          this.$emit("refresh-data")
        }else{
          alert(data.errmsg)
        }
      }).catch(err => {
        alert(err)
      })
    },
    handleDelete(index, row) {
      request({
        url: "File/DeleteBorrowRecord",
        method: "get",
        params: {
          borrowRecordId: row.id,
          type: this.type
        }
      }).then(res => {
        let data = res.data
        if (data.errcode == 0) {
          alert("删除该借阅记录成功！")
          this.$emit("update:loading", true)
          this.$emit("refresh-data")
        }else{
          alert(data.errmsg)
        }
      }).catch(err => {
        alert(err)
      })
    },
    handleAgree(index, row) {
      this.$prompt('请输入审批意见', '通过申请', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
      }).then(({ opinion }) => {
        request({
          url: "File/AgreeFile",
          method: "get",
          params: {
            approverId: this.$store.state.auth.currentUser.userid,
            borrowRecordId: row.id,
            approveOpinion: opinion
          }
        }).then(res => {
          let data = res.data
          if (data.errcode == 0) {
            alert("同意借阅！")
            this.$emit("update:loading", true)
            this.$emit("refresh-data")
          }else{
            alert(data.errmsg)
          }
        }).catch(err => {
          alert(err)
        })
      }).catch(() => {

      });
    },
    handleRefuse(index, row) {
      this.$prompt('请输入审批意见', '拒绝申请', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
      }).then(({ opinion }) => {
        request({
          url: "File/RefuseFile",
          method: "get",
          params: {
            approverId: this.$store.state.auth.currentUser.userid,
            borrowRecordId: row.id,
            approveOpinion: opinion
          }
        }).then(res => {
          let data = res.data
          if (data.errcode == 0) {
            alert("拒绝借阅！")
            this.$emit("update:loading", true)
            this.$emit("refresh-data")
          }else{
            alert(data.errmsg)
          }
        }).catch(err => {
          alert(err)
        })
      }).catch(() => {
              
      });
    },
    handleConfirm(index, row) {
      request({
        url: "File/ConfirmFile",
        method: "get",
        params: {
          borrowRecordId: row.id
        }
      }).then(res => {
        let data = res.data
        if (data.errcode == 0) {
          alert("确认归还！")
          this.$emit("update:loading", true)
          this.$emit("refresh-data")
        }else{
          alert(data.errmsg)
        }
      }).catch(err => {
        alert(err)
      })
    },
    handleSelectionChange(selectedRows) {
      this.selectedRecords = selectedRows
    },
    handleSelectionAgree() {
      if (this.selectedRecords.length == 0) {
        alert("请至少选中一项记录！")
        return ;
      }
      this.$confirm('此操作将批量通过选中的申请, 是否继续?', '批量通过申请', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        this.$prompt('请输入审批意见', '批量通过申请', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
        }).then(({ opinion }) => {
          let allMeetCondition = this.selectedRecords.every(val => {
            return val.status == 0
          })
          alert("success")
          if (allMeetCondition == true) {
            
            request({
              url: "File/AgreeSelectionRecords",
              method: "post",
              data: {
                borrowRecordIds: this.selectedRecords.map(val => val.id),
                approverId: this.$store.state.auth.currentUser.userid,
                approveOpinion: opinion
              }
            }).then(res => {
              let data = res.data
              if (data.errcode==0){
                this.$message({
                  type: 'success',
                  message: '批量通过申请成功!'
                }); 
                this.$emit("update:loading", true)
                this.$emit("refresh-data")
              }
              else alert(data.errmsg)
            }).catch(err => {
              alert(err)
            })
          }else {
            alert("请确保选中的记录状态都为待通过状态！")
          }
        }).catch(() => {

        });
      }).catch(() => {
        this.$message({
          type: 'info',
          message: '已取消批量通过申请'
        });          
      });
    },
    handleSelectionRefuse() {
      if (this.selectedRecords.length == 0) {
        alert("请至少选中一项记录！")
        return ;
      }
       this.$confirm('此操作将批量拒绝选中的申请, 是否继续?', '批量拒绝申请', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        this.$prompt('请输入审批意见', '批量拒绝申请', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
        }).then(({ opinion }) => {
          let allMeetCondition = this.selectedRecords.every(val => {
            return val.status == 0
          })
          if (allMeetCondition == true) {
            request({
              url: "File/RefuseSelectionRecords",
              method: "post",
              data: {
                borrowRecordIds: this.selectedRecords.map(val => val.id),
                approverId: this.$store.state.auth.currentUser.userid,
                approveOpinion: opinion
              }
            }).then(res => {
              let data = res.data
              if (data.errcode==0){
                this.$message({
                  type: 'success',
                  message: '批量拒绝申请成功!'
                }); 
                this.$emit("update:loading", true)
                this.$emit("refresh-data")
              }
              else alert(data.errmsg)
            }).catch(err => {
              alert(err)
            })
          }else {
            alert("请确保选中的记录状态都为待通过状态！")
          }
        }).catch(() => {

        });
      }).catch(() => {
        this.$message({
          type: 'info',
          message: '已取消批量拒绝申请'
        });          
      });
    },
    handleSelectionConfirm() {
      if (this.selectedRecords.length == 0) {
        alert("请至少选中一项记录！")
        return ;
      }
       this.$confirm('此操作将批量确认归还文件, 是否继续?', '批量确认归还文件', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        let allMeetCondition = this.selectedRecords.every(val => {
          return val.status == 4
        })
        if (allMeetCondition == true) {
          request({
            url: "File/ConfirmSelectionRecords",
            method: "post",
            data: {
              borrowRecordIds: this.selectedRecords.map(val => val.id)
            }
          }).then(res => {
            let data = res.data
            if (data.errcode==0){
              this.$message({
                type: 'success',
                message: '批量确认归还文件成功!'
              }); 
              this.$emit("update:loading", true)
              this.$emit("refresh-data")
            }
            else alert(data.errmsg)
          }).catch(err => {
            alert(err)
          })
        }else {
          alert("请确保选中的记录状态都为待归还状态！")
        }
      }).catch(() => {
        this.$message({
          type: 'info',
          message: '已取消批量确认归还文件'
        });          
      });
    },
    handleSelectionDelete() {
      if (this.selectedRecords.length == 0) {
        alert("请至少选中一项记录！")
        return ;
      }
      this.$confirm('此操作将批量删除借阅记录, 是否继续?', '批量删除文件记录', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        let allMeetCondition = this.selectedRecords.every(val => {
          return val.status == 2 || val.status == 5
        })
        if (allMeetCondition == true) {
          request({
            url: "File/DeleteSelectionRecords",
            method: "post",
            data: {
              borrowRecordIds: this.selectedRecords.map(val => val.id)
            }
          }).then(res => {
            let data = res.data
            if (data.errcode==0){
              this.$message({
                type: 'success',
                message: '批量删除借阅记录成功!'
              }); 
              this.$emit("update:loading", true)
              this.$emit("refresh-data")
            }
            else alert(data.errmsg)
          }).catch(err => {
            alert(err)
          })
        }else {
          alert("请确保选中的记录状态都为已拒绝或者已归还状态！")
        }
      }).catch(() => {
        this.$message({
          type: 'info',
          message: '已取消批量删除文件记录'
        });          
      });
    }
  }
}
</script>

<style lang="scss">

.borrow-records-table {

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
}

</style>