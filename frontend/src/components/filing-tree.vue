<template>
  <div class="tree">
    <span
      v-if="$store.state.auth.currentUser.permissions.indexOf(21)!=-1"
      @click.stop="handleAddProjectTeam"
      class="add-project-team-icon">
      <i class="ri-add-circle-fill"></i>
    </span>
    <NewFilingDialog
      :level="0"
      :id="0"
      :showAddDialog.sync="showAddDialog"
      @addSuccess="getProjectTeamsData"
    ></NewFilingDialog>

    <TreeNode v-for="projectTeam in projectTeams"
      :key="projectTeam.id"
      :id="projectTeam.id"
      :name="projectTeam.name"
      :type="projectTeam.type"
      :position="projectTeam.position"
      :remark="projectTeam.remark"
      :managers="projectTeam.managers"
      :level="level+1"
      :havePermission="currentPermission"
      :havePermitBorrow="currentPermission"
      :userid="userid"
      :permissionUsers="projectTeam.permission_users"
      :isOpenProp="openId==projectTeam.id"
      @open-file="handleOpenFile"
      @refresh-structure="handleRefreshStructure"
    >
    </TreeNode>
  </div>
</template>

<script>
import { mapState} from 'vuex';
import TreeNode from "./filing-tree-node";
import {request} from '@/network/request';
import {
  authMethods,
} from "@/state/helpers";
import NewFilingDialog from "./new-filing-dialog";

export default {
  components: { TreeNode, NewFilingDialog },
  data() {
    return {
      projectTeams: [
        {
          id:1,
          name:"test1"
        },
        {
          id:2,
          name: "test2"
        }
      ],
      level: 0,
      userid: "",
      currentPermission:false,
      currentPermitBorrow:false,
      openId: 0,
      showAddDialog: false,
    }
  },
  computed:{
    ...authMethods,
    ...mapState('file', {
    filingHaveChange: (state) => state.filingHaveChange,
  })
  },
  watch: {
    'filingHaveChange'(newval, oldval) {
      if (newval) this.getProjectTeamsData();
    }
  },
  methods: {
    getProjectTeamsData() {
      if (this.$store.state.auth.currentUser.permissions.indexOf(21)!=-1) {
        this.currentPermission = true
        this.currentPermitBorrow = true
      }
      this.userid = this.$store.state.auth.currentUser.userid
      request({
        url: "File/ChildFolders",
        method: "get",
        params: {
          level:0,
          position: 0
        }
      }).then(res => {
        let data = res.data
        this.projectTeams = data.res
      }).catch(err => {
        alert(err)
      })
    },
    handleOpenFile(folderId) {
      this.openId = folderId
    },
    handleAddProjectTeam() {
      this.showAddDialog = true
    },
    handleRefreshStructure() {
      this.getProjectTeamsData()
    }
  },
  mounted:function() {
    this.getProjectTeamsData()
  },
};
</script>

<style>

.tree {
  padding-left: 9px;
  overflow-x: hidden;
  overflow-y: auto;
  position: relative;
}

.tree:before {
  display: inline-block;
  content: "";
  position: absolute;
  top: 14px;
  bottom: 16px;
  left: 0;
  border: 1px dotted #67b2dd;
  border-width: 0 0 0 1px;
  z-index: 1;
}

.add-project-team-icon {
  font-size: 1.5rem;
  color:#67b2dd;
}

.add-project-team-icon:hover {
  cursor: pointer;
}



</style>