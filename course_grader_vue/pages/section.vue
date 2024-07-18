// home.vue

<template>
  <Layout :page-title="pageTitle">
    <template #content>
      <h2>Section Info</h2>

      <h3>Grade Roster</h3>
      <ul>
        <li>Philip Tucker</li>
        <li>Garrett Brock</li>
        <li>Birdie Welch</li>
        <li>Mae Williamson</li>
        <li>Nell Simmons</li>
        <li>Lucinda Mendez</li>
      </ul>
    </template>
  </Layout>
</template>

<script>
import Layout from "@/layouts/default.vue";

export default {
  name: "PagesHome",
  components: {
    Layout,
  },
  data() {
    return {
      pageTitle: "Gesadfasdtting started",
    };
  },
  methods: {},
};
</script>
