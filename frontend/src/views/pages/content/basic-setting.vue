<template>
  <div class="basic-setting-page">
      <PageHeader :title="title" :items="items" />
      <el-card class="user-info-card">
        <el-form :label-position="'right'" size="small" label-width="120px" :model="userInfoForm">
          <el-form-item class="user-info-form-item" label="姓名：" v-if="$store.state.auth.currentUser.permissions.indexOf(61)!=-1">
            <el-input v-model="userInfoForm.name"></el-input>
          </el-form-item>
          <el-form-item class="user-info-form-item" label="姓名：" v-else>
            <el-input :disabled="true" v-model="userInfoForm.name"></el-input>
          </el-form-item>
          <el-form-item class="user-info-form-item" label="工号：">
            <el-input :disabled="true" v-model="userInfoForm.userid"></el-input>
          </el-form-item>
          <el-form-item class="user-info-form-item" label="部门：">
            <el-input :disabled="true" v-model="userInfoForm.dept"></el-input>
          </el-form-item>
          <el-form-item class="user-info-form-item" label="角色：">
            <el-input :disabled="true" v-model="userInfoForm.role"></el-input>
          </el-form-item>
          <el-form-item class="user-info-form-item" label="可借阅次数：">
            <el-input :disabled="true" v-model="userInfoForm.borrowCount"></el-input>
          </el-form-item>
          <el-form-item class="user-info-form-item" label="联系电话：">
            <el-input :disabled="true" v-model="userInfoForm.phone"></el-input>
          </el-form-item>
          <el-form-item class="user-info-form-item" label="邮箱：">
            <el-input :disabled="true" v-model="userInfoForm.email"></el-input>
          </el-form-item>
          <el-form-item class="user-info-form-item" label="微信号：">
            <el-input :disabled="true" v-model="userInfoForm.wechat"></el-input>
          </el-form-item>
          <el-form-item class="user-info-form-item" v-if="$store.state.auth.currentUser.permissions.indexOf(61)!=-1">
            <el-button type="primary" @click.stop="handleEditUserBasicInfo">更新信息</el-button>
            <el-button @click.stop="resetUserBasicInfo">重置</el-button>
          </el-form-item>
        </el-form>
      </el-card>
      <el-card class="user-avatar-card">
        <div class="old-avatar-div">
          <span style="vertical-align:top;">头像：</span>
          <el-image
            class="old-avatar"
            :src="myAvatar"
            :fit="'fit'">
          </el-image>
        </div>
        <div class="upload-avatar-div" v-if="$store.state.auth.currentUser.permissions.indexOf(61)!=-1">
          <div>
            <el-button type="primary" @click.stop="clickUploadButton">
              <i class="el-icon-upload" style="margin-right:5px; font-size:1.1rem;"></i>
              更换头像
              <input ref="avatarInput" type="file" name="avatarInput" style="display:none;" @change="handleUploadAvatar">
            </el-button>
          </div>
          <div>
            <el-image
              class="new-avatar"
              :src="croppedAvatar"
              :fit="'fit'">
              <div :slot="'error'" class="el-image__error">未选择新头像</div>
            </el-image>
          </div>
          <div>
            <el-button type="primary" @click.stop="submitAvatar">
              <i class="el-icon-upload2" style="margin-right:5px; font-size:1.1rem;"></i>
              上传头像</el-button>
          </div>
        </div>
      </el-card>


      <el-dialog
        title="裁剪头像"
        :visible.sync="dialogVisible"
        :close-on-click-modal="false"
        :destroy-on-close="true"
        :show-close="false">
        <vueCropper
          style="width:90%;height:300px"
          ref="cropper"
          :img="uploadAvatar"
          :outputSize="1"
          :info="true"
          :canScale="true"
          :autoCrop="true"
          :autoCropWidth="256"
          :autoCropHeight="256"
          :fixedBox="false"
          :canMove="true"
          :canMoveBox="true"
          :centerBox="true">
        </vueCropper>
        <div style="margin-top:20px;">
          <el-button type="primary " size="medium" round @click="handleCropAvatar">确定</el-button>
          <el-button size="medium" round @click.stop="closeCropDialog">取消</el-button>
        </div>
    </el-dialog>
  </div>
</template>

<script>
import { request } from "@/network/request";
import PageHeader from "@/components/page-header";

export default {
  components: {
    PageHeader
  },
  data() {
    return {
      title: "Basic Setting",
      items:[
        {
          text: "DMS"
        },
        {
          text: "个人中心"
        },
        {
          text: "基本设置",
          active: true
        }
      ],

      userInfoForm: {
        userid: "",
        name: "",
        dept: "",
        role: "",
        borrowCount: 0,
        phone: "",
        email: "",
        wechat: "",
      },
      resetName: "",

      myAvatar: "",
      dialogVisible: false,
      uploadAvatar: "",
      croppedAvatar: "",
    }
  },
  methods: {
    getUserBasicInfo() {
      request({
        url: "User/UserBasicInfo",
        method: "get",
        params: {
          userid: this.$store.state.auth.currentUser.userid
        }
      }).then(res => {
        let data = res.data
        if (data.errcode == 0) {
          this.userInfoForm = data.userInfoForm
          this.resetName = data.userInfoForm.name
        }else {
          alert(data.errmsg)
        }
      }).catch(err => {
        alert(err)
      })
    },
    handleEditUserBasicInfo() {
      request({
        url: "User/EditUserBasicInfo",
        method: "get",
        params: {
          userid: this.userInfoForm.userid,
          name: this.userInfoForm.name,
        }
      }).then(res => {
        let data = res.data
        if (data.errcode == 0){
          this.$message.success("信息修改成功！")
          this.getUserBasicInfo()
        }else {
          alert(data.errmsg)
        }
      }).catch(err => {
        alert(err)
      })
    },
    resetUserBasicInfo() {
      this.userInfoForm.name = this.resetName
    },
    getAvatar() {
      request({
        url: "User/Avatar",
        method: "get",
        params: {
          userid: this.$store.state.auth.currentUser.userid
        },
        responseType: "blob"
      }).then(res => {
        let data = res.data
        const type = data.type || null
        if (type.includes('application/json')) {
          let reader = new FileReader()
            reader.onload = e => {
                if (e.target.readyState === 2) {
                  let ans = {}
                  ans = JSON.parse(e.target.result)
                  alert(ans.errmsg)
                }
          }
          reader.readAsText(response)
          return ;
        }
        else {
          this.myAvatar = URL.createObjectURL(data)
        }
      }).catch(err => {
        alert(err)
      })
    },
    clickUploadButton() {
      let avatarInput = this.$refs.avatarInput
      avatarInput.value = ""
      avatarInput.click();
    },
    handleUploadAvatar(e) {
      let file = e.target.files[0]
      if (file == null) return ;
      let imageType = new RegExp("^image\/");
      if (!imageType.test(file.type)) {
          alert("请上传图片类型的文件！")
          return ;
      }
      let reader = new FileReader();
      reader.readAsDataURL(file); //重要 以dataURL形式读取文件
      reader.onload = e => {
        let data = e.target.result;
        this.uploadAvatar = data;
        this.dialogVisible = true
      }
    },
    closeCropDialog() {
      this.uploadAvatar = ""
      this.dialogVisible = false
    },
    handleCropAvatar() {
      this.dialogVisible = false
      this.$refs.cropper.startCrop()
      this.$refs.cropper.getCropData((data) => {
        this.croppedAvatar = data
      })
    },
    submitAvatar() {
      request({
        url: "User/UpdateAvatar",
        method: "post",
        data: {
          avatar: this.croppedAvatar,
          userid: this.userInfoForm.userid
        }
      }).then(res => {
        const data = res.data
        if (data.errcode == 0) {
          alert("头像修改成功！")
          this.getAvatar()
          this.$store.commit("auth/SET_AVATAR_CHANGE")
        }else {
          alert(data.errmsg)
        }
      }).catch(err => {
        alert(err)
      })
    }
  },
  mounted:function() {
    this.getUserBasicInfo()
    this.getAvatar()
  }
}
</script>

<style lang="scss" scoped>

.basic-setting-page {

  .user-info-card {
    display: inline-block;
    min-height: 600px;
    width: 50%;
    padding-left: 2%;
    padding-top: 20px;
  }

  .user-info-form-item {
    width: 80%;
  }

  .user-avatar-card {
    display: inline-block;
    min-height: 600px;
    width: 45%;
    margin-left: 2%;
  }

  .old-avatar-div {
    width: 100%;
    margin-left: 25%;
    margin-top: 50px;
  }

  .old-avatar {
    margin-left: 38px;
    width:150px;
    height:150px;
    border-radius:50%;
  }

  .upload-avatar-div {
    width: 100%;
    height: 300px;
    margin-top: 20px;
    display: flex;
    flex-direction: column;
    justify-content: space-around;
    align-items: center;
  }

  .new-avatar {
    width:150px;
    height:150px;
    border-radius:50%;
  }

  .el-image__error {
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 14px;
    color: #C0C4CC;
    vertical-align: middle;
  }
}



</style>