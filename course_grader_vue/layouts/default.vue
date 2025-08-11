<!-- eslint-disable vue/no-v-html -->
<template>
  <!-- layout.vue: this is where you override the layout -->
  <STopbarNeo
    :app-name="appName"
    :app-root-url="appRootUrl"
    :page-title="pageTitle"
    :user-name="context.login_user"
    :sign-out-url="context.signout_url"
    :background-class="'bg-body'"
  >
    <template #settings>
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
      <SColorMode color-class="text-white" class="ms-2" />
    </template>

    <template #navigation>
      <ul class="navbar-nav text-white me-auto mb-2 mb-xl-0">
        <li class="nav-item me-5">
          <BLink
            class="nav-link text-white px-0"
            :class="matchedTerm(currentTerm.id) ? 'active' : ''"
            :href="'/term/' + currentTerm.id"
          >
            {{ currentTerm.quarter }} {{ currentTerm.year }}
          </BLink>
        </li>
        <li class="nav-item dropdown">
          <a
            class="nav-link dropdown-toggle text-white px-0"
            :class="!matchedTerm(currentTerm.id) ? 'active' : ''"
            href="#"
            role="button"
            data-bs-toggle="dropdown"
            aria-expanded="false"
          >
            Previous Terms
          </a>
          <ul class="dropdown-menu">
            <template
              v-for="(term, index) in contextStore.context.terms"
              :key="index"
            >
              <li>
                <BDropdownItem v-if="index != 0"
                  ><BLink
                    class=""
                    :class="matchedTerm(term.id) ? 'bg-opacity-10' : ''"
                    :href="term.url"
                    >{{ term.quarter }} {{ term.year }}</BLink
                  ></BDropdownItem
                >
              </li>
            </template>
          </ul>
        </li>
      </ul>
    </template>

    <!-- TODO: hide system messages if empty -->
    <template v-if="window.gradepage.messages" #system>
      <div class="row">
        <div class="col">
          <ul
            class="list-unstyled py-2 m-0 text-center text-info-emphasis small"
          >
            <li
              v-for="(message, index) in window.gradepage.messages"
              :key="index"
              class="mb-2"
              v-html="message"
            ></li>
          </ul>
        </div>
      </div>
    </template>

    <template #main>
      <div class="row mt-2">
        <div class="col d-flex justify-content-end">
          <ul class="list-inline list-unstyled m-0">
            <li class="list-inline-item me-3">
              <BLink
                :href="helpURL"
                class="link-quiet-primary"
                target="_blank"
                rel="noopener"
              >
                <i class="bi bi-question-circle me-1"></i>GradePage Help</BLink
              >
            </li>
            <li class="list-inline-item">
              <BLink
                :href="codaURL"
                class="link-quiet-primary"
                target="_blank"
                rel="noopener"
                ><i class="bi bi-box-arrow-in-up-right me-1"></i>Course
                Dashboard</BLink
              >
            </li>
          </ul>
        </div>
      </div>
      <div class="row my-5">
        <div class="col">
          <slot name="content"></slot>
        </div>
      </div>
    </template>
    <template #footer></template>
  </STopbarNeo>
</template>

<script>
import { useContextStore } from "@/stores/context";
import { clearOverride } from "@/utils/data";
import { BLink, BDropdownItem } from "bootstrap-vue-next";
import { STopbarNeo, SProfile, SColorMode } from "solstice-vue";

export default {
  name: "GradepageApp",
  components: {
    BLink,
    BDropdownItem,
    STopbarNeo,
    SProfile,
    SColorMode,
  },
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
      selectedRoute: "Spring 2013",
      helpURL:
        "https://uwconnect.uw.edu/it?id=kb_article_view&sysparm_article=KB0034603",
      codaURL: "https://coda.uw.edu",
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
        .then((data) => {})
        .catch((error) => {})
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
