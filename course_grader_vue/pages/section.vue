// home.vue

<template>
  <Layout :page-title="pageTitle">
    <template #content>
      <h2>Section Info</h2>
      <p>
        Lorem ipsum dolor sit, amet consectetur adipisicing elit. Neque libero
        laborum ratione et, blanditiis voluptas, odit exercitationem similique
        repellat quisquam non reprehenderit. Sequi, reprehenderit!
        Necessitatibus quod at illo nihil ipsam?
      </p>

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
  name: "PagesSection",
  components: {
    Layout,
  },
  data() {
    return {
      pageTitle: "ESS 101 A",
    };
  },
  methods: {},
};
</script>
