<!-- eslint-disable vue/no-v-html -->
<template>
  <!-- layout.vue: this is where you override the layout -->
  <STopbar
    :app-name="appName"
    :app-root-url="appRootUrl"
    :page-title="pageTitle"
    :user-name="context.login_user"
    :sign-out-url="context.signout_url"
    :background-class="'bg-body'"
  >
    <template #navigation>
      <ul class="nav flex-column my-3">
        <li class="nav-item mb-1 position-relative">
          <BLink
            class="d-flex justify-content-between nav-link rounded-3 text-body chevron bg-secondary-hover bg-opacity-10-hover"
            :class="
              matchedTerm(currentTerm.id) ? 'bg-secondary bg-opacity-10' : ''
            "
            :href="'/term/' + currentTerm.id"
          >
            <span
              ><i class="bi bi-house-door-fill me-3"></i
              >{{ currentTerm.quarter }} {{ currentTerm.year }}</span
            >
          </BLink>
        </li>
        <li class="nav-item mb-1 position-relative">
          <BLink
            id="gettingStartedHeading"
            class="d-flex justify-content-between nav-link rounded-3 text-body chevron bg-secondary-hover bg-opacity-10-hover"
            data-bs-toggle="collapse"
            data-bs-target="#gettingStartedCollapse"
            :aria-expanded="matchedTerm(currentTerm.id) ? false : true"
            aria-controls="gettingStartedCollapse"
          >
            <span><i class="bi bi-calendar3 me-3"></i>Previous terms</span>
            <i class="bi bi-chevron-right" aria-hidden="true"></i>
          </BLink>
          <div
            id="gettingStartedCollapse"
            class="collapse"
            :class="matchedTerm(currentTerm.id) ? '' : 'show'"
            aria-labelledby="gettingStartedHeading"
          >
            <ul class="nav flex-column small mt-1">
              <li
                v-for="(term, index) in contextStore.context.terms"
                :key="index"
                class="nav-item mb-1"
              >
                <BLink
                  v-if="index != 0"
                  class="ps-4 nav-link rounded-3 text-body fw-lighter bg-secondary-hover bg-opacity-10-hover"
                  :class="
                    matchedTerm(term.id) ? 'bg-secondary bg-opacity-10' : ''
                  "
                  :href="term.url"
                  >{{ term.quarter }} {{ term.year }}</BLink
                >
              </li>
            </ul>
          </div>
        </li>
      </ul>
    </template>
    <template #profile>
      <SProfile
        v-if="context.override_user != null"
        :user-netid="context.login_user"
        :user-override="context.override_user"
      >
        <button
          class="btn btn-link btn-sm text-danger p-0 m-0 border-0"
          value="Clear override"
          @click="clearUserOverride()"
        >
          Clear override
        </button>
      </SProfile>
      <SProfile v-else :user-netid="context.login_user">
        <a :href="context.signout_url" class="text-white"> Sign out </a>
      </SProfile>
    </template>
    <template #aside>
      <div class="my-3">
        <div class="bg-body-tertiary rounded-3 p-3">
          <div class="mb-2 text-body">
            <i class="bi bi-exclamation-triangle-fill me-3"></i>
            Grading Period Status
          </div>
          <ul class="list-unstyled m-0 text-body small">
            <li
              v-for="(message, index) in window.gradepage.messages"
              :key="index"
              class="mt-2"
              v-html="message"
            ></li>
          </ul>
        </div>
        <SColorMode></SColorMode>
      </div>
    </template>
    <template #main>
      <div class="row justify-content-center my-3">
        <div class="col">
          <slot name="title">
            <h1>{{ pageTitle }}</h1>
          </slot>
          <slot name="content"></slot>
        </div>
      </div>
    </template>
    <template #footer></template>
  </STopbar>
</template>

<script>
import { useContextStore } from "@/stores/context";
import { clearOverride } from "@/utils/data";
import { BLink } from "bootstrap-vue-next";
import { STopbar, SProfile, SColorMode } from "solstice-vue";

export default {
  name: "GradepageApp",
  components: { BLink, STopbar, SProfile, SColorMode },
  props: {
    pageTitle: {
      type: String,
      required: true,
    },
    termUrl: {
      type: String,
      default: null,
    },
  },
  setup() {
    const contextStore = useContextStore();
    return {
      contextStore,
      clearOverride,
    };
  },
  data() {
    return {
      appName: "GradePage",
      appRootUrl: "/",
    };
  },
  computed: {
    context() {
      return this.contextStore.context;
    },
    currentTerm() {
      return this.contextStore.context.terms[0];
    },
  },
  created: function () {
    // constructs page title in the following format "Page Title - AppName"
    document.title = this.pageTitle + " - " + this.appName;
  },
  methods: {
    matchedTerm: function (id) {
      return (
        this.$route.path.includes("/term/" + id) ||
        this.$route.path.includes("/section/" + id)
      );
    },
    clearUserOverride: function () {
      this.clearOverride(this.context.clear_override_url)
        .then((data) => {
        })
        .catch((error) => {
        })
        .finally(() => {
          window.location.href = this.context.clear_override_url;
        });
    },
  },
};
</script>

<style lang="scss" scoped>
.chevron .bi-chevron-right {
  display: inline-block;
  transition: transform 0.35s ease;
  transform-origin: 0.5em 50%;
  font-weight: bolder;
}

.chevron[aria-expanded="true"] .bi-chevron-right {
  transform: rotate(90deg);
}

.bi-chevron-right::after {
  font-weight: bolder !important;
}
</style>
