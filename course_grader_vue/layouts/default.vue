<template>
 <!-- layout.vue: this is where you override the layout -->
 <axdd-sidebar
    :app-name="appName"
    :app-root-url="appRootUrl"
    :page-title="pageTitle"
    :user-name="userName"
    :sign-out-url="signOutUrl"
  >
    <template #profile>
      <axdd-profile
        v-if="userName != userOverride"
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
    <template #navigation>
      nav
    </template>
    <template #aside>
     asfdasfdasfd
    </template>
    <template #main>
      <slot name="title">
        <h1 class="visually-hidden">{{ pageTitle }}</h1>
      </slot>
      <slot name="content"></slot>
    </template>
    <template #footer></template>
  </axdd-sidebar>

</template>

<script>
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
    return {
      clearOverride,
    };
  },
  data() {
    return {
      // minimum application setup overrides
      appName: "Gradepage",
      appRootUrl: "/",
      userName: "asdf",
      userOverride: "asdfaasdasdf",
      signOutUrl: "/sadfasdfasd",
      userRoles: "asdfafsd",
      // automatically set year
      currentYear: new Date().getFullYear(),
    };
  },
  created: function () {
    // constructs page title in the following format "Page Title - AppName"
    document.title = this.pageTitle + " - " + this.appName;
  },
};
</script>
