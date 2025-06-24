<template>
  <div class="mb-3 d-flex">
    <div>{{ selectedTermName }}</div>
    <div class="w-25">
      <select
        v-model="selectedTerm.url"
        aria-label="Select term"
        class="form-select"
        @change="selectTerm"
      >
        <template v-for="term in contextStore.context.terms" :key="term.id">
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
  </div>
</template>

<script>
import { useContextStore } from "@/stores/context";
//import { getSections } from "@/utils/data";

export default {
  name: "TermPage",
  components: {},
  setup() {
    const contextStore = useContextStore();
    return {
      contextStore,
      //getSections,
    };
  },
  data() {
    return {
      //isLoading: true,
      //currentTerm: this.contextStore.context.terms[0],
      selectedTerm: null,
      //selectedTermText: this.contextStore.context.page_title,
      //sectionsURL: this.contextStore.context.sections_url,
      //errorResponse: null,
      //sections: [],
    };
  },
  computed: {
    selectedTermName() {
      return this.selectedTerm.quarter + " " + this.selectedTerm.year;
    },
    /*
    isCurrentTermDisplay() {
      return (
        this.currentTerm.quarter === this.selectedTerm.quarter &&
        this.currentTerm.year === this.selectedTerm.year
      );
    },*/
  },
  created() {
    this.updateTerm();
    //this.loadSectionsForTerm();
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

    /*
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
      }, 2000);
    },*/
  },
};
</script>
