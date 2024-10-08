import { createApp } from "vue";
import { createBootstrap } from "bootstrap-vue-next";
import { createPinia } from "pinia";
import VueGtag from "vue-gtag-next";
import { Vue3Mq } from "vue3-mq";

// solstice-vue
// import SolsticeVue from "solstice-vue";

import App from "@/app.vue";
import router from "@/router";

// bootstrap js + bootstrap-icons
import "bootstrap";
import "bootstrap-icons/font/bootstrap-icons.css";

// solstice-vue
import "solstice-vue/dist/style.css";
import "solstice-vue/dist/solstice.scss";

// bootstrap-vue-next
// import "bootstrap/dist/css/bootstrap.css";
import "bootstrap-vue-next/dist/bootstrap-vue-next.css";

const app = createApp(App);
app.config.productionTip = false;
app.config.globalProperties.window = window
app.config.globalProperties.gettext = window.gettext;
app.config.globalProperties.ngettext = window.ngettext;
app.config.globalProperties.interpolate = window.interpolate;

// vue-gtag-next
const gaCode = document.body.getAttribute("data-google-analytics");
const debugMode = document.body.getAttribute("data-django-debug");

app.use(VueGtag, {
  isEnabled: debugMode == "false",
  property: {
    id: gaCode,
    params: {
      anonymize_ip: true,
      // user_id: 'provideSomeHashedId'
    },
  },
});

// vue-mq (media queries)
app.use(Vue3Mq, {
  preset: "bootstrap5",
});

// pinia (vuex) state management
const pinia = createPinia();
app.use(pinia);

// bootstrap-vue-next
app.use(createBootstrap());

// solstice-vue
// app.use(SolsticeVue);

// vue-router
app.use(router);

app.mount("#app");
