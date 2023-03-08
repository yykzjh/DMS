<template>
  <el-dialog
    title="查看文件详情"
    :close-on-click-modal="false"
    :destroy-on-close="true"
    :visible.sync="dialogFormVisible"
    class="look-file-info">
    <div class="look-file-basic-info">
      <div class="file-basic-info-item" v-for="item in fileInfo" :key="item.label">
        <span>{{item.label}}</span>
        <p v-if="item.label!='附件：'">{{item.value}}</p>
        <div v-else style="display:inline-block;float:right">
          <a v-for="subFile in item.value" :key="subFile" @click.prevent="showAttachmentFile(subFile)">{{subFile}}</a>
        </div>
      </div>
      <div class="file-basic-info-item" style="margin-top:50px;margin-left:50px;">
        <el-button  type="primary" icon="el-icon-download" round @click.stop="handleDownloadFolder">下载该文件所有附件</el-button>
      </div>
    </div>
    <div class="preview-file">
      <div v-if="fileDataType=='image'">
        <el-image
         class="image-file"
        :lazy="true"
        :src="imageData"
        :fit="'contain'"
        :z-index="2010"
        :preview-src-list="[imageData]"></el-image>
      </div>
      <div v-else-if="fileDataType=='pdf'">
        <iframe
          id="myIframe"
          :src="pdfData"
          class="iframe-file"
          :frameborder="1"
        ></iframe>
      </div>
      <div v-else-if="fileDataType=='text'">
        <iframe
          :src="textData"
          class="text-file"
          :frameborder="1"
        ></iframe>
      </div>
      <el-button
        v-if="currentFileName!=''"
        style="position:absolute;right:20px;bottom:20px"
        type="primary"
        icon="el-icon-download"
        round
        @click.stop="handleDownloadFile">
        下载该附件
      </el-button>
    </div>
  </el-dialog>
</template>

<script>
import { request } from "@/network/request";
import pdf from 'vue-pdf'

export default {
  components: {pdf},
  props: {
    dialogFormVisibleProp: {
      type: Boolean,
      default: false
    },
    fileId: {
      type: Number,
      default: 0
    },
    fileInfo: Array,
  },
  data() {
    return {
      dialogFormVisible: false,
      currentFileName: "",
      fileDataType: "",
      imageData: "",
      pdfData: "",
      textData: "",
    }
  },
  watch: {
    "dialogFormVisibleProp"(newVal, oldVal) {
      this.dialogFormVisible = newVal
    },
    dialogFormVisible: {
      handler: "handleVisibleChange"
    }
  },
  methods: {
    handleVisibleChange(newVal, oldVal) {
      this.pdfData = ""
      this.imageData = ""
      this.fileDataType = ""
      this.elseData = ""
      this.currentFileName = ""
      this.$emit("update:dialogFormVisibleProp", newVal)
    },
    showAttachmentFile(attachFileName) {
      this.currentFileName = attachFileName
      request({
        url: "File/PreviewFile",
        method: "get",
        params: {
          fileId: this.fileId,
          fileName: attachFileName
        },
        responseType: 'blob',
      }).then(res => {
        console.log(res)
        let data = res.data
        const type = data.type || null
        let fileURL = ""
        // 根据返回的数据类型判断是否请求出错
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
        else if(type.includes('image/jpeg') || type.includes('image/png')){
          fileURL = URL.createObjectURL(data)
          this.imageData = fileURL
          this.fileDataType = "image"
        }
        else if(type.includes('application/pdf')){
          fileURL = URL.createObjectURL(data)
          this.pdfData = "/pdf/web/viewer.html?file=" + fileURL
          this.fileDataType = "pdf"
        }
        else if(type.includes('text/plain')||type.includes('text/html')) {
          fileURL = URL.createObjectURL(data)
          this.textData = fileURL
          this.fileDataType = "text"
        }
      }).catch(err => {
        alert(err)
      })
    },
    handleDownloadFolder() {
      request({
        url:"File/DownloadFolder", 
        params:{
          fileId:this.fileId
        },
        responseType: "blob"
      }).then(res => {
        const link = document.createElement('a');
        // 创建Blob对象，设置文件类型
        let blob = new Blob([res.data]);
        link.href = URL.createObjectURL(blob); // 创建URL
        let tmpStr = res.headers.content_disposition
        let pos = tmpStr.indexOf('=')
        link.setAttribute('download', decodeURIComponent(tmpStr.slice(pos+2,-1))); // 设置下载文件名称
        link.click(); // 下载文件
      }).catch(err => {
        alert(err)
      })
    },
    handleDownloadFile() {
      request({
        url: "File/DownloadFile",
        method: "get",
        params: {
          fileId: this.fileId,
          fileName: this.currentFileName
        },
        responseType: "blob"
      }).then(res => {
        const link = document.createElement('a');
        // 创建Blob对象，设置文件类型
        let blob = new Blob([res.data]);
        link.href = URL.createObjectURL(blob); // 创建URL
        let tmpStr = res.headers.content_disposition
        let pos = tmpStr.indexOf('=')
        link.setAttribute('download', decodeURIComponent(tmpStr.slice(pos+2,-1))); // 设置下载文件名称
        link.click(); // 下载文件
      }).catch(err => {
        alert(err)
      })
    }
  }
};
</script>

<style lang="scss">
.look-file-info {

  .el-dialog {
    width: 90% !important;
    margin-top: 10vh !important;
  }

  .el-dialog__body {
    display: flex;
    justify-content: space-around;
  }

  .look-file-basic-info {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    justify-content: space-around;
    width: 45%;
    height: 100%;

    .file-basic-info-item {
      margin-left:20px;
      margin-top:20px;
      display: flex;
      justify-content: flex-start;
      span {
        font-size: 1.1rem;
        font-weight: 600;
      }
      p {
        display: inline;
        font-size: 1rem;
      }
      a {
        font-size: 0.8rem;
        display: block;
      }
      a:hover {
        cursor: pointer !important;
        text-decoration: underline !important;
        color: cornflowerblue !important;
      }
    }
  }

  .preview-file {
    display: inline-block;
    width: 54%;
    height: 600px;
  }

  .image-file {
    width: 100%;
    height: 550px;
  }

  .iframe-file {
    width: 100%;
    height: 550px;
  }

  .text-file {
    width: 100%;
    height: 550px;
  }
}




</style>