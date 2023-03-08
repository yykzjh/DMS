<template>
  <div>
    <PageHeader :title="title" :items="items" />
    <el-card class="borrow-record-management-card">
      <div class="query-header">
        <label for="statusType" style="padding-left: 20px">状态：</label>
        <el-select id="statusType" v-model="selectedStatusTypes" clearable multiple placeholder="请选择">
          <el-option
            v-for="statusType in statusTypes"
            :key="statusType.value"
            :label="statusType.label"
            :value="statusType.value">
          </el-option>
        </el-select>
        <label for="userName" style="padding-left: 20px">借阅人：</label>
        <el-input
          id="userName"
          :clearable="true"
          class="query-condition-item"
          placeholder="借阅人姓名"
          v-model="userName">
        </el-input>
        <label for="fileName" style="padding-left: 20px">文件名：</label>
        <el-input
          id="fileName"
          :clearable="true"
          class="query-condition-item"
          placeholder="文件名关键字"
          v-model="fileName">
        </el-input>
        <el-button
          icon="el-icon-search"
          class="search-button"
          type="primary"
          @click="handleConditionSearch"></el-button>
      </div>
      <BorrowRecordsTable
        :page.sync="page"
        :pageSize.sync="pageSize"
        :totalSize="totalSize"
        :data="tableData"
        :columns="columns"
        :type="2"
        :loading.sync="loading"
        @refresh-data="getManageBorrowRecords"
      ></BorrowRecordsTable>
    </el-card>
  </div>
</template>

<script>
import { request } from "@/network/request";
import PageHeader from "@/components/page-header";
import BorrowRecordsTable from "@/components/borrow-records-table";

export default {
  components: {
    PageHeader,
    BorrowRecordsTable,
  },
  data() {
    return {
      title: "Borrow Record Management",
      items:[
        {
          text: "DMS"
        },
        {
          text: "工作台"
        },
        {
          text: "借阅管理",
          active: true
        }
      ],

      statusTypes: [
        {label:"待通过", value:0},
        {label:"已通过", value:1},
        {label:"已拒绝", value:2},
        {label:"已超时", value:3},
        {label:"待归还", value:4},
        {label:"已归还", value:5},
      ],
      selectedStatusTypes: [],
      userName: "",
      fileName: "",

      page: 1,
      pageSize: 5,
      totalSize: 0,
      tableData: [],
      columns: [
        {prop:"id", type:"selection", minWidth:60, fixed:"left", resizable:false},
        {label:"借阅人", prop:"userName", minWidth:120, resizable:true},
        {label:"文件名", prop:"fileName", minWidth:150, resizable:true},
        {label:"借阅时间段", prop:"btime", minWidth:400, resizable:true},
        {label:"发起时间", prop:"stime", minWidth:200, resizable:true, sortable:true},
        {label:"借阅事由", prop:"reason", minWidth:200, resizable:true},
        {label:"审批时间", prop:"ptime", minWidth:200, resizable:true, sortable:true},
        {label:"审批意见", prop:"opinion", minWidth:250, resizable:true},
      ],
      loading:false,
    }
  },
  methods: {
    getManageBorrowRecords() {
      let statusList = [0, 1, 2, 3, 4, 5]
      if (this.selectedStatusTypes.length > 0) {
        statusList = this.selectedStatusTypes
      }
      request({
        url: "File/ManageBorrowRecords",
        method: "post",
        data: {
          userid: this.$store.state.auth.currentUser.userid,
          statusList: statusList,
          userName: this.userName,
          fileName: this.fileName,
          page: this.page,
          pageSize: this.pageSize
        }
      }).then(res => {
        let data = res.data
        if (data.errcode == 0) {
          this.totalSize = data.totalSize
          this.tableData = data.res
          this.loading = false
        }
        else{
          alert(data.errmsg)
        }
      }).catch(err => {
        alert(err)
      })
    },
    handleConditionSearch() {
      this.loading = true
      this.getManageBorrowRecords()
    },
  },
  mounted:function() {
    this.getManageBorrowRecords()
  },
}
</script>

<style lang="scss" scoped>

.borrow-record-management-card {
  min-height: 600px;
}

.query-header {
  width: 100%;
  margin-bottom: 20px;
}

.query-condition-item {
  width: 200px;
  font-size: 0.8rem;
}

.search-button {
  position:relative;
  top:1px;
}

</style>