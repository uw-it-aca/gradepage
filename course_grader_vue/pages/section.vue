<template>
  <Layout :page-title="section.section_name">
    <template #content>

      <BLink href="/">Back To Current Term </BLink>

      <BCard
        class="shadow-sm rounded-3 my-4"
        header-class="p-3"
        header-bg-variant="transparent"
      >
        <template #header>
          <h2 class="h6 m-0 fw-bold">{{ section.section_name }}</h2>
          <span> SLN {{ section.section_sln }}</span>
        </template>
        <template v-if="isLoading">
          <ul class="list-unstyled">
            <li v-for="index in 10" class="mb-3">
              <BPlaceholder
                class="d-block bg-light-gray"
                style="height: 60px"
                animation="glow"
              />
            </li>
          </ul>
        </template>
        <template v-else>
          <template v-if="graderoster.students.length > 0">
            <GradeRosterList :graderoster="graderoster"></GradeRosterList>
          </template>
        </template>
      </BCard>
    </template>
  </Layout>
</template>

<script>
import Layout from "@/layouts/default.vue";
import GradeRosterList from "@/components/graderoster/list.vue";
import { getSection, getGraderoster } from "@/utils/data";

export default {
  components: {
    Layout,
    GradeRosterList,
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
    };
  },
  methods: {
    loadGraderoster: function (url) {
      this.getGraderoster(url)
        .then((response) => {
          return response.data;
        })
        .then((data) => {
          this.isLoading = false;
          this.graderoster = data;
        })
        .catch((error) => {
          this.isLoading = false;
          console.log(error.message);
        });
    },
    loadSection: function () {
      let section_id = this.$route.params.id;
      this.getSection("/api/v1/section/" + section_id)
        .then((response) => {
          return response.data;
        })
        .then((data) => {
          this.section = data;
          if (this.section.graderoster_url) {
            this.loadGraderoster(this.section.graderoster_url);
          }

          // programatically update page title with section name
          document.title = this.section.section_name + " - GradePage";

        })
        .catch((error) => {
          this.isLoading = false;
          console.log(error.message);
        });
    },
  },
  computed: {

  },
  created() {
    this.loadSection();
  },
};
</script>
