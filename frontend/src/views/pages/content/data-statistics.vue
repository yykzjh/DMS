<template>
  <div>
      <PageHeader :title="title" :items="items" />
      <div>
        DataStatistics
      </div>
  </div>
</template>

<script>

import PageHeader from "@/components/page-header";

export default {
  data() {
    return {
      title: "Data Statistics",
      items:[
        {
          text: "DMS"
        },
        {
          text: "首页"
        },
        {
          text: "数据统计",
          active: true
        }
      ]
    }
  },
  components: {
    PageHeader
  }
}
</script>

<style>

</style>