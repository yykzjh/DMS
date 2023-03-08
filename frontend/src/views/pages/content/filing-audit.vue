<template>
  <div>
      <PageHeader :title="title" :items="items" />
      <el-card class="filng-audit-card">
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
        <label for="structure-type" class="query-item-label">结构类型：</label>
        <el-select id="structure-type" v-model="selectedStructure" clearable multiple placeholder="请选择">
          <el-option
            v-for="structureType in structureTypes"
            :key="structureType.value"
            :label="structureType.label"
            :value="structureType.value">
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
        <br />
        <label for="userName" class="query-item-label">操作人：</label>
        <el-input
          id="userName"
          clearable
          class="query-condition-item"
          placeholder="操作人姓名"
          v-model="userName">
        </el-input>
        <label for="filingName" class="query-item-label">结构名称：</label>
        <el-input
          id="filingName"
          clearable
          class="query-condition-item"
          placeholder="结构名称关键词"
          v-model="filingName">
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
        :type="1"
        :loading.sync="loading"
        @refresh-data="getFilingAudit"
        @export-data="handleExportFilingAudit"
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
      title: "Filing Audit",
      items:[
        {
          text: "DMS"
        },
        {
          text: "台账"
        },
        {
          text: "文件柜台账",
          active: true
        }
      ],

      operationTypes: ["新增", "修改", "删除"],
      selectedOperation: [],
      structureTypes: [
        {label: "项目组", value: 1},
        {label: "文件柜", value: 2},
        {label: "文件柜格", value: 3},
        {label: "文件盒", value: 4} 
      ],
      selectedStructure: [],
      lowerDateTime: null,
      upperDateTime: null,
      userName: "",
      filingName: "",

      page: 1,
      pageSize: 5,
      totalSize: 0,
      tableData: [],
      columns: [
        {label:"操作人", prop:"userName", minWidth:120, resizable:true},
        {label:"操作类型", prop:"operation", minWidth:120, resizable:true},
        {label:"结构类型", prop:"structureType", minWidth:120, resizable:true},
        {label:"当前结构路径", prop:"filingPath", minWidth:500, resizable:true},
        {label:"操作时间", prop:"datetime", minWidth:200, resizable:true, sortable:true},
        {label:"操作对象", prop:"target", minWidth:500, resizable:true},
        {label:"名称变化", prop:"nameVary", minWidth:500, resizable:true},
        {label:"开放权限的用户变化", prop:"permitUsersVary", minWidth:500, resizable:true},
        {label:"位置变化", prop:"positionVary", minWidth:500, resizable:true},
        {label:"备注变化", prop:"remarkVary", minWidth:500, resizable:true},
      ],
      loading:false,
    }
  },
  methods: {
    getFilingAudit() {
      request({
        url: "File/FilingAudits",
        method: "post",
        data: {
          operations: this.selectedOperation,
          structures: this.selectedStructure,
          lowerDateTime: this.lowerDateTime,
          upperDateTime: this.upperDateTime,
          userName: this.userName,
          filingName: this.filingName,
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
      this.getFilingAudit()
    },
    handleExportFilingAudit() {
      request({
        url: "File/ExportFilingAudits",
        method: "post",
        data: {
          operations: this.selectedOperation,
          structures: this.selectedStructure,
          lowerDateTime: this.lowerDateTime,
          upperDateTime: this.upperDateTime,
          userName: this.userName,
          filingName: this.filingName,
        },
        responseType: "blob"
      }).then(res => {
        let blob = new Blob([res.data], {
          type: 'text/csv'
        })
        let link = document.createElement('a')
        link.href = window.URL.createObjectURL(blob)
        link.download = "filingAudit.csv"
        link.click()
        //释放内存
        window.URL.revokeObjectURL(link.href)
      }).catch(err => {
        alert(err)
      })
    },
  },
  mounted:function() {
    this.getFilingAudit()
  },
}
</script>

<style lang="scss" scoped>

.filng-audit-card {
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

</style>