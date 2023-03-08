<template>
  <div class="file-audit-page">
      <PageHeader :title="title" :items="items" />
      <el-card class="file-audit-card">
      <div class="query-header">
        <label for="operation-type" class="query-item-label">操作类型：</label>
        <el-select id="operation-type" v-model="selectedOperation" clearable multiple placeholder="请选择">
          <el-option
            v-for="operationType in operationTypes"
            :key="operationType"
            :label="operationType"
            :value="operationType">
          </el-option>
        </el-select>
        <label for="lower-datetime" class="query-item-label">最早操作时间：</label>
        <el-date-picker
          id="lower-datetime"
          value-format="yyyy-MM-dd HH:mm:ss"
          v-model="lowerDateTime"
          type="datetime"
          placeholder="选择日期时间">
        </el-date-picker>
        <label for="upper-datetime" class="query-item-label">最晚操作时间：</label>
        <el-date-picker
          id="upper-datetime"
          value-format="yyyy-MM-dd HH:mm:ss"
          v-model="upperDateTime"
          type="datetime"
          placeholder="选择日期时间">
        </el-date-picker>
        <label for="userName" class="query-item-label">操作人：</label>
        <el-input
          id="userName"
          clearable
          class="query-condition-item"
          placeholder="操作人姓名"
          v-model="userName">
        </el-input>
        <br />
        <label for="fileName" class="query-item-label">文件名：</label>
        <el-input
          id="fileName"
          clearable
          class="query-condition-item"
          placeholder="文件名关键词"
          v-model="fileName">
        </el-input>
        <el-button
          icon="el-icon-search"
          class="search-button"
          type="primary"
          @click="handleConditionSearch"></el-button>
      </div>
      <AuditTable
        :page.sync="page"
        :pageSize.sync="pageSize"
        :totalSize="totalSize"
        :data="tableData"
        :columns="columns"
        :type="2"
        :loading.sync="loading"
        @refresh-data="getFileAudit"
        @export-data="handleExportFileAudit"
      ></AuditTable>
    </el-card>
  </div>
</template>

<script>
import { request } from "@/network/request";
import PageHeader from "@/components/page-header";
import AuditTable from "@/components/audit-table";

export default {
  components: {
    PageHeader,
    AuditTable,
  },
  data() {
    return {
      title: "File Audit",
      items:[
        {
          text: "DMS"
        },
        {
          text: "台账"
        },
        {
          text: "文件台账",
          active: true
        }
      ],

      operationTypes: ["新增", "修改", "删除"],
      selectedOperation: [],
      lowerDateTime: null,
      upperDateTime: null,
      userName: "",
      fileName: "",

      page: 1,
      pageSize: 5,
      totalSize: 0,
      tableData: [],
      columns: [
        {label:"操作人", prop:"userName", minWidth:120, resizable:true},
        {label:"操作类型", prop:"operation", minWidth:120, resizable:true},
        {label:"当前文件路径", prop:"filePath", minWidth:500, resizable:true},
        {label:"操作时间", prop:"datetime", minWidth:200, resizable:true, sortable:true},
        {label:"操作对象", prop:"target", minWidth:500, resizable:true},
        {label:"名称变化", prop:"nameVary", minWidth:500, resizable:true},
        {label:"文件版本变化", prop:"versionVary", minWidth:500, resizable:true},
        {label:"位置变化", prop:"positionVary", minWidth:500, resizable:true},
        {label:"备注变化", prop:"remarkVary", minWidth:500, resizable:true},
      ],
      loading:false,
    }
  },
  methods: {
    getFileAudit() {
      request({
        url: "File/FileAudits",
        method: "post",
        data: {
          operations: this.selectedOperation,
          lowerDateTime: this.lowerDateTime,
          upperDateTime: this.upperDateTime,
          userName: this.userName,
          fileName: this.fileName,
          page: this.page,
          pageSize: this.pageSize,
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
      this.getFileAudit()
    },
    handleExportFileAudit() {
      request({
        url: "File/ExportFileAudits",
        method: "post",
        data: {
          operations: this.selectedOperation,
          lowerDateTime: this.lowerDateTime,
          upperDateTime: this.upperDateTime,
          userName: this.userName,
          fileName: this.fileName,
        },
        responseType: "blob"
      }).then(res => {
        let blob = new Blob([res.data], {
          type: 'text/csv'
        })
        let link = document.createElement('a')
        link.href = window.URL.createObjectURL(blob)
        link.download = "fileAudit.csv"
        link.click()
        //释放内存
        window.URL.revokeObjectURL(link.href)
      }).catch(err => {
        alert(err)
      })
    },
  },
  mounted:function() {
    this.getFileAudit()
  },
}
</script>

<style lang="scss">
.file-audit-page {
  .file-audit-card {
    min-height: 600px;
  }

  .query-header {
    width: 100%;
    margin-bottom: 20px;
  }

  .query-item-label {
    margin-left: 20px;
    min-width: 80px;
    text-align: right;
  }

  .query-condition-item {
    width: 200px;
    font-size: 0.8rem;
  }

  .search-button {
    position:relative;
    top:1px;
  }
}

</style>