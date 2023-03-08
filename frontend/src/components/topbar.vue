<script>
import i18n from "../i18n";
import {
  authMethods
} from "@/state/helpers";
import { request } from "@/network/request";

export default {
  data() {
    return {
      languages: [
        {
          flag: require("@/assets/images/flags/china.png"),
          language: "zh",
          title: "Chinese"
        },
        {
          flag: require("@/assets/images/flags/us.jpg"),
          language: "en",
          title: "English"
        },
      ],
      current_entry: {
        flag: require("@/assets/images/flags/china.png"),
        language: "zh",
        title: "Chinese"
      },

      myAvatar: "",
    };
  },
  computed: {
    userName() {
      return this.$store.state.auth.currentUser == null? "":this.$store.state.auth.currentUser.username
    },
    languageImage() {
      return i18n.locale=='zh'?this.languages[0].flag:this.languages[1].flag
    }
  },
  components: {},
  watch: {
    "$store.state.auth.avatarChange"(newVal, oldVal) {
      this.getAvatar()
    }
  },
  methods: {
    ...authMethods,
    toggleMenu() {
      this.$parent.toggleMenu();
    },
    initFullScreen() {
      document.body.classList.toggle("fullscreen-enable");
      if (
        !document.fullscreenElement &&
        /* alternative standard method */ !document.mozFullScreenElement &&
        !document.webkitFullscreenElement
      ) {
        // current working methods
        if (document.documentElement.requestFullscreen) {
          document.documentElement.requestFullscreen();
        } else if (document.documentElement.mozRequestFullScreen) {
          document.documentElement.mozRequestFullScreen();
        } else if (document.documentElement.webkitRequestFullscreen) {
          document.documentElement.webkitRequestFullscreen(
            Element.ALLOW_KEYBOARD_INPUT
          );
        }
      } else {
        if (document.cancelFullScreen) {
          document.cancelFullScreen();
        } else if (document.mozCancelFullScreen) {
          document.mozCancelFullScreen();
        } else if (document.webkitCancelFullScreen) {
          document.webkitCancelFullScreen();
        }
      }
    },
    toggleRightSidebar() {
      this.$parent.toggleRightSidebar();
    },
    setLanguage(entry) {
      i18n.locale = entry.language;
      this.current_entry = entry;
    },
    handleLogout() {
      this.logOut()
      this.$router.push({name: 'login'})
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
  },
  mounted:function() {
    this.getAvatar()
  }
};
</script>

<template>
  <header id="page-topbar">
    <div class="navbar-header">
      <div class="d-flex">
        <!-- LOGO -->
        <div class="navbar-brand-box">
          <a href="index.html" class="logo logo-dark">
            <span class="logo-sm">
              <img src="@/assets/images/buct-sm-logo.png" alt height="35" />
            </span>
            <span class="logo-lg">
              <img src="@/assets/images/buct-logo.png" alt height="60" />
            </span>
          </a>

          <a href="index.html" class="logo logo-light">
            <span class="logo-sm">
              <img src="@/assets/images/buct-sm-logo-light.png" alt height="35" />
            </span>
            <span class="logo-lg">
              <img src="@/assets/images/buct-logo-light.png" alt height="60" />
            </span>
          </a>
        </div>
        
        <!-- 收缩左侧导航栏 -->
        <button
          @click.stop="toggleMenu"
          type="button"
          class="btn btn-sm px-3 font-size-24 header-item waves-effect"
          id="vertical-menu-btn"
        >
          <i class="ri-menu-2-line align-middle"></i>
        </button>
      </div>

      <div class="d-flex">
        <!-- 语言 -->
        <b-dropdown variant="white" right toggle-class="header-item">
          <template v-slot:button-content>
            <img class :src="languageImage" alt="Header Language" height="16" />
          </template>
          <b-dropdown-item
            class="notify-item"
            v-for="(entry, i) in languages"
            :key="`Lang${i}`"
            :value="entry"
            @click.stop="setLanguage(entry)"
            :link-class="{'active': entry.language === current_entry.language}"
          >
            <img :src="`${entry.flag}`" alt="user-image" class="mr-1" height="12" />
            <span class="align-middle">{{ entry.title }}</span>
          </b-dropdown-item>
        </b-dropdown>

        <!-- 全屏 -->
        <div class="dropdown d-none d-lg-inline-block ml-1">
          <button
            type="button"
            class="btn header-item noti-icon waves-effect"
            @click="initFullScreen"
          >
            <i class="ri-fullscreen-line"></i>
          </button>
        </div>

        <!-- 登出 -->
        <b-dropdown
          right
          variant="black"
          toggle-class="header-item"
          class="d-inline-block user-dropdown"
        >
          <template v-slot:button-content>
            <img
              class="rounded-circle header-profile-user"
              :src="myAvatar"
              alt="Header Avatar"
            />
            <span class="d-none d-xl-inline-block ml-1">{{userName}}</span>
            <i class="mdi mdi-chevron-down d-none d-xl-inline-block"></i>
          </template>
          <!-- item-->
          <div class="dropdown-divider"></div>
          <a class="dropdown-item text-danger" @click.stop="handleLogout" style="cursor:pointer !important;">
            <i class="ri-shut-down-line align-middle mr-1 text-danger"></i>
            {{ $t('topbar.profile.logout.text') }}
          </a>
        </b-dropdown>

        <!-- 右边侧边栏开关 -->
        <div class="dropdown d-inline-block">
          <button
            type="button"
            class="btn header-item noti-icon right-bar-toggle waves-effect toggle-right"
            @click="toggleRightSidebar"
          >
            <i class="ri-settings-2-line toggle-right"></i>
          </button>
        </div>
      </div>
    </div>
  </header>
</template>

<style lang="scss" scoped>
.notify-item {
  .active {
    color: #16181b;
    background-color: #f8f9fa;
  }
}

</style>