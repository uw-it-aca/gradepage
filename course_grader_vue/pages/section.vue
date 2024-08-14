<template>
  <Layout :page-title="pageTitle">
    <template #content>

      <BLink :href="section.term_url" :variant="'dark'" class="link-dark link-opacity-75 link-opacity-75-hover link-underline-opacity-50 link-underline-opacity-75-hover">
        Back To {{ section.section_year }} {{ section.section_quarter }}
      </BLink>

      <GradeRoster
        v-if="graderoster"
        :section="section"
        :graderoster="graderoster"
        :unsubmitted="unsubmitted"
      ></GradeRoster>
      <div v-else>Graderoster errors go here</div>
    </template>
  </Layout>
</template>

<script>
import Layout from "@/layouts/default.vue";
import GradeRoster from "@/components/graderoster.vue";
import { getSection, getGraderoster } from "@/utils/data";
import { BLink } from "bootstrap-vue-next";

export default {
  components: {
    Layout,
    GradeRoster,
    BLink
  },
  setup() {
    return {
      getSection,
      getGraderoster,
    };
  },
  data() {
    return {
      isLoading: true,
      section: {},
      graderoster: {},
      unsubmitted: 0,
      pageTitle: "Course Section",
    };
  },
  methods: {
    loadGraderoster: function () {
      if (this.section.graderoster_url) {
        this.getGraderoster(this.section.graderoster_url)
          .then((response) => {
            return response.data;
          })
          .then((data) => {
            this.graderoster = data.graderoster;
            this.unsubmitted = this.graderoster.students.filter(
              s => s.grade_url !== null).length;
          })
          .catch((error) => {
            console.log(error.message);
          })
          .finally(() => {
            this.isLoading = false;
          });
      } else {
        this.isLoading = false;
      }
    },
    loadSection: function () {
      let section_id = this.$route.params.id;
      this.getSection("/api/v1/section/" + section_id)
        .then((response) => {
          return response.data;
        })
        .then((data) => {
          this.section = data.section;
          this.loadGraderoster();
        })
        .catch((error) => {
          console.log(error.message);
          this.isLoading = false;
        })
        .finally(() => {
          this.pageTitle = this.section.section_name;
          document.title = this.pageTitle + " - GradePage";
        });
    },
  },
  created() {
    this.loadSection();
  },
};
</script>
