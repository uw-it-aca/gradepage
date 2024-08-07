<template>
  <Layout
    :page-title="selectedTermName"
    :term-url="isCurrentTermDisplay ? null : currentTerm.url"
  >
    <template #content>
      <div>
        <select
          aria-label="Select term"
          @change="selectTerm"
          v-model="selectedTerm.url"
        >
          <template
            v-for="term in this.contextStore.context.terms"
            :key="term.id"
          >
            <option
              :value="term.url"
              :title="`Select ${term.quarter} ${term.year}`"
              :selected="term.is_selected"
            >
              {{ term.quarter }} {{ term.year }}
            </option>
          </template>
        </select>
      </div>

      <BCard
        class="shadow-sm rounded-3 my-4"
        header-class="p-3"
        header-bg-variant="transparent"
      >
        <template #header>
          <div class="fs-6 m-0 fw-bold">{{ selectedTermName }}</div>
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
          <template v-if="sections.length > 0">
            <SectionList :sections="sections"></SectionList>
          </template>
          <div v-else>
            You do not have any classes to grade for
            <strong>{{ selectedTermName }}</strong
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
import SectionList from "@/components/section/list.vue";
import { useContextStore } from "@/stores/context";
import { getSections } from "@/utils/data";

export default {
  components: {
    Layout,
    SectionList,
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
      selectedTermUrl: "",
      selectedTermText: this.contextStore.context.page_title,
      sectionsURL: this.contextStore.context.sections_url,
      currentTerm: this.contextStore.context.terms[0],
      selectedTerm: null,
      sections: [],
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
  methods: {
    selectTerm: function (e) {
      this.contextStore.selectTerm(e.target.value);
      window.location.href = this.contextStore.context.terms.find(
        (t) => t.is_selected
      ).url;
    },
    updateTerm: function () {
      let term;
      if (this.$route.params.id) {
        term = this.contextStore.context.terms.find((t) =>
          t.sections_url.endsWith(this.$route.params.id)
        );
      }
      if (!term) {
        term = this.contextStore.context.terms[0];
      }
      this.selectedTerm = term;
    },
    loadSectionsForTerm: function () {
      this.getSections(this.selectedTerm.sections_url)
        .then((response) => {
          return response.data;
        })
        .then((data) => {
          this.sections = data.sections;
        })
        .catch((error) => {
          console.log(error.message);
        })
        .finally(() => {
          this.isLoading = false;
        });
    },
  },
  created() {
    setTimeout(() => {
      this.loadSectionsForTerm();
    }, "1000");

    this.updateTerm();
  },
};
</script>
