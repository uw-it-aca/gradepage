<template>
  <Layout
    :page-title="selectedTermName"
    :term-url="isCurrentTermDisplay ? null : currentTerm.url"
  >
    <template #content>
      <h1 class="fs-1 fw-bold mb-4">{{ selectedTermName }}</h1>

      <template v-if="isLoading">
        <div role="status">
          <span class="visually-hidden">Loading courses...</span>
        </div>
        <ul class="list-unstyled" aria-hidden="true">
          <li
            v-for="index in 10"
            :key="index"
            class="border-bottom"
            :class="index == 1 ? 'pb-4 pt-0' : 'py-4'"
          >
            <div class="fs-4">
              <BPlaceholder
                animation="glow"
                cols="1"
                variant="secondary-subtle"
              />
            </div>
            <div class="fs-6">
              <BPlaceholder
                animation="glow"
                cols="2"
                variant="secondary-subtle"
              />
            </div>
          </li>
        </ul>
      </template>
      <template v-else-if="errorResponse">
        <Errors :error-response="errorResponse" />
      </template>
      <template v-else>
        <template v-if="sections.length > 0">
          <ul class="list-unstyled">
            <li
              v-for="(section, index) in sections"
              :key="section.section_id"
              class="border-bottom"
              :class="index == 0 ? 'pb-4 pt-0' : 'py-4'"
            >
              <PrimarySection
                :section="section"
                :timeout="index * base_timeout"
              ></PrimarySection>
            </li>
          </ul>
        </template>
        <div v-else>
          You do not have any classes to grade for
          <strong>{{ selectedTerm.quarter }} {{ selectedTerm.year }}</strong
          >. If you believe this to be incorrect, please contact your
          department's Time Schedule Coordinator.
        </div>
      </template>
    </template>
  </Layout>
</template>

<script>
import Layout from "@/layouts/default.vue";
import PrimarySection from "@/components/section/primary.vue";
import Errors from "@/components/errors.vue";
import { useContextStore } from "@/stores/context";
import { getSections } from "@/utils/data";
import { BPlaceholder } from "bootstrap-vue-next";

export default {
  name: "TermPage",
  components: {
    Layout,
    PrimarySection,
    Errors,
    BPlaceholder,
  },
  setup() {
    const contextStore = useContextStore();
    return {
      contextStore,
      getSections,
    };
  },
  data() {
    return {
      isLoading: true,
      currentTerm: this.contextStore.context.terms[0],
      selectedTerm: null,
      selectedTermText: this.contextStore.context.page_title,
      sectionsURL: this.contextStore.context.sections_url,
      errorResponse: null,
      sections: [],
      base_timeout: 500,
    };
  },
  computed: {
    selectedTermName() {
      return this.selectedTerm.quarter + " " + this.selectedTerm.year;
    },
    isCurrentTermDisplay() {
      return (
        this.currentTerm.quarter === this.selectedTerm.quarter &&
        this.currentTerm.year === this.selectedTerm.year
      );
    },
  },
  created() {
    this.updateTerm();
    this.loadSectionsForTerm();
  },
  methods: {
    selectTerm: function (e) {
      this.contextStore.selectTerm(e.target.value);
      window.location.href = this.contextStore.context.terms.find(
        (t) => t.is_selected
      ).url;
    },
    updateTerm: function () {
      var term;
      if (this.$route.params.id) {
        term = this.contextStore.context.terms.find((t) =>
          t.sections_url.endsWith(this.$route.params.id)
        );
      }
      if (!term) {
        term = this.currentTerm;
      }
      this.selectedTerm = term;
    },

    loadSectionsForTerm: function () {
      setTimeout(() => {
        this.getSections(this.selectedTerm.sections_url)
          .then((data) => {
            this.sections = data.sections;
          })
          .catch((error) => {
            this.errorResponse = error.data;
          })
          .finally(() => {
            this.isLoading = false;
          });
      }, 500);
    },
  },
};
</script>
