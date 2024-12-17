import { defineStore } from "pinia";

export const useTokenStore = defineStore("token", {
  state: () => {
    return {
      name: "Vue",
      csrfToken: document.getElementsByName("csrfmiddlewaretoken")[0].value,
    };
  },
  getters: {},
  actions: {},
});
