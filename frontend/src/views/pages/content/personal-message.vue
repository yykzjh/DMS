<template>
  <div>
    <PageHeader :title="title" :items="items" />
    <el-card class="box-card personal-message-card">
      <el-tabs v-model="activeName" @tab-click="handleClick">
        <el-tab-pane :label="labelsData[0].name + '(' + labelsData[0].count + ')'" name="first">
					<MessageTable
            :page.sync="table1.page"
            :pageSize.sync="table1.pageSize"
            :totalSize="table1.totalSize"
            :data="table1.data"
            :columns="table1.columns"
            :type="2"
            :loading.sync="table1.loading"
            @refresh-data="getAllBorrowRecord"
          ></MessageTable>
				</el-tab-pane>
        <el-tab-pane :label="labelsData[1].name + '(' + labelsData[1].count + ')'" name="second">
					<MessageTable
            :page.sync="table2.page"
            :pageSize.sync="table2.pageSize"
            :totalSize="table2.totalSize"
            :data="table2.data"
            :columns="table2.columns"
            :type="1"
            :loading.sync="table2.loading"
            @refresh-data="getAllBorrowRecord"
          ></MessageTable>
				</el-tab-pane>
        <el-tab-pane :label="labelsData[2].name + '(' + labelsData[2].count + ')'" name="third">
					<MessageTable
            :page.sync="table3.page"
            :pageSize.sync="table3.pageSize"
            :totalSize="table3.totalSize"
            :data="table3.data"
            :columns="table3.columns"
            :type="3"
            :loading.sync="table3.loading"
            @refresh-data="getAllBorrowRecord"
          ></MessageTable>
				</el-tab-pane>
        <el-tab-pane :label="labelsData[3].name + '(' + labelsData[3].count + ')'" name="fourth">
					<MessageTable
            :page.sync="table4.page"
            :pageSize.sync="table4.pageSize"
            :totalSize="table4.totalSize"
            :data="table4.data"
            :columns="table4.columns"
            :type="1"
            :loading.sync="table4.loading"
            @refresh-data="getAllBorrowRecord"
          ></MessageTable>
				</el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script>
import { request } from "@/network/request";
import PageHeader from "@/components/page-header";
import MessageTable from "@/components/message-table";

export default {
  components: {
    PageHeader,
    MessageTable,
  },
  data() {
    return {
      title: "Personal Message",
      items: [
        {
          text: "DMS",
        },
        {
          text: "工作台",
        },
        {
          text: "个人消息",
          active: true,
        },
      ],

      activeName: "",
      labelsData: [
        {
          name: "待处理",
          count: "",
        },
        {
          name: "已处理",
          count: "",
        },
        {
          name: "已发起",
          count: "",
        },
        {
          name: "我收到的",
          count: "",
        },
      ],

      table1: {
        loading:false,
        page: 1,
        pageSize: 5,
        totalSize: 0,
        data: [],
        columns:[
          {prop:"id", type:"selection", minWidth:60, fixed:"left", resizable:false},
          {label:"文件名", prop:"fileName", minWidth:150, resizable:true},
          {label:"借阅时间段", prop:"btime", minWidth:400, resizable:true},
          {label:"发起时间", prop:"stime", minWidth:200, resizable:true, sortable:true},
          {label:"借阅事由", prop:"reason", minWidth:200, resizable:true},
          {label:"审批时间", prop:"ptime", minWidth:200, resizable:true, sortable:true},
          {label:"审批人", prop:"approverName", minWidth:120, resizable:true},
        ]
      },
      table2: {
        loading:false,
        page: 1,
        pageSize: 5,
        totalSize: 0,
        data: [],
        columns:[
          {prop:"id", type:"selection", minWidth:60, fixed:"left", resizable:false},
          {label:"文件名", prop:"fileName", minWidth:150, resizable:true},
          {label:"借阅时间段", prop:"btime", minWidth:400, resizable:true},
          {label:"发起时间", prop:"stime", minWidth:200, resizable:true, sortable:true},
          {label:"借阅事由", prop:"reason", minWidth:200, resizable:true},
          {label:"审批时间", prop:"ptime", minWidth:200, resizable:true, sortable:true},
          {label:"审批人", prop:"approverName", minWidth:120, resizable:true},
        ]
      },
      table3: {
        loading:false,
        page: 1,
        pageSize: 5,
        totalSize: 0,
        data: [],
        columns:[
          {prop:"id", type:"selection", minWidth:60, fixed:"left", resizable:false},
          {label:"文件名", prop:"fileName", minWidth:150, resizable:true},
          {label:"借阅时间段", prop:"btime", minWidth:400, resizable:true},
          {label:"发起时间", prop:"stime", minWidth:200, resizable:true, sortable:true},
          {label:"借阅事由", prop:"reason", minWidth:200, resizable:true},
        ]
      },
      table4: {
        loading:false,
        page: 1,
        pageSize: 5,
        totalSize: 0,
        data: [],
        columns:[
          {prop:"id", type:"selection", minWidth:60, fixed:"left", resizable:false},
          {label:"文件名", prop:"fileName", minWidth:150, resizable:true},
          {label:"借阅时间段", prop:"btime", minWidth:400, resizable:true},
          {label:"发起时间", prop:"stime", minWidth:200, resizable:true, sortable:true},
          {label:"借阅事由", prop:"reason", minWidth:200, resizable:true},
          {label:"审批时间", prop:"ptime", minWidth:200, resizable:true, sortable:true},
          {label:"审批人", prop:"approverName", minWidth:120, resizable:true},
          {label:"审批意见", prop:"opinion", minWidth:250, resizable:true},
        ]
      },
    };
  },
  methods: {
    getBorrowRecord(statusList, tableNum) {
      let page = 1
      let pageSize = 5
      if (tableNum == 1) {
        page = this.table1.page
        pageSize = this.table1.pageSize
      }
      else if(tableNum == 2) {
        page = this.table2.page
        pageSize = this.table2.pageSize
      }
      else if(tableNum == 3) {
        page = this.table3.page
        pageSize = this.table3.pageSize
      }
      else if(tableNum == 4) {
        page = this.table4.page
        pageSize = this.table4.pageSize
      }
      request({
        url: "File/MyBorrowRecord",
        method: "post",
        data: {
          userid: this.$store.state.auth.currentUser.userid,
          statusList: statusList,
          page: page,
          pageSize: pageSize
        }
      }).then(res => {
        let data = res.data
        if (data.errcode == 0) {
          if (tableNum == 1) {
            this.table1.totalSize = data.totalSize
            this.table1.data = data.res
            this.labelsData[0].count = data.totalSize
            this.table1.loading = false
          }
          else if(tableNum == 2) {
            this.table2.totalSize = data.totalSize
            this.table2.data = data.res
            this.labelsData[1].count = data.totalSize
            this.table2.loading = false
          }
          else if(tableNum == 3) {
            this.table3.totalSize = data.totalSize
            this.table3.data = data.res
            this.labelsData[2].count = data.totalSize
            this.table3.loading = false
          }
          else if(tableNum == 4) {
            this.table4.totalSize = data.totalSize
            this.table4.data = data.res
            this.labelsData[3].count = data.totalSize
            this.table4.loading = false
          }
        }
        else{
          alert(data.errmsg)
        }
      }).catch(err => {
        alert(err)
      })
    },
    getAllBorrowRecord() {
      this.getBorrowRecord([3], 1)
      this.getBorrowRecord([4], 2)
      this.getBorrowRecord([0], 3)
      this.getBorrowRecord([1,2,3,5], 4)
    },
    handleClick(tag) {
      if (tag.name == "first") {
        this.getBorrowRecord([3], 1)
      }
      else if (tag.name == "second") {
        this.getBorrowRecord([4], 2)
      }
      else if (tag.name == "third") {
        this.getBorrowRecord([0], 3)
      }
      else if (tag.name == "fourth") {
        this.getBorrowRecord([1,2,3,5], 4)
      }
    }
  },
  mounted:function() {
    this.getAllBorrowRecord()
  }
};
</script>

<style lang="scss">

.personal-message-card {
	min-height: 600px;
}

.el-tabs__item {
	width: 220px;
	text-align: center;
	padding:0 50px;
}

</style>