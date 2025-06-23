<template>
  <BCard bg-variant="body-tertiary" class="border-0">
    <h3 class="fs-4 ff-encode-sans">Helpful Links</h3>
    <ul class="list-unstyled m-0">
      <li>
        <BLink
          href="https://itconnect.uw.edu/learn/tools/gradepage/assign-submit-grades/"
          target="_blank"
          >GradePage Help</BLink
        >
      </li>
      <li>
        <BLink href="https://coda.uw.edu">Course Dashboard</BLink>
      </li>
    </ul>
  </BCard>
</template>

<script>
import { BCard, BLink } from "bootstrap-vue-next";

export default {
  components: {
    BCard,
    BLink,
  },
  data() {
    return {};
  },
};
</script>
