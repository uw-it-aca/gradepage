<template>
  <div class="fixed-bottom m-2 text-end">
    <BButton v-b-toggle.offcanvasFeedback size="sm">
      <i class="bi bi-chat-right-text-fill me-2"></i>Send us feedback
    </BButton>
  </div>
  <BOffcanvas
    id="offcanvasFeedback"
    title="Send us feedback"
    shadow
    placement="end"
    body-class="p-0"
  >
    <div class="d-flex flex-column h-100">
      <iframe
        class="flex-fill flex-grow-1"
        width="640px"
        height="480px"
        src="https://forms.office.com/r/J5G809c0UT?embed=true"
        frameborder="0"
        marginwidth="0"
        marginheight="0"
        style="border: none; max-width: 100%; max-height: 100vh"
        allowfullscreen
        webkitallowfullscreen
        mozallowfullscreen
        msallowfullscreen
      >
      </iframe>
    </div>
  </BOffcanvas>
</template>

<script>
  import { BButton, BOffcanvas } from "bootstrap-vue-next";
  import { vBToggle } from "bootstrap-vue-next/directives/BToggle";

  export default {
    name: "Feedback",
    components: {
      BButton,
      BOffcanvas,
    },
    directives: {
      "b-toggle": vBToggle,
    },
    setup() {
      return {};
    },
  };
</script>
