<template>
  <!-- layout.vue: this is where you override the layout -->
  <axdd-topbar
    :app-name="appName"
    :app-root-url="appRootUrl"
    :page-title="pageTitle"
    :user-name="userName"
    :sign-out-url="signOutUrl"
    :background-class="'bg-body-secondary'"
  >
    <template #navigation>
      <ul class="nav flex-column my-3">
        <li class="nav-item mb-1 bg-black bg-opacity-10 rounded-3">
          <a href="#" class="nav-link text-purple d-block px-3 py-2"
            ><i class="bi bi-house-door-fill me-3"></i>Home</a
          >
        </li>
        <li class="nav-item mb-1 position-relative">
          <router-link
            class="d-flex justify-content-between nav-link rounded-3 text-dark chevron bg-black-hover bg-opacity-10-hover"
            exact-active-class="bg-black bg-opacity-10"
            to="/getting-started/"
            id="gettingStartedHeading"
            data-bs-toggle="collapse"
            data-bs-target="#gettingStartedCollapse"
            :aria-expanded="
              $route.path.includes('/getting-started') ? true : false
            "
            aria-controls="gettingStartedCollapse"
          >
            <span><i class="bi bi-clock-fill me-3"></i>Previous</span>
            <i class="bi bi-chevron-right" aria-hidden="true"></i>
          </router-link>
          <div
            id="gettingStartedCollapse"
            class="collapse"
            :class="$route.path.includes('/getting-started') ? 'show' : ''"
            aria-labelledby="gettingStartedHeading"
          >
            <ul class="nav flex-column small mt-1">
              <li class="nav-item mb-1">
                <router-link
                  class="ps-5 nav-link rounded-3 text-dark fw-lighter bg-black-hover bg-opacity-10-hover"

                  exact-active-class="bg-black bg-opacity-10"
                  to="/getting-started/solstice-101"
                  >Winter 2013</router-link
                >
              </li>
              <li class="nav-item mb-1">
                <router-link
                  class="ps-5 nav-link rounded-3 text-dark fw-lighter bg-black-hover bg-opacity-10-hover"

                  exact-active-class="bg-black bg-opacity-10"
                  to="/getting-started/design-with-solstice"
                  >Fall 2012</router-link
                >
              </li>
              <li lass="nav-item">
                <router-link
                  class="ps-5 nav-link rounded-3 text-dark fw-lighter bg-black-hover bg-opacity-10-hover"

                  exact-active-class="bg-black bg-opacity-10"
                  to="/getting-started/installation-setup"
                  >Spring 2012</router-link
                >
              </li>
            </ul>
          </div>
        </li>
      </ul>
    </template>
    <template #profile>
      <axdd-profile
        v-if="userOverride != null"
        :user-netid="userName"
        :user-override="userOverride"
      >
        <button
          class="btn btn-link btn-sm text-danger p-0 m-0 border-0"
          value="Clear override"
          @click="clearUserOverride()"
        >
          Clear
        </button>
      </axdd-profile>
      <axdd-profile v-else :user-netid="userName">
        <a :href="signOutUrl" class="text-white">Sign out</a>
      </axdd-profile>
    </template>
    <template #aside>
      <div class="border border-danger">aside slot area</div>
    </template>
    <template #bar>
      <div class="border border-danger">bar slot area</div>
    </template>
    <template #main>
      <div class="row justify-content-center">
        <div class="col">
          <slot name="title">
            <h1 class="">{{ pageTitle }}</h1>
          </slot>
          <slot name="content"></slot>
        </div>
      </div>
    </template>
    <template #footer></template>
  </axdd-topbar>
</template>

<script>
import { useContextStore } from "@/stores/context";
import { clearOverride } from "@/utils/data";

export default {
  name: "GradepageApp",
  components: {},
  props: {
    pageTitle: {
      type: String,
      required: true,
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
      appName = "Gradepage";
    return {
      appName: appName,
      appRootUrl: "/",
      userName: context.login_user,
      userFullName: context.user_fullname,
      userOverride: context.override_user,
      clearOverrideUrl: context.clear_override_url,
      signOutUrl: context.signout_url,
      // pageTitle: context.page_title + " - " + appName,
    };
  },
  created: function () {
    // document.title = this.pageTitle;

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
