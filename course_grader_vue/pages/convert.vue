<template>
  <Layout :page-title="pageTitle">
    <template #content>

      <BCard
        class="shadow-sm rounded-3"
        header-class="p-3"
        header="Default"
      >

        <template #header>
          <SectionHeader :section="section" :title="TODO" />
        </template>

        ... Calculator ...

        <template #footer>

        </template>
      </BCard>
    </template>
  </Layout>
</template>

<script>
import {
  getSection,
} from "@/utils/data";
import Layout from "@/layouts/default.vue";
import SectionHeader from "@/components/section/header.vue";
import { BButton, BCard, BLink } from "bootstrap-vue-next";

export default {
  components: {
    Layout,
    SectionHeader,
    BButton,
    BCard,
    BLink,
  },
  setup() {
    return {
      getSection,
    };
  },
  data() {
    return {
      section: {},
      pageTitle: "Course Section",
      errorResponse: null,
    };
  },
  methods: {
    loadSection: function () {
      let section_id = this.$route.params.id;
      this.getSection("/api/v1/section/" + section_id)
        .then((response) => {
          return response.data;
        })
        .then((data) => {
          this.section = data.section;
          this.pageTitle = this.section.section_name;
          document.title = this.pageTitle + " - GradePage";
        })
        .catch((error) => {
          this.errorResponse = error.response;
        });
    },
  },
  created() {
    this.loadSection();
  },
};
</script>
