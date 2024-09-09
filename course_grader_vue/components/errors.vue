<template>
  <template v-if="errorResponse.status === 404" id="404-error">
    <div class="alert" role="main">
      <h3>404 {{ errorText }}</h3>
      <p>Some things you may want to try:</p>
      <ul>
        <li>Make sure you are logged into this service with the appropriate UW NetID.</li>
        <li>Feel free to contact us at help@uw.edu if you have questions or need help.</li>
      </ul>
    </div>
  </template>
  <template v-else-if="errorResponse.status === 401" id="403-error">
    <div class="alert" role="main">
      <h3>{{ errorText }}</h3>
      <p>Some things you may want to try:</p>
      <ul>
        <li>Make sure you are logged into this service with the appropriate UW NetID.</li>
        <li>Feel free to contact us at help@uw.edu if you have questions or need help.</li>
      </ul>
    </div>
  </template>
  <template v-else-if="errorResponse.status === 500" id="500-error">
    <div class="alert" role="main">
      <h3>There was a problem retrieving grade information:</h3>
      <h4>{{ errorText }}</h4>

      <p>The Gradepage support team has been alerted of this issue and are working to get you back on track.</p>
      <p>You may want to:</p>
      <ul>
        <li>Give us a little time, and try again later.</li>
        <li>Drop us a line at <a href="mailto:help@uw.edu">help@uw.edu</a> and let us know that this has been taking awhile.</li>
      </ul>
    </div>
  </template>
  <template v-else id="543-error">
    <div class="alert" role="main">
      <h3>There was a problem retrieving grade information:</h3>
      <h4>{{ errorText }}</h4>

      <p>To correct this issue, <strong>please email us at <a href="mailto:help@uw.edu">help@uw.edu</a></strong>.</p>
      <ul>
        <li>Include a screenshot, or paste the error text into your email so that we can quickly diagnose the issue.
          <ul>
            <li>The error text to paste into your email to us is: <br/>{{ errorText }}</li>
          </ul>
        </li>
      </ul>
    </div>
  </template>
</template>

<script>
export default {
  props: {
    errorResponse: {
      type: Object,
      required: true,
    },
  },
  computed: {
    errorText() {
      return this.errorResponse.data ? this.errorResponse.data.error : "";
    },
  },
};
</script>
