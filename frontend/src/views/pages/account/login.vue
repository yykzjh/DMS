<template>
  <div class="login-page">
    <div>
      <div class="container-fluid p-0">
        <div class="row no-gutters">
          <div class="col-lg-4">
            <div class="authentication-page-content p-4 d-flex align-items-center min-vh-100">
              <div class="w-100">
                <div class="row justify-content-center">
                  <div class="col-lg-9">
                    <div>
                      <div class="text-center">
                        <div>
                          <a href="/" class="logo">
                            <img src="@/assets/images/buct-logo.png" height="50" alt="logo" />
                          </a>
                        </div>

                        <h4 class="font-size-18 mt-4">Welcome Back !</h4>
                        <p class="text-muted">Sign in to continue to DMS.</p>
                      </div>

                      <b-alert
                        variant="danger"
                        class="mt-3"
                        v-if="notification.message"
                        show
                        dismissible
                      >{{notification.message}}</b-alert>

                      <div class="p-2 mt-5">
                        <form class="form-horizontal" @submit.prevent="tryToLogIn">
                          <div class="form-group auth-form-group-custom mb-4">
                            <i class="ri-mail-line auti-custom-input-icon"></i>
                            <label for="userid">UserID</label>
                            <input
                              type="userid"
                              v-model="userid"
                              class="form-control"
                              id="userid"
                              placeholder="Enter userid"
                              :class="{ 'is-invalid': submitted && $v.userid.$error }"
                            />
                            <div v-if="submitted && $v.userid.$error" class="invalid-feedback">
                              <span v-if="!$v.userid.required">userid is required.</span>
                              <span v-if="!$v.userid.userid">Please enter valid userid.</span>
                            </div>
                          </div>

                          <div class="form-group auth-form-group-custom mb-4">
                            <i class="ri-lock-2-line auti-custom-input-icon"></i>
                            <label for="userpassword">Password</label>
                            <input
                              v-model="password"
                              type="password"
                              class="form-control"
                              id="userpassword"
                              placeholder="Enter password"
                              :class="{ 'is-invalid': submitted && $v.password.$error }"
                            />
                            <div
                              v-if="submitted && !$v.password.required"
                              class="invalid-feedback"
                            >Password is required.</div>
                          </div>

                          <div class="custom-control custom-checkbox">
                            <input
                              v-model="requireRemenber"
                              type="checkbox"
                              class="custom-control-input"
                              id="customControlInline"
                            />
                            <label
                              class="custom-control-label"
                              for="customControlInline"
                            >Remember me</label>
                          </div>

                          <div class="mt-4 text-center">
                            <button
                              class="btn btn-primary w-md waves-effect waves-light"
                              type="submit"
                            >Log In</button>
                          </div>

                          <div class="mt-4 text-center">
                            <div class="text-muted">
                              <i class="mdi mdi-lock mr-1"></i> Forgot your password?
                            </div>
                          </div>
                        </form>
                      </div>

                      <div class="other-login-ways">
                        <span>other login ways:</span>
                        <div style="display:inline-block;justify-content:flex-start;">
                          <el-button round class="other-login-ways-button">
                            <img class="other-login-ways-image" :src="require('@/assets/images/wechat.png')">
                          </el-button>
                          <el-button class="other-login-ways-button" @click.stop="handleFaceRecognitionDialogVisible">
                            <img class="other-login-ways-image" :src="require('@/assets/images/face.png')">
                          </el-button>
                        </div>
                        <el-dialog
                          title="人脸识别登录"
                          :visible.sync="faceRecognitionLoginVisible"
                          :close-on-click-modal="false"
                          :destroy-on-close="true"
                          :show-close="false"
                          class="face-recognition-dialog"
                          >
                          <div class="system-logo">
                            <img src="@/assets/images/buct-sm-logo.png" alt="logo">
                          </div>
                          <div class="face-recognition-box">
                            <div class="face-recognition-left">
                              <div ref="canvasParent" class="face-recognition-left-content">
                                <video height="250" ref="videoDom" id="video" preload autoplay loop muted></video>
                                <canvas height="250" ref="canvasDOM"></canvas>
                              </div>
                              <div class="face-recognition-footer">
                                <el-button type="primary" @click.stop="initTracker">开启摄像头</el-button>
                                <el-button @click.stop="closeFaceRecognitionDialog">取消</el-button>
                              </div>
                            </div>
                            <!-- <div class="face-recognition-right">
                              <div class="face-recognition-right-content">
                                <el-image :src="dataUrl" :fit="'fit'" class="captured-face">
                                  <div :slot="'error'" class="el-image__error">请开启摄像头抓取人脸</div>
                                </el-image>
                              </div>
                              <div class="face-recognition-footer">
                                <el-button type="primary" @click.stop="handleUploadFace">上传人脸图像</el-button>
                              </div>
                            </div> -->
                          </div>
                        </el-dialog>
                      </div>

                      <div class="mt-5 text-center">
                        <p>
                          © 2021 DMS. Crafted with
                          <i class="mdi mdi-heart text-danger"></i> by yykzjh
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="col-lg-8">
            <div class="authentication-bg">
              <div class="bg-overlay"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { required } from "vuelidate/lib/validators";
import { request } from "@/network/request";
require('tracking/build/tracking-min.js')
require('tracking/build/data/face-min.js')
import {
  authMethods,
  notificationMethods
} from "@/state/helpers";

export default {
  data() {
    return {
      userid: "2017040394",
      password: "2017040394",
      requireRemenber:false,
      submitted: false,

      faceRecognitionLoginVisible: false,
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
    };
  },
  computed: {
    notification() {
      return this.$store ? this.$store.state.notification : null;
    }
  },
  created() {
    document.body.classList.add("auth-body-bg");
  },
  validations: {
    userid: { required },
    password: { required }
  },
  methods: {
    ...authMethods,
    // ...authFackMethods,
    ...notificationMethods,
    // Try to log the user in with the username
    // and password they provided.
    tryToLogIn() {
      this.submitted = true;
      this.$v.$touch();

      if (this.$v.$invalid) {
        return;
      } else {
        this.tryingToLogIn = true;
        this.authError = null;

        this.logIn({
          userid: this.userid,
          password: this.password,
          requireRemenber: this.requireRemenber
        }).then( result => {
          if (result.errcode == 0) {
            // print(result)
            this.tryingToLogIn = false;
            this.isAuthError = false;
            this.$router.push(
              this.$route.query.redirectFrom || { name: "home" }
            );
          } else {
            this.tryingToLogIn = false;
            this.authError = result.errmsg ? result.errmsg : "";
            this.isAuthError = true;
            alert(result.errmsg)
          }
        }).catch( err => {
          this.tryingToLogIn = false;
          this.authError = err.errmsg ? err.errmsg : "";
          this.isAuthError = true;
          alert(err)
        })
      }
    },
    handleFaceRecognitionDialogVisible() {
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
      this.faceRecognitionLoginVisible = true
      this.$nextTick(() => {
        this.video = this.$refs.videoDom
        this.canvas = this.$refs.canvasDOM
        const canvasParentWidth = parseFloat(window.getComputedStyle(this.$refs.canvasParent).width)
        console.log(canvasParentWidth)
        this.video.width = canvasParentWidth
        this.canvas.width = canvasParentWidth
      });
    },
    closeFaceRecognitionDialog() {
      this.faceRecognitionLoginVisible = false
      this.onStopTracking()
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
      this.$confirm('人脸抓取成功，是否上传图像？', '人脸识别登录', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
        center: true,
        showClose: false,
        closeOnClickModal: false,
        closeOnPressEscape: false,
        customClass: "message-box-position",
      }).then(() => {
        this.handleUploadFace()
      }).catch(() => {});
    },
    handleUploadFace() {
      request({
        url: "User/FaceRecognitionLogin",
        method: "post",
        data: {
          face: this.imgbase64,
        }
      }).then(res => {
        const data = res.data
        if(data.errcode == 0) {
            this.$store.commit('auth/SET_CURRENT_USER', data.user)
            sessionStorage.setItem("user", JSON.stringify(data.user))
            if (this.requireRemenber) localStorage.setItem("user", JSON.stringify(data['user']))
            this.$message.success("登录成功！")
            this.closeFaceRecognitionDialog()
            this.tryingToLogIn = false;
            this.isAuthError = false;
            this.$router.push(
              this.$route.query.redirectFrom || { name: "home" }
            );
        }
        else {
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
  }
};
</script>


<style lang="scss">

.message-box-position {
  margin-top: 35vh !important;
}

.login-page {

  .other-login-ways {
    margin-top: 20px;

    .other-login-ways-button {
      margin-left: 20px;
      padding: 0;

      .other-login-ways-image {
        width:30px !important;
        height:30px !important;
      }
    }

    .face-recognition-dialog {
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

    .face-recognition-box {
      display: flex;
      justify-content: space-around;
      width: 100%;
      min-height: 350px;
    }

    .face-recognition-left {
      display: inline-block;
      width: 70%;
      
      .face-recognition-left-content {
        position: relative;
        width: 100%;
        min-height: 300px;

        video, canvas {
          position: absolute;
        }
      }
    }

    .face-recognition-footer {
      width: 100%;
      display:flex;
      justify-content: center;
    }

    .face-recognition-right {
      display: inline-block;
      width: 35%;

      .face-recognition-right-content {
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
}

</style>
