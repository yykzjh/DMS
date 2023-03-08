<template>
  <div class="files-management-page">
    <PageHeader :title="title" :items="items" />
    <div class="content-body">
      <el-card class="box-card left-filing-tree">
        <el-input placeholder="请输入搜索条件" v-model="searchText">
          <el-button slot="append" icon="el-icon-search"></el-button>
        </el-input>
        <FilingTree></FilingTree>
      </el-card>
      <el-card class="box-card right-files-table" v-if="showTable">
        <div class="query-condition-header">
          <QueryConditionHearder
            v-if="showFilesTableHeader"
            :fileNameProp="fileNameProp"
            :creatorProp="creatorProp"
            :havePermission="havePermission">
          </QueryConditionHearder>
        </div>
        <div class="files-table">
          <PaTable
            :data="onePageData"
            :tableMaxHeight="400"
            :havePermission="havePermission"
            :showfileDetails="showfileDetails"
            :columns="columns"
            :loading="loading"
            :page.sync="page"
            :pageSize.sync="pageSize"
            :totalSize="totalSize"
          ></PaTable>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script>
import { mapState} from 'vuex';
import {request} from '@/network/request';
import PageHeader from "@/components/page-header";
import FilingTree from "@/components/filing-tree";
import PaTable from "@/components/paginator-table";
import QueryConditionHearder from "@/components/query-condition-header"

export default {
  components: {
    PageHeader,
    FilingTree,
    PaTable,
    QueryConditionHearder,
  },
  data() {
    return {
      showFilesTableHeader: false,
      title: "Files Management",
      items: [{text: "DMS",},{text: "文件管理",active: true}],
      searchText:"",
      columns:[
        {prop:"id", type:"selection", minWidth:60, fixed:"left", resizable:false},
        {label:"文件名", prop:"name", minWidth:150, fixed:"left", resizable:true},
        {label:"文件类型", prop:"type", minWidth:100, resizable:false},
        {label:"位置", prop:"position", minWidth:300, resizable:true},
        {label:"创建人", prop:"creator", minWidth:100, resizable:false},
        {label:"创建时间", prop:"datetime", minWidth:170, resizable:false},
        {label:"备注", prop:"remark", minWidth:150, resizable:true},
      ],
      onePageData: [],
      loading:false,
      havePermission: false,
      showfileDetails: false,
      page: 1,
      pageSize: 5,
      totalSize: 0,
      fileNameProp: "",
      creatorProp: "",
      showTable: false,
    };
  },
  computed: {
    ...mapState('file', {
      showFilesInfo: (state) => state.showFilesInfo,
      openFolder: (state) => state.openFolder,
    })
  },
  methods:{
    getFilesData(newVal, oldval) {
      if(newVal.level==0 && newVal.id==0) return ;
      this.showFilesTableHeader = true
      // console.log(newVal)
      this.loading = true
      request({
        url: "File/FilesData",
        method: "post",
        data: {
          userid: this.$store.state.auth.currentUser.userid,
          level: newVal.level,
          id: newVal.id,
          page: newVal.page,
          pageSize: newVal.pageSize,
          fileName: newVal.fileName,
          creator: newVal.creator
        }
      }).then(res => {
        let data = res.data
        this.havePermission = newVal.havePermission
        this.showfileDetails = newVal.showfileDetails
        this.page = newVal.page
        this.pageSize = newVal.pageSize
        this.totalSize = data.totalSize
        this.fileNameProp = newVal.fileName
        this.creatorProp = newVal.creator
        this.onePageData = data.res
        this.loading = false
      }).catch(err => {
        alert(err)
      })
    }
  },
  watch: {
    showFilesInfo: {
      handler: "getFilesData",
      immediate: true,
      deep: true,
    },
    "openFolder"(newVal, oldVal) {
      this.showTable = newVal
    }
  }
};
</script>

<style lang="scss">

.files-management-page {

  .content-body {
    display: flex;
    justify-content:space-between;
  }

  .el-input {
    margin-bottom: 20px;
  }

  .el-input-group__append {
    padding:0 12px !important;
  }

  .el-icon-search {
    font-size: 1rem;
    font-weight: 500;
  }


  .left-filing-tree {
    display: inline-block;
    background-color: rgba(240, 240, 240, 0.5);
    height:615px;
    padding: 10px;
    width: 22%;

    .el-card__body {
      padding: 0;
      padding-left: 10px;
    }
  }

  .right-files-table {
    display: inline-block;
    background-color: rgba(240, 240, 240, 0.5);
    min-height: 615px;
    width: 77%;
    position: relative;

    .el-card__body {
      padding: 0;
      padding-left: 0px;
    }
  }
}

</style>