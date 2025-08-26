<template>
  <template v-if="errorResponse.status === 404">
    <div id="404-error">
      <h1 class="fs-1 fw-bold">Error 404</h1>
      <p>{{ errorText }}</p>
      <p>Some things you may want to try:</p>
      <ul>
        <li>
          Make sure you are logged into this service with the appropriate UW
          NetID.
        </li>
        <li>
          Feel free to contact us at help@uw.edu if you have questions or need
          help.
        </li>
      </ul>
    </div>
  </template>
  <template v-else-if="errorResponse.status === 401">
    <div id="401-error">
      <h1 class="fs-1 fw-bold">Error 401</h1>
      <p>{{ errorText }}</p>
      <p>Some things you may want to try:</p>
      <ul>
        <li>
          Make sure you are logged into this service with the appropriate UW
          NetID.
        </li>
        <li>
          Feel free to contact us at help@uw.edu if you have questions or need
          help.
        </li>
      </ul>
    </div>
  </template>
  <template v-else-if="errorResponse.status === 500">
    <div id="500-error">
      <h1 class="fs-1 fw-bold">Error 500</h1>
      <h2>There was a problem retrieving grade information:</h2>
      <p>{{ errorText }}</p>

      <p>
        The Gradepage support team has been alerted of this issue and are
        working to get you back on track.
      </p>
      <p>You may want to:</p>
      <ul>
        <li>Give us a little time, and try again later.</li>
        <li>
          Drop us a line at <a href="mailto:help@uw.edu">help@uw.edu</a> and let
          us know that this has been taking awhile.
        </li>
      </ul>
    </div>
  </template>
  <template v-else>
    <div id="543-error">
      <h1 class="fs-1 fw-bold">Error 543</h1>
      <h2>There was a problem retrieving grade information:</h2>
      <p>{{ errorText }}</p>

      <p>
        To correct this issue,
        <strong
          >please email us at
          <a href="mailto:help@uw.edu">help@uw.edu</a></strong
        >.
      </p>
      <ul>
        <li>
          Include a screenshot, or paste the error text into your email so that
          we can quickly diagnose the issue.
          <ul>
            <li>
              The error text to paste into your email to us is: <br />{{
                errorText
              }}
            </li>
          </ul>
        </li>
      </ul>
    </div>
  </template>
</template>

<script>
export default {
  name: "ErrorsComp",
  props: {
    errorResponse: {
      type: Object,
      required: true,
    },
  },
  computed: {
    errorText() {
      return this.errorResponse.error
        ? this.errorResponse.error
        : this.errorResponse;
    },
  },
};
</script>
