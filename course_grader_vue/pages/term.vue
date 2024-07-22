<template>
  <layout :page-title="pageTitle">
    <template #content>
      <div v-if="sections.length > 0">
        <section-list :sections="sections"></section-list>
      </div>
      <div v-else>
        You do not have any classes to grade for <strong>{{ pageTitle }}</strong>. If you believe this to be incorrect, please contact your department's Time Schedule Coordinator.
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
      pageTitle: this.contextStore.context.page_title,
      sectionsURL: this.contextStore.context.sections_url,
      sections: [],
    };
  },
  methods: {
    updateTerm: function () {
      let term;
      if (this.$route.params.id) {
        term = this.contextStore.context.terms.find(
            t => t.sections_url.endsWith(this.$route.params.id));
        if (term) {
          this.pageTitle = term.quarter + " " + term.year;
          this.sectionsURL = term.sections_url;
        }
      } else {
        this.pageTitle = this.contextStore.context.page_title;
        this.sectionsURL = this.contextStore.context.sections_url;
      }
    },
    loadSectionsForTerm: function () {
      this.getSections(this.sectionsURL).then(response => {
        return response.data;
      }).then(data => {
        this.sections = data.sections;
      })
    },
  },
  created() {
    this.updateTerm();
    this.loadSectionsForTerm();
  },
};
</script>
