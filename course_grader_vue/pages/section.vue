<template>
  <Layout :page-title="pageTitle">
    <template #content>
      <BLink href="/">Back To Current Term </BLink>

      <BCard
        class="shadow-sm rounded-3 my-4"
        header-class="p-3"
        header="Default"
      >
        <template #header>
          <div class="">
            <div class="fs-5 text-muted fw-light">Grade Receipt for</div>
            <span class="fs-2 m-0 me-3">
              <BPlaceholder
                v-if="!section.section_name"
                class="bg-light-gray"
                width="15"
                animation="glow"
              />{{ section.section_name }}
            </span>
            <span class="small"
              >SLN
              <BPlaceholder
                v-if="!section.section_sln"
                class="bg-light-gray"
                width="5"
                animation="glow"
              />{{ section.section_sln }}</span
            >
          </div>
        </template>

        <div class="mb-2 small text-muted">
          Duplicate Code <i class="bi bi-circle-fill text-secondary"></i>
        </div>
        <GradeRoster
          v-if="graderoster"
          :graderoster="graderoster"
        ></GradeRoster>
        <div v-else>Graderoster not available</div>
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
  computed: {},
  created() {
    setTimeout(() => {
      this.loadSection();
    }, "1000");
  },
};
</script>
