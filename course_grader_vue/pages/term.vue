<template>
  <layout :page-title="selectedTermName">
    <template #content>
      <div>
        <div v-if="!isCurrentTermDisplay">
          <a :href="currentTerm.url" title="Back to current quarter">
            Back to current quarter
          </a>
        </div>
        <select
          aria-label="Select term"
          @change="selectTerm"
          v-model="selectedTerm.url"
        >
          <template v-for="term in this.contextStore.context.terms" :key="term.id">
            <option
              :value="term.url"
              :title="`Select ${term.quarter} ${term.year}`"
              :selected="term.is_selected"
            >{{ term.quarter }} {{ term.year }}</option>
          </template>
        </select>
      </div>
      <div class="border">
        <div v-if="sections.length > 0">
          <section-list :sections="sections"></section-list>
        </div>
        <div v-else>
          You do not have any classes to grade for <strong>{{ selectedTermName }}</strong
          >. If you believe this to be incorrect, please contact your department's
          Time Schedule Coordinator.
          </div>
      </div>
    </template>
  </layout>
</template>

<script>
import Layout from "@/layouts/default.vue";
import SectionList from "@/components/section/list.vue";
import { useContextStore } from "@/stores/context";
import { getSections } from "@/utils/data";

export default {
  components: {
    layout: Layout,
    "section-list": SectionList,
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
      return (this.currentTerm.quarter === this.selectedTerm.quarter) &&
        (this.currentTerm.year === this.selectedTerm.year);
    },
  },
  methods: {
    selectTerm: function (e) {
      this.contextStore.selectTerm(e.target.value);
      window.location.href = this.contextStore.context.terms.find((t) =>
        t.is_selected).url;
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
        });
    },
  },
  created() {
    this.updateTerm();
    this.loadSectionsForTerm();
  },
};
</script>
