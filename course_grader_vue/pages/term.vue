<template>
  <layout :page-title="selectedTermText">
    <template #content>
      <div>
        <select
          aria-label="Select term"
          @change="selectTerm"
          v-model="selectedTermUrl"
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
          You do not have any classes to grade for <strong>{{ selectedTermText }}</strong
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
      selectedTermUrl: "",
      selectedTermText: this.contextStore.context.page_title,
      sectionsURL: this.contextStore.context.sections_url,
      sections: [],
    };
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
      this.selectedTermUrl = term.url;
      this.selectedTermText = term.quarter + " " + term.year;
      this.sectionsURL = term.sections_url;
    },
    loadSectionsForTerm: function () {
      this.getSections(this.sectionsURL)
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
