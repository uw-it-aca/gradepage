import { defineStore } from "pinia";

export const useContextStore = defineStore({
  id: "django-context",
  state: () => {
    return {
      name: "Context",
      context: JSON.parse(
        document.getElementById("django-context-data").textContent
      ),
      messages: JSON.parse(
        document.getElementById("persistent-message-data").textContent
      ),
    };
  },
  getters: {},
  actions: {},
});
