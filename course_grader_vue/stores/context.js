import { defineStore } from "pinia";

export const useContextStore = defineStore({
  id: "django-context",
  state: () => {
    return {
      name: "Context",
      context: JSON.parse(
        document.getElementById("django-context-data").textContent
      ),
    };
  },
  getters: {},
  actions: {
    selectTerm (url) {
      this.context.terms.forEach((term) => {
        term.is_selected = (term.url === url) ? true : false;
      });
    },
  },
});
