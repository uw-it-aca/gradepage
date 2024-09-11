<template>
  <!-- layout.vue: this is where you override the layout -->
  <STopbar
    :app-name="appName"
    :app-root-url="appRootUrl"
    :page-title="pageTitle"
    :user-name="userName"
    :sign-out-url="signOutUrl"
    :background-class="'bg-body-secondary'"
  >
    <template #navigation>
      <ul class="nav flex-column my-3">
        <li class="nav-item mb-1 bg-secondary bg-opacity-10 rounded-3">
          <BLink class="d-flex justify-content-between nav-link rounded-3 text-body chevron bg-secondary-hover bg-opacity-10-hover"
            exact-active-class="bg-secondary bg-opacity-10"
            href="/">
            <span><i class="bi bi-house-door-fill me-3"></i>Current</span>
          </BLink>
        </li>
        <li class="nav-item mb-1 position-relative">
          <BLink
            class="d-flex justify-content-between nav-link rounded-3 text-dark chevron bg-secondary-hover bg-opacity-10-hover"
            exact-active-class="bg-secondary bg-opacity-10"
            href="/term"
            id="gettingStartedHeading"
            data-bs-toggle="collapse"
            data-bs-target="#gettingStartedCollapse"
            :aria-expanded="
              $route.path.includes('/term') ? true : false
            "
            aria-controls="gettingStartedCollapse"
          >
            <span><i class="bi bi-calendar3 me-3"></i>Previous</span>
            <i class="bi bi-chevron-right" aria-hidden="true"></i>
          </BLink>
          <div
            id="gettingStartedCollapse"
            class="collapse"
            :class="$route.path.includes('/getting-started') ? 'show' : ''"
            aria-labelledby="gettingStartedHeading"
          >
            <ul class="nav flex-column small mt-1">
              <li class="nav-item mb-1">
                <BLink
                  class="ps-4 nav-link rounded-3 text-body fw-lighter bg-secondary-hover bg-opacity-10-hover"
                  style="--bs-text-opacity: 0.6"
                  exact-active-class="bg-secondary bg-opacity-10"
                  href="/term/2013-winter"
                  >Winter 2013</BLink
                >
              </li>
            </ul>
          </div>
        </li>
      </ul>
    </template>
    <template #profile>
      <SProfile
        v-if="userOverride != null"
        :user-netid="userName"
        :user-override="userOverride"
      >
        <button
          class="btn btn-link btn-sm text-danger p-0 m-0 border-0"
          value="Clear override"
          @click="clearUserOverride()"
        >
          Clear override
        </button>
      </SProfile>
      <SProfile v-else :user-netid="userName">
        <a :href="signOutUrl" class="text-white">Sign out</a>
      </SProfile>
    </template>
    <template #aside>
      <div class="my-3">
        <div class="bg-secondary bg-opacity-10 rounded-3 p-3">
          <div class="mb-2 text-dark">
            <i class="bi bi-exclamation-triangle-fill me-3"></i>System Messages
          </div>
          <ul class="list-unstyled m-0 text-dark small">
            <li
              v-for="(msg, index) in messages"
              :key="index"
              v-html="msg"
              class="mt-2"
            ></li>
          </ul>
        </div>
      </div>
    </template>
    <template #main>
      <div class="row justify-content-center my-3">
        <div class="col">
          <slot name="title">
            <h1 class="visually-hidden">{{ pageTitle }}</h1>
          </slot>
          {{ termUrl }}
          <div v-if="termUrl">
            <BLink :href="termUrl" title="Back to current quarter"
              >Back To Current Term
            </BLink>
          </div>

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
import { BAlert, BLink } from "bootstrap-vue-next";
import { STopbar, SProfile } from "solstice-vue";

export default {
  name: "GradepageApp",
  components: { BAlert, BLink, STopbar, SProfile },
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
    let context = this.contextStore.context,
      appName = "GradePage";
    return {
      appName: appName,
      appRootUrl: "/",
      userName: context.login_user,
      userFullName: context.user_fullname,
      userOverride: context.override_user,
      clearOverrideUrl: context.clear_override_url,
      signOutUrl: context.signout_url,
      messages: window.gradepage.messages,
      messageLevel: window.gradepage.message_level,
    };
  },
  created: function () {
    // constructs page title in the following format "Page Title - AppName"
    document.title = this.pageTitle + " - " + this.appName;
  },
  methods: {
    clearUserOverride: function () {
      this.clearOverride(this.clearOverrideUrl).then(() => {
        window.location.href = this.clearOverrideUrl;
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
