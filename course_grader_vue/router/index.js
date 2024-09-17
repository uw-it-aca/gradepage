import { createWebHistory, createRouter } from "vue-router";
import { setActivePinia, createPinia } from 'pinia';

// pinia setup to get current term id from context store
setActivePinia(createPinia());
import { useContextStore } from "@/stores/context";

// access the context store
const contextStore = useContextStore();
const currentTermUrl = contextStore.context.terms[0].url;
console.log(currentTermUrl);

// vue-gtag-next track routing
// import { trackRouter } from "vue-gtag-next";

// page components
import Term from "@/pages/term.vue";
import Section from "@/pages/section.vue";

const routes = [
  {
    path: "/",
    //component: Term,
    //props: true,
    path: "/",
    redirect: currentTermUrl,
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
