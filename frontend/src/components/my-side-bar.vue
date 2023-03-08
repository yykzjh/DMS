<script>
import simplebar from "simplebar-vue";
import { layoutComputed } from "@/state/helpers";

import { menuItems } from "./my-menu";

export default {
  components: {
    simplebar,
  },
  props: {
    isCondensed: {
      type: Boolean,
      default: false,
    },
    type: {
      type: String,
      required: true,
    },
    width: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      menuItems: menuItems,
      currentPath:""
    };
  },
  computed: {
    ...layoutComputed,
  },
  methods: {
    /**
     * Returns true or false if given menu item has child or not
     * @param item menuItem
     */
    hasItems(item) {
      return item.subItems !== undefined ? item.subItems.length > 0 : false;
    },
    filterItems(navigateItems) {
      return navigateItems.filter((item) => {
        if (item.id == 1) return this.$store.state.auth.currentUser.permissions.indexOf(10)!=-1
        else if(item.id == 5) return this.$store.state.auth.currentUser.permissions.indexOf(20)!=-1
        else if(item.id == 6) return this.$store.state.auth.currentUser.permissions.indexOf(40)!=-1
        else if(item.id == 11) return this.$store.state.auth.currentUser.permissions.indexOf(50)!=-1
        else if(item.id == 14) return this.$store.state.auth.currentUser.permissions.indexOf(60)!=-1
        else if(item.id == 17) return this.$store.state.auth.currentUser.permissions.indexOf(70)!=-1
        else if(item.id == 18) return this.$store.state.auth.currentUser.permissions.indexOf(80)!=-1
        else if(item.id == 7 || item.id == 9) return this.$store.state.auth.currentUser.permissions.indexOf(41)!=-1
        else if(item.id == 8 || item.id == 10) return this.$store.state.auth.currentUser.permissions.indexOf(42)!=-1
        else return true
      })
    }
  },
  watch: {
    type: {
      immediate: true,
      handler(newVal, oldVal) {
        if (newVal !== oldVal) {
          switch (newVal) {
            case "dark":
              document.body.setAttribute("data-sidebar", "dark");
              document.body.removeAttribute("data-topbar");
              document.body.removeAttribute("data-sidebar-size");
              break;
            case "light":
              document.body.setAttribute("data-topbar", "dark");
              document.body.removeAttribute("data-sidebar");
              document.body.removeAttribute("data-sidebar-size");
              document.body.classList.remove("vertical-collpsed");
              break;
            case "compact":
              document.body.setAttribute("data-sidebar-size", "small");
              document.body.setAttribute("data-sidebar", "dark");
              document.body.classList.remove("vertical-collpsed");
              document.body.removeAttribute("data-topbar", "dark");
              break;
            case "icon":
              document.body.setAttribute("data-keep-enlarged", "true");
              document.body.classList.add("vertical-collpsed");
              document.body.setAttribute("data-sidebar", "dark");
              document.body.removeAttribute("data-topbar", "dark");
              break;
            case "colored":
              document.body.setAttribute("data-sidebar", "colored");
              document.body.removeAttribute("data-keep-enlarged");
              document.body.classList.remove("vertical-collpsed");
              document.body.removeAttribute("data-sidebar-size");
              break;
            default:
              document.body.setAttribute("data-sidebar", "dark");
              break;
          }
        }
      },
    },
    width: {
      immediate: true,
      handler(newVal, oldVal) {
        if (newVal !== oldVal) {
          switch (newVal) {
            case "boxed":
              document.body.setAttribute("data-layout-size", "boxed");
              break;
            case "fluid":
              document.body.setAttribute("data-layout-mode", "fluid");
              document.body.removeAttribute("data-layout-size");
              break;
            default:
              document.body.setAttribute("data-layout-mode", "fluid");
              break;
          }
        }
      },
    },
  },
};
</script>

<template>
  <div class="vertical-menu">
    <div id="sidebar-menu">
      <el-menu
        :unique-opened="true"
        :collapse-transition="true"
        background-color="transparent"
      >
        <li v-for="item in filterItems(menuItems)" :key="item.id">
          <el-submenu
            v-if="hasItems(item)"
            :index="$t(item.label)"
          >
            <template
              :slot="'title'"
            >
             <div style="line-height:36px !important;">
                <i :class="`bx ${item.icon}`" v-if="item.icon" style=""></i>
                <span>{{ $t(item.label) }}</span>
                <span
                  :class="`badge badge-pill badge-${item.badge.variant} float-right`"
                  v-if="item.badge"
                >
                  {{ $t(item.badge.text) }}
                </span>
             </div>
            </template>

            <li v-for="(subitem, index) in filterItems(item.subItems)" :key="index">
              <el-submenu
                v-if="hasItems(subitem)"
                :index="$t(subitem.label)"
              >
                <template
                  :slot="'title'"
                >
                  <div class="sub-navigate">
                    <i :class="`bx ${subitem.icon}`" v-if="subitem.icon"></i>
                    <span>{{ $t(subitem.label) }}</span>
                    <span
                      :class="`badge badge-pill badge-${subitem.badge.variant} float-right`"
                      v-if="subitem.badge"
                    >
                      {{ $t(subitem.badge.text) }}
                    </span>
                  </div>
                </template>

                <li v-for="(subSubitem, index) in filterItems(subitem.subItems)" :key="index">
                  <router-link
                    :to="subSubitem.link"
                    class="sub-sub-navigate"
                  >
                    <i :class="`bx ${subSubitem.icon}`" v-if="subSubitem.icon"></i>
                    <span>{{ $t(subSubitem.label) }}</span>
                    <span
                      :class="`badge badge-pill badge-${subSubitem.badge.variant} float-right`"
                      v-if="subSubitem.badge"
                    >
                      {{ $t(subSubitem.badge.text) }}
                    </span>
                  </router-link>
                </li>

              </el-submenu>
              <router-link
                :to="subitem.link"
                v-if="!hasItems(subitem)"
                class="sub-navigate"
              >
                <i :class="`bx ${subitem.icon}`" v-if="subitem.icon"></i>
                <span>{{ $t(subitem.label) }}</span>
                <span
                  :class="`badge badge-pill badge-${subitem.badge.variant} float-right`"
                  v-if="subitem.badge"
                >
                  {{ $t(subitem.badge.text) }}
                </span>
              </router-link>
            </li>
          
          </el-submenu>
          <router-link
            :to="item.link"
            v-if="!hasItems(item)"
            style="line-height:36px !important;"
          >
            <i :class="`bx ${item.icon}`" v-if="item.icon"></i>
            <span>{{ $t(item.label) }}</span>
            <span
              :class="`badge badge-pill badge-${item.badge.variant} float-right`"
              v-if="item.badge"
              >{{ $t(item.badge.text) }}</span
            >
          </router-link>
        </li>
      </el-menu>
    </div>
  </div>
</template>

<style lang="scss">
  .el-submenu__title {
    padding: 0.625rem 1.5rem !important;
    color: #8590a5;
    font-size: 15px;

    i{
      display: inline-block;
      min-width: 1.5rem;
      padding-bottom: 0.125em;
      font-size: 1.1rem;
      line-height: 1.40625rem;
      vertical-align: middle !important;
      transition: all 0.4s;
      opacity: 0.75;
    }
  }

  #sidebar-menu {
    padding: 10px 0 30px 0;
  }
  .is-opened .el-submenu__title span {
    color: #d7e4ec !important;
  }
  .router-link-exact-active span {
    color: #d7e4ec !important;
  }
  .sub-navigate {
    padding: 0.625rem 3rem !important;
  }
  .sub-sub-navigate {
    padding-left: 40px;
  }
</style>

