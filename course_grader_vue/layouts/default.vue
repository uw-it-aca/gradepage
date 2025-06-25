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
    <template #system>
      <div class="bg-info-subtle">
        <div class="container-xl text-center text-info-emphasis p-2">
          <ul class="list-unstyled m-0">
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
    <!--<template #navigation>navigation goes here</template>-->
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
      <SColorMode></SColorMode>
    </template>
    <!--<template #bar> <div class="border">message bar goes here</div> </template>-->
    <template #main>
      <div class="row mb-3">
        <div class="col">
          <ul class="list-inline m-0">
            <li class="list-inline-item py-2 me-4">
              <BLink
                class=""
                :class="matchedTerm(currentTerm.id) ? 'bg-opacity-10' : ''"
                :href="'/term/' + currentTerm.id"
              >
                <span
                  ><i class="bi bi-house-door-fill me-2"></i
                  >{{ currentTerm.quarter }} {{ currentTerm.year }}</span
                >
              </BLink>
            </li>
            <li class="list-inline-item py-2">
              <BDropdown variant="link-primary border-0 p-0" class="m-0">
                <template #button-content>
                  <i class="bi bi-calendar3 me-2"></i>Previous Terms
                </template>
                <template
                  v-for="(term, index) in contextStore.context.terms"
                  :key="index"
                >
                  <BDropdownItem v-if="index != 0"
                    ><BLink
                      class=""
                      :class="matchedTerm(term.id) ? 'bg-opacity-10' : ''"
                      :href="term.url"
                      >{{ term.quarter }} {{ term.year }}</BLink
                    ></BDropdownItem
                  >
                </template>
              </BDropdown>
            </li>
          </ul>
        </div>
      </div>


      <div class="row">
        <div class="col d-flex justify-content-between">
          <ul class="list-inline list-unstyled m-0">
            <li class="list-inline-item me-3">
              <BLink
                href="https://itconnect.uw.edu/learn/tools/gradepage/assign-submit-grades/"
                class="link-quiet-primary"
                target="_blank"
              >
                <i class="bi bi-question-circle me-1"></i>GradePage Help</BLink
              >
            </li>
            <li class="list-inline-item">
              <BLink
                href="https://coda.uw.edu"
                class="link-quiet-primary"
                target="_blank"
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
    <!--<template #aside></template>-->
    <template #footer></template>
  </STopbar>
</template>

<script>
import { useContextStore } from "@/stores/context";
import { clearOverride } from "@/utils/data";
import { BLink, BDropdown, BDropdownItem, BButton } from "bootstrap-vue-next";
import { STopbar, SProfile, SColorMode } from "solstice-vue";

export default {
  name: "GradepageApp",
  components: { BLink, BButton, STopbar, SProfile, SColorMode },
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
      blah: false,
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
    toggleDropdown() {
      console.log("lsakjdfa");
      this.blah = !this.blah;
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
