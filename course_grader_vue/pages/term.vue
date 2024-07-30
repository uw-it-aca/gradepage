<template>
  <Layout :page-title="selectedTermText">
    <template #content>
      <div>
        <select
          aria-label="Select term"
          @change="selectTerm"
          v-model="selectedTermUrl"
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

      <BCard class="shadow-sm rounded-3 my-4" header-class="p-3" header-bg-variant="transparent">
        <template #header>
          <h2 class="h6 m-0 fw-bold">Course Sections</h2>
        </template>
        <div v-if="isLoading">
          <ul class="list-unstyled">
            <li v-for="index in 10" class="mb-3">
              <div>
                <BPlaceholder
                  class="d-block bg-light-gray"
                  style="height: 60px;"
                  animation="glow"
                />
              </div>
            </li>
          </ul>
        </div>
        <div v-else>
          <div v-if="sections.length > 0">
            <SectionList :sections="sections"></SectionList>
          </div>
          <div v-else>
            You do not have any classes to grade for
            <strong>{{ selectedTermText }}</strong
            >. If you believe this to be incorrect, please contact your
            department's Time Schedule Coordinator.
          </div>
        </div>
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
      sections: [],
    };
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
          this.isLoading = false;
          this.sections = data.sections;
        });
    },
  },
  created() {
    this.updateTerm();

    setTimeout(() => {
      this.loadSectionsForTerm();
    }, 2000);
  },
};
</script>
