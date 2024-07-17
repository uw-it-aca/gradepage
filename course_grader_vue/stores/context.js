import { defineStore } from "pinia";

export const useContextStore = defineStore({
  id: "django-context",
  state: () => {
    console.log(document.getElementById("django-context-data").textContent);
    return {
      name: "Context",
      context: JSON.parse(
        document.getElementById("django-context-data").textContent
      ),
      messages: {},
    };
  },
  getters: {},
  actions: {},
});
