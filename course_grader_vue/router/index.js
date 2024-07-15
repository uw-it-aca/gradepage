import { createWebHistory, createRouter } from "vue-router";

// vue-gtag-next track routing
// import { trackRouter } from "vue-gtag-next";

// page components
import Chooser from "@/pages/chooser.vue";
import Section from "@/pages/section.vue";

const routes = [
  {
    path: "/",
    name: "Chooser",
    component: Chooser,
  },
  {
    path: "/section",
    name: "Section",
    component: Section,
    pathToRegexpOptions: { strict: true },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// add router tracking to vue-gtag-next
// trackRouter(router);

export default router;
