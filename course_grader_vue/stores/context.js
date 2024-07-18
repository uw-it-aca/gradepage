import { defineStore } from "pinia";

export const useContextStore = defineStore({
  id: "django-context",
  state: () => {
    return {
      name: "Context",
      context: JSON.parse(
        document.getElementById("django-context-data").textContent
      ),
      messages: window.gradepage.messages,
      message_level: window.gradepage.message_level,
    };
  },
  getters: {},
  actions: {},
});
