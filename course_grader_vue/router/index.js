import { createWebHistory, createRouter } from "vue-router";

// vue-gtag-next track routing
// import { trackRouter } from "vue-gtag-next";

// page components
import Term from "@/pages/term.vue";
import Section from "@/pages/section.vue";

const routes = [
  {
    path: "/",
    component: Term,
    props: true,
  },
  {
    path: "/term/:id?",
    component: Term,
    pathToRegexpOptions: { strict: true },
    props: true,
  },
  {
    path: "/section/:id?",
    name: Section,
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
