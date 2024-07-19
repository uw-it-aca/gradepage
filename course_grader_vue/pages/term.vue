// home.vue

<template>
  <Layout :page-title="pageTitle">
    <template #content>

      <h2>Section List</h2>
      <ul>
        <li>
          <a href="/section/2024-spring-ESS-101-A-51CAAF8E6A7D11D5A4AE0004AC494FFE">ESS 101 A</a>
          <ul>
            <li>ESS 101 AA</li>
            <li>ESS 101 AB</li>
          </ul>
        </li>
        <li>ESS 101 B
          <ul>
            <li>ESS 101 BA</li>
            <li>ESS 101 BB</li>
            <li>ESS 101 BC</li>
          </ul>
        </li>
        <li></li>
        <li></li>
        <li></li>
        <li></li>
      </ul>
    </template>
  </Layout>
</template>

<script>
import Layout from "@/layouts/default.vue";

export default {
  name: "PagesTerm",
  components: {
    Layout,
  },
  data() {
    return {
      pageTitle: "Summer 2024",
    };
  },
  methods: {},
};
</script>
