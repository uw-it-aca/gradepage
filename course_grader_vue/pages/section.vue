<template>
  <Layout :page-title="pageTitle">
    <template #content>
      <BLink href="/">Back To Current Term </BLink>

      <BCard
        class="shadow-sm rounded-3 my-4"
        header-class="p-3"
        header-bg-variant="transparent"
      >
        <template #header>
          <div class="fs-6 m-0 fw-bold">{{ section.section_name }}</div>
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
          <GradeRoster
            v-if="graderoster"
            :graderoster="graderoster"
          ></GradeRoster>
          <div v-else>Graderoster not available</div>
        </template>
      </BCard>
    </template>
  </Layout>
</template>

<script>
import Layout from "@/layouts/default.vue";
import GradeRoster from "@/components/graderoster/list.vue";
import { getSection, getGraderoster } from "@/utils/data";

export default {
  components: {
    Layout,
    GradeRoster,
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
      pageTitle: "Course Section",
    };
  },
  methods: {
    loadGraderoster: function (url) {
      this.getGraderoster(url)
        .then((response) => {
          return response.data;
        })
        .then((data) => {
          this.graderoster = data.graderoster;
        })
        .catch((error) => {
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
          this.section = data.section;
          if (this.section.graderoster_url) {
            this.loadGraderoster(this.section.graderoster_url);
          }
        })
        .catch((error) => {
          console.log(error.message);
        })
        .finally(() => {
          this.isLoading = false;
          this.pageTitle = this.section.section_name;
          document.title = this.pageTitle + " - GradePage";
        });
    },
  },
  computed: {

  },
  created() {
    setTimeout(() => {
      this.loadSection();
    }, "1000");


  },
};
</script>
