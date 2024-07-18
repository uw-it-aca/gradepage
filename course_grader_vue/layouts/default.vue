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
      <ul class="text-white">
        <li>Summer 2024</li>
        <li>Spring 2024</li>
        <li>Winter 2024</li>
        <li>Autumn 2023</li>
        <li>Summer 2023</li>
      </ul>
    </template>
    <template #aside>
     asfdasfdasfd
    </template>
    <template #main>
      <slot name="title">
        <h1 class="">{{ pageTitle }}</h1>
      </slot>
      <slot name="content"></slot>
    </template>
    <template #footer></template>
  </axdd-sidebar>

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
      userName: context.user_login,
      userFullName: context.user_fullname,
      userOverride: context.override_user,
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
      this.clearOverride().then(() => {
        window.location.href = "/support";
      });
    },
  },
};
</script>
