<template>
  <Layout
    :page-title="selectedTermName"
    :term-url="isCurrentTermDisplay ? null : currentTerm.url"
  >
    <template #content>
      <BCard
        class="shadow-sm rounded-3"
        header-class="p-3"
        header-bg-variant="transparent"
      >
        <template #header>
          <div class="fs-6 m-0 fw-bold">{{ selectedTermName }}</div>
        </template>
        <template v-if="isLoading">
          <ul class="list-unstyled">
            <li v-for="index in 10" :key="index" class="mb-3">
              <BPlaceholder
                class="d-block bg-body-secondary"
                style="height: 60px"
                animation="glow"
              />
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
                v-for="section in sections"
                :key="section.section_id"
                class="mb-3"
              >
                <PrimarySection :section="section"></PrimarySection>
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
      </BCard>
    </template>
  </Layout>
</template>

<script>
import Layout from "@/layouts/default.vue";
import PrimarySection from "@/components/section/primary.vue";
import Errors from "@/components/errors.vue";
import { useContextStore } from "@/stores/context";
import { getSections } from "@/utils/data";
import { BCard, BPlaceholder } from "bootstrap-vue-next";

export default {
  name: "TermPage",
  components: {
    Layout,
    PrimarySection,
    Errors,
    BCard,
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
      selectedTerm: null,
      errorResponse: null,
      sections: [],
    };
  },
  computed: {
    currentTerm() {
      return this.contextStore.context.terms[0];
    },
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
      this.getSections(this.selectedTerm.sections_url)
        .then((data) => {
          this.sections = data.sections;
        })
        .catch((error) => {
          this.errorResponse = error;
        })
        .finally(() => {
          this.isLoading = false;
        });
    },
  },
};
</script>
