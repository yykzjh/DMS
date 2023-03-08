<template>
  <div>
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
        :show-overflow-tooltip="column.prop=='filingPath'||column.prop=='filePath'||column.prop=='target'
          ||column.prop=='nameVary'||column.prop=='permitUsersVary'||column.prop=='versionVary'
          ||column.prop=='positionVary'||column.prop=='remarkVary'">
      </el-table-column>
    </el-table>
    <!-- 分页栏 -->
    <div class="ops">
      <el-button
        v-if="$store.state.auth.currentUser.permissions.indexOf(51)!=-1"
        type="primary"
        circle
        icon="el-icon-download"
        @click.stop="handleExport"
        class="button-float-left">
        导出
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
  name: "AuditTable",
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
      
    }
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
    handleExport() {
      this.$emit("export-data")
    },
  }
}
</script>

<style scoped>

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