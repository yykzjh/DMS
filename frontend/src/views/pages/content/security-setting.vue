<template>
  <div class="security-setting-page">
      <PageHeader :title="title" :items="items" />
      <el-card class="security-setting-card">
        <div class="security-setting-item">
          <div class="security-setting-item-content">
            <span class="item-title">账户密码</span>
            <span class="item-value">当前密码强度：</span>
            <span style="color:lightgreen">{{passwordPower}}</span>
          </div>
          <span class="modify-item" @click.stop="handleModifyPassword" v-if="$store.state.auth.currentUser.permissions.indexOf(62)!=-1">修改</span>
          <el-divider :direction="'horizontal'" :content-position="'center'"></el-divider>
        </div>
        <div class="security-setting-item">
          <div class="security-setting-item-content">
            <span class="item-title">绑定手机</span>
            <span class="item-value">已绑定手机：</span>
            <span style="color:#C0C4CC;">{{phoneCover}}</span>
          </div>
          <span class="modify-item" @click.stop="handleModifyPhone" v-if="$store.state.auth.currentUser.permissions.indexOf(62)!=-1">修改</span>
          <el-divider :direction="'horizontal'" :content-position="'center'"></el-divider>
        </div>
        <div class="security-setting-item">
          <div class="security-setting-item-content">
            <span class="item-title">绑定邮箱</span>
            <span class="item-value">已绑定邮箱：</span>
            <span style="color:#C0C4CC;">{{emailCover}}</span>
          </div>
          <span class="modify-item" @click.stop="handleModifyEmail" v-if="$store.state.auth.currentUser.permissions.indexOf(62)!=-1">修改</span>
          <el-divider :direction="'horizontal'" :content-position="'center'"></el-divider>
        </div>
        <div class="security-setting-item">
          <div class="security-setting-item-content">
            <span class="item-title">绑定微信</span>
            <span class="item-value">已绑定微信：</span>
            <span style="color:#C0C4CC;">{{wechatMessage}}</span>
          </div>
          <span class="modify-item" @click.stop="handleModifyWechat" v-if="$store.state.auth.currentUser.permissions.indexOf(62)!=-1">修改</span>
          <el-divider :direction="'horizontal'" :content-position="'center'"></el-divider>
        </div>
        <div class="security-setting-item">
          <div class="security-setting-item-content">
            <span class="item-title">人脸识别</span>
            <span :class="{'have-face-verification':faceVerification}" class="item-value">{{faceVerificationMessage}}</span>
          </div>
          <span v-if="!faceVerification&&$store.state.auth.currentUser.permissions.indexOf(62)!=-1" class="modify-item" @click.stop="handleVerifyFace">认证</span>
          <el-divider :direction="'horizontal'" :content-position="'center'"></el-divider>
        </div>
      </el-card>


      <!-- 各个设置的修改弹出框 -->
      <!-- 修改密码 -->
      <el-dialog
        title="修改密码"
        :visible.sync="modifyPasswordDialogVisible"
        :close-on-click-modal="false"
        :destroy-on-close="true"
        :show-close="false"
        class="modify-password-dialog">
        <el-form
          label-width="100px"
          :model="modifyPasswordForm"
          status-icon
          :rules="modifyPasswordRules"
          ref="modifyPasswordForm">
          <el-form-item class="form-item" label="新密码：" prop="newPassword">
            <el-input
              type="password"
              :show-password="true"
              v-model="modifyPasswordForm.newPassword"
              :clearable="true"
              autocomplete="off"></el-input>
          </el-form-item>
          <el-form-item class="form-item" label="确认密码：" prop="confirmPassword">
            <el-input
              type="password"
              :show-password="true"
              v-model="modifyPasswordForm.confirmPassword"
              :clearable="true"
              autocomplete="off"></el-input>
          </el-form-item>
          <el-form-item class="form-item">
            <el-button type="primary" @click.stop="submitUpdatePassword('modifyPasswordForm')">提交</el-button>
            <el-button @click.stop="modifyPasswordDialogVisible = false">取消</el-button>
          </el-form-item>
        </el-form>
      </el-dialog>
      <!-- 修改邮箱 -->
      <el-dialog
        title="修改邮箱"
        :visible.sync="modifyEmailDialogVisible"
        :close-on-click-modal="false"
        :destroy-on-close="true"
        :show-close="false"
        class="modify-email-dialog">
        <el-form
          label-width="100px"
          :model="modifyEmailForm"
          status-icon
          :rules="modifyEmailRules"
          ref="modifyEmailForm">
          <el-form-item class="form-item" label="新邮箱：" prop="newEmail">
            <el-input
              type="email"
              v-model="modifyEmailForm.newEmail"
              :clearable="true"
              autocomplete="off"></el-input>
            <span class="send-verification-code" @click.stop="sendVerificationCode('modifyEmailForm')">
              {{countDown}}
            </span>
          </el-form-item>
          <el-form-item class="form-item" label="验证码：" prop="verificationCode">
            <el-input
              type="text"
              v-model="modifyEmailForm.verificationCode"
              :clearable="true"
              autocomplete="off"></el-input>
          </el-form-item>
          <el-form-item class="form-item">
            <el-button type="primary" @click.stop="submitUpdateEmail('modifyEmailForm')">提交</el-button>
            <el-button @click.stop="() => {modifyEmailDialogVisible = false;countdown=0} ">取消</el-button>
          </el-form-item>
        </el-form>
      </el-dialog>
      <!-- 人脸认证 -->
      <el-dialog
        title="人脸认证"
        :visible.sync="modifyFaceDialogVisible"
        :close-on-click-modal="false"
        :destroy-on-close="true"
        :show-close="false"
        class="face-verify-dialog"
        >
        <div class="system-logo">
          <img src="@/assets/images/buct-sm-logo.png" alt="logo">
        </div>
        <div class="face-verify-box">
          <div class="face-verify-left">
            <div ref="canvasParent" class="face-verify-left-content">
              <video height="250" ref="videoDom" id="video" preload autoplay loop muted></video>
              <canvas height="250" ref="canvasDOM"></canvas>
            </div>
            <div class="face-verify-footer">
              <el-button type="primary" @click.stop="initTracker">抓取人脸</el-button>
              <el-button @click.stop="closeFaceVerifyDialog">取消</el-button>
            </div>
          </div>
        </div>
      </el-dialog>
  </div>
</template>

<script>
import { request } from "@/network/request";
import PageHeader from "@/components/page-header";
require('tracking/build/tracking-min.js')
require('tracking/build/data/face-min.js')

export default {
  components: {
    PageHeader
  },
  data() {
    let validatePass = (rule, value, callback) => {
      if (value === '') {
        callback(new Error('请再次输入密码'));
      } else if (value !== this.modifyPasswordForm.newPassword) {
        callback(new Error('两次输入密码不一致!'));
      } else {
        callback();
      }
    };
    let validateEmail = (rule, value, callback) => {
      let re = /^(([^()[\]\\.,;:\s@\"]+(\.[^()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/
      if (value === '') {
        callback(new Error('请输入新邮箱！'));
      } else if (!re.test(value)) {
        callback(new Error('请输入正确的邮箱格式！'));
      } else {
        callback();
      }
    };
    return {
      title: "Security Setting",
      items:[
        {
          text: "DMS"
        },
        {
          text: "个人中心"
        },
        {
          text: "安全设置",
          active: true
        }
      ],

      // 原本的显示信息
      password: "zjh121543",
      phone: "18810280617",
      email: "yykzhjh@163.com",
      wechat: "zjh18810280617",
      faceVerification: false,

      // 修改密码的弹出框数据
      modifyPasswordDialogVisible: false,
      modifyPasswordForm: {
        newPassword: "",
        confirmPassword: "",
      },
      modifyPasswordRules: {
        newPassword: [
          { required: true, message: '请输入新密码', trigger: 'blur' }
        ],
        confirmPassword: [
          { required: true, message: '请再次输入密码', trigger: 'blur' },
          { validator: validatePass, trigger: 'blur' }
        ],
      },

      // 修改邮箱的弹出框数据
      modifyEmailDialogVisible: false,
      countdown: 0,
      modifyEmailForm: {
        newEmail: "",
        verificationCode: "",
      },
      modifyEmailRules: {
        newEmail: [
          { required: true, message: '请输入新邮箱', trigger: 'blur' },
          { validator: validateEmail, trigger: 'blur' }
        ],
        verificationCode: [
          { required: true, message: '请输入验证码', trigger: 'blur' },
        ]
      },

      // 人脸认证弹出框的数据
      modifyFaceDialogVisible: false,
      video: null,
      canvas: null,
      count: 0,
      isdetected: "",
      rect: {
        x: 0,
        y: 0,
        width: 0,
        height: 0,
      },
      dataUrl: "",
      imgbase64: "",
    }
  },
  computed: {
    passwordPower() {
      var strongRegex = new RegExp("^(?=.{8,})(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])(?=.*\\W).*$", "g");
      var mediumRegex = new RegExp("^(?=.{7,})(((?=.*[A-Z])(?=.*[a-z]))|((?=.*[A-Z])(?=.*[0-9]))|((?=.*[a-z])(?=.*[0-9]))).*$", "g");
      var enoughRegex = new RegExp("(?=.{6,}).*", "g");
      if (this.password != ""&&this.password!=null) {
        if (false == enoughRegex.test(this.password)) {
          //弱,密码小于六位
          return "弱"
        }
        else if (strongRegex.test(this.password)) {
          //强,密码为八位及以上并且字母数字特殊字符三项都包括
          return "强"
        }
        else if (mediumRegex.test(this.password)) {
          //中等,密码为七位及以上并且字母、数字、特殊字符三项中有两项，强度是中等
          return "中"
        }
        else {
          //弱,如果密码为6为及以下，就算字母、数字、特殊字符三项都包括，强度也是弱的
          return "弱"
        }  
      }
      else {
        return "无"
      }
    },
    phoneCover() {
      if (this.phone != "" && this.phone != null) {
        return this.phone.substr(0,3) + "****" + this.phone.substr(7,4)
      }
      else {
        return "未绑定"
      }
    },
    emailCover() {
      if (this.email != "" && this.email != null) {
        let emailSplits = this.email.split("@")
        return emailSplits[0].substr(0, emailSplits[0].length-4) + "****@" + emailSplits[1]
      }
      else {
        return "未绑定"
      }
    },
    wechatMessage() {
      if (this.wechat != "" && this.wechat != null) {
        return this.wechat
      }
      else {
        return "未绑定"
      }
    },
    faceVerificationMessage() {
      return this.faceVerification?"已认证":"未认证"
    },
    countDown() {
      if (this.countdown == 0) {
        return "发送验证码"
      }else {
        return "重新发送(" + this.countdown + ")"
      }
    },
  },
  methods: {
    getUserSecurityInfo() {
      request({
        url: "User/UserSecurityInfo",
        method: "get",
        params: {
          userid: this.$store.state.auth.currentUser.userid
        }
      }).then(res => {
        const data = res.data
        if (data.errcode == 0) {
          console.log(data.res)
          this.password = data.res.password
          this.phone = data.res.phone
          this.email = data.res.email
          this.wechat = data.res.wechat
          this.faceVerification = data.res.faceVerification
        }else {
          alert(data.errmsg)
        }
      }).catch(err => {
        alert(err)
      })
    },
    handleModifyPassword() {
      this.modifyPasswordForm = {
        newPassword: "",
        confirmPassword: "",
      }
      this.modifyPasswordDialogVisible = true
    },
    handleModifyPhone() {

    },
    handleModifyEmail() {
      this.modifyEmailForm = {
        newEmail: "",
        verificationCode: ""
      }
      this.countdown = 0
      this.modifyEmailDialogVisible = true
    },
    handleModifyWechat() {

    },
    handleVerifyFace() {
      this.count = 0
      this.isdetected = ""
      this.dataUrl = ""
      this.imgbase64 = ""
      this.rect = {
        x: 0,
        y: 0,
        width: 0,
        height: 0,
      }
      this.modifyFaceDialogVisible = true
      this.$nextTick(() => {
        this.video = this.$refs.videoDom
        this.canvas = this.$refs.canvasDOM
        const canvasParentWidth = parseFloat(window.getComputedStyle(this.$refs.canvasParent).width)
        console.log(canvasParentWidth)
        this.video.width = canvasParentWidth
        this.canvas.width = canvasParentWidth
      });
    },
    closeFaceVerifyDialog() {
      this.modifyFaceDialogVisible = false
      this.onStopTracking()
    },
    setCountDown() {
      if (this.countdown <= 0) {
        return ;
      }
      console.log(this.countdown)
      this.countdown--
      setTimeout(() => {
        this.setCountDown()
      }, 1000)
    },
    submitUpdatePassword(formName) {
      this.$refs[formName].validate((valid) => {
        if (valid) {
          request({
            url: "User/ModifyPassword",
            method: "get",
            params: {
              userid: this.$store.state.auth.currentUser.userid,
              newPassword: this.modifyPasswordForm.newPassword,
            }
          }).then(res => {
            const data = res.data
            if (data.errcode == 0) {
              this.$message.success("修改密码成功！");
              this.modifyPasswordDialogVisible = false
              this.getUserSecurityInfo()
            }else {
              alert(data.errmsg)
            }
          }).catch(err => {
            alert(err)
          })
        } else {
          this.$message.warning("提交的信息不满足验证要求！");
        }
      });
    },
    sendVerificationCode(formName) {
      if (this.countdown > 0) return ;
      this.$refs[formName].validateField('newEmail', emailError => {
        if (!emailError) {
          request({
            url: "User/EmailVerificationCode",
            method: "get",
            params: {
              userid: this.$store.state.auth.currentUser.userid,
              email: this.modifyEmailForm.newEmail,
            }
          }).then(res => {
            const data = res.data
            if (data.errcode == 0) {
              this.countdown = 60
              this.setCountDown()
              this.$message.success("验证码已经发送到您的邮箱，5分钟之内验证码有效！");
            }else {
              alert(data.errmsg)
            }
          }).catch(err => {
            alert(err)
          })
        } else {
          this.$message.warning("提交的信息不满足验证要求！");
        }
      });
    },
    submitUpdateEmail(formName) {
      this.$refs[formName].validate((valid) => {
        if (valid) {
          request({
            url: "User/ModifyEmail",
            method: "get",
            params: {
              userid: this.$store.state.auth.currentUser.userid,
              newEmail: this.modifyEmailForm.newEmail,
              verificationCode: this.modifyEmailForm.verificationCode
            }
          }).then(res => {
            const data = res.data
            if (data.errcode == 0) {
              this.$message.success("修改邮箱成功！");
              this.modifyEmailDialogVisible = false
              this.getUserSecurityInfo()
            }else {
              alert(data.errmsg)
            }
          }).catch(err => {
            alert(err)
          })
        } else {
          this.$message.warning("提交的信息不满足验证要求！");
        }
      });
    },
    initTracker(){
      // 启用摄像头,这一个是原生调用摄像头的功能,不写的话有时候谷歌浏览器调用摄像头会失败
      navigator.mediaDevices
        .getUserMedia({video: true,audio: true})
        .then(this.getMediaStreamSuccess)
        .catch(this.getMediaStreamError)

      this.context  = this.canvas.getContext('2d')

      // 初始化tracking参数
      this.tracker = new tracking.ObjectTracker("face");
      this.tracker.setInitialScale(4);
      this.tracker.setStepSize(2);
      this.tracker.setEdgesDensity(0.1);
      this.tracker.on("track", event => {
        this.onTracked(event);
      });

      // tracking启用摄像头,这里我选择调用原生的摄像头
      // tracking.track(this.video, this.tracker, { camera: true });

      // 如果是读取视频，可以用trackerTask.stop trackerTask.run来暂停、开始视频
      this.count = 0
      this.trackerTask = tracking.track(this.video, this.tracker);
    },
    onTracked(event){
      // 判断终止条件, stop是异步的，不返回的话，还会一直截图
      if (this.count > 5) {
        this.onStopTracking();
        return;
      }

      // 画框框
      this.context.clearRect(0, 0, this.canvas.width, this.canvas.height);
      event.data.forEach(rect => {
        this.context.lineWidth = 1;
        this.context.strokeStyle = "#a64ceb";
        //'#a64ceb';
        this.context.strokeRect(rect.x, rect.y, rect.width, rect.height);
        this.rect.x = rect.x
        this.rect.y = rect.y
        this.rect.width = rect.width
        this.rect.height = rect.height
        console.log(rect.x, rect.y, rect.width, rect.height)
        this.context.font = "11px Helvetica";
        this.context.fillStyle = "#fff";
        // 截图

        if (this.count <= 5) {
          this.count += 1
          if (this.count > 5) {
            this.isdetected = '已检测到人脸，正在识别'
            this.getPhoto()
          }
        }
      });
      if (event.data.length == 0) {
        this.count --
        if (this.count < 0) this.count = 0
        this.isdetected = '请您保持脸部在画面中央'
      }
      // 视频中心展示文字
      this.context.fillText(this.isdetected, 100,30);
    },
    onStopTracking() {
      this.trackerTask.stop();
      this.video.pause();
      // 关闭摄像头
      this.video.srcObject = null
      window.stream.getTracks().forEach(track => track.stop())

    },
    getPhoto(){
      this.isdetected = '人脸抓取成功，等待上传'
      this.context.drawImage(this.video, 0,0, this.canvas.width, this.canvas.height)
      this.dataUrl = this.canvas.toDataURL('image/jpeg', 1);
      this.context.strokeRect(this.rect.x, this.rect.y, this.rect.width, this.rect.height);
      this.imgbase64 = this.dataUrl.replace(/^data:image\/\w+;base64,/, "");
      this.$confirm('人脸抓取成功，是否上传图像？', '人脸识别认证', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
        center: true,
        showClose: false,
        closeOnClickModal: false,
        closeOnPressEscape: false,
        customClass: "message-box-position"
      }).then(() => {
        this.handleUploadFace()
      }).catch(() => {});
    },
    handleUploadFace() {
      request({
        url: "User/FaceVerify",
        method: "post",
        data: {
          userid: this.$store.state.auth.currentUser.userid,
          face: this.imgbase64,
        }
      }).then(res => {
        const data = res.data
        if (data.errcode == 0) {
          this.$message.success("人脸认证成功！")
          this.closeFaceVerifyDialog()
          this.getUserSecurityInfo()
        }else {
          alert(data.errmsg)
        }
      }).catch(err => {
        alert(err)
      })
    },
    // 视频流启动
    getMediaStreamSuccess(stream) {
      window.stream = stream
      this.video.srcObject = stream
    },
    // 视频媒体流失败
    getMediaStreamError(error) {
      alert('视频媒体流获取错误' + error)
    },
  },
  mounted:function() {
    this.getUserSecurityInfo()
  }
}
</script>

<style lang="scss">

.message-box-position {
  margin-top: 35vh !important;
}

.security-setting-page {

  .security-setting-card {
    min-height: 600px;
    width: 100%;
  }

  .security-setting-item {
    width: 70%;
    margin-left: 10%;
    margin-top: 40px;
  }

  .security-setting-item-content {
    display: inline-block;
    width: 70%;
  }

  .item-title {
    font-weight: 600;
    font-family: "微软雅黑";
    display: block;
    margin-bottom: 5px;
  }

  .item-value {
    color: #C0C4CC;
  }

  .have-face-verification {
    color: lightgreen !important;
  }

  .modify-item {
    float: right;
    position: relative;
    top: 15px;
    color:cornflowerblue;
    cursor: pointer;
    vertical-align: middle;
  }


  .modify-password-dialog {
    .el-dialog {
      width: 40% !important;
    }
  }

  .modify-email-dialog {
    .el-dialog {
      width: 40% !important;
    }
  }

  .form-item {
    width: 80%;
  }

  .send-verification-code {
    color:cornflowerblue;
    cursor: pointer;

    &:hover {
      text-decoration: underline;
    }
  }

  .face-verify-dialog {
    .el-dialog {
      width: 30% !important;
    }
  }

  .system-logo {
    height: 130px;
    width: 130px;
    border-radius: 50%;
    padding: 10px;
    box-shadow: 0 0 10px #ddd;
    position: absolute;
    left: 50%;
    transform: translate(-50%, -100%);
    background-color: #fff;

    img {
      height: 100%;
      width: 100%;
      border-radius: 50%;
      background-color: #eee;
    }
  }

  .face-verify-box {
    display: flex;
    justify-content: space-around;
    width: 100%;
    min-height: 350px;
  }

  .face-verify-left {
    display: inline-block;
    width: 70%;
    
    .face-verify-left-content {
      position: relative;
      width: 100%;
      min-height: 300px;

      video, canvas {
        position: absolute;
      }
    }
  }

  .face-verify-footer {
    width: 100%;
    display:flex;
    justify-content: center;
  }

  .face-verify-right {
    display: inline-block;
    width: 35%;

    .face-verify-right-content {
      position: relative;
      width: 100%;
      min-height: 300px;

      .captured-face {
        position: absolute;
        width: 100%;
        height: 250px;
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
  }

}

</style>