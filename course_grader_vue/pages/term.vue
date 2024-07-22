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
      sections: [],
    };
  },
  methods: {
    loadSectionsForTerm: function () {
      let url = this.contextStore.context.sections_url;
      this.getSections(url).then(response => {
        return response.data;
      }).then(data => {
        this.sections = data.sections;
      })
    },
  },
  mounted() {
    this.loadSectionsForTerm();
  },
};
</script>
