// home.vue

<template>
  <Layout :page-title="pageTitle">

    <template #content>
      <div class="row">
        <div class="col-md-6">
          <h2>Requirements</h2>
          <p>Download the following:</p>
          <ul>
            <li>
              <a
                href="https://www.docker.com/products/docker-desktop/"
                target="_blank"
                >Docker Desktop
              </a>
            </li>
            <li>
              <a href="https://nodejs.org/en" target="_blank">Node</a>
            </li>
          </ul>

          <h2>Development</h2>
          <p>
            What's included? This template repository is intended to start you
            off with the Service Coordination and T&amp;LS supported development
            stack.
          </p>
          <ul>
            <li>Django</li>
            <li>Vue</li>
            <li>Vite</li>
          </ul>

          <h2>Design</h2>
          <p>
            We use the
            <a href="https://test.solstice.uw.edu">Solstice Design System</a> as
            the basis of our design.
          </p>
          <ul>
            <li>Bootstrap</li>
            <li>Bootstrap Icons</li>
          </ul>
        </div>
        <div class="col-md-6">
          <h2>Testing</h2>
          <ul>
            <li>
              <a href="https://vitest.dev/" target="_blank">Vitest</a>
            </li>
            <li>
              <a href="https://test-utils.vuejs.org/" target="_blank"
                >Vue Test Utils</a
              >
            </li>
          </ul>

          <h2>Linting (code quality)</h2>
          <ul>
            <li>Pycodestyle for Python</li>
            <li>ESLint for JS</li>
            <li>Stylelint for CSS</li>
          </ul>

          <h2>UW-IT Libraries</h2>
          <p>
            The following is a list of specific AXDD libraries used in building
            applications.
          </p>
          <ul>
            <li>
              <a
                href="https://github.com/uw-it-aca/django-container"
                target="_blank"
                >django-container</a
              >
            </li>
            <li>
              <a
                href="https://github.com/uw-it-aca/solstice-vue"
                target="_blank"
                >solstice-vue</a
              >
            </li>
          </ul>
        </div>

        <hr />

        <div class="col-md-6">
          <h2>Libraries</h2>
          <p>
            The following is a list of common JS and Vue libraries included in
            this repository.
          </p>
          <ul>
            <li>
              <a href="https://axios-http.com/" target="_blank">axios</a> (data
              fetching)
            </li>
            <li>
              <a href="https://pinia.vuejs.org/" target="_blank">pinia</a>
              (state management, formerly vuex)
            </li>
            <li>
              <a
                href="https://matteo-gabriele.gitbook.io/vue-gtag/v/next/"
                target="_blank"
                >vue-gtag-next</a
              >
              (google analytics)
            </li>
            <li>
              <a href="https://github.com/KanHarI/vue3-cookies" target="_blank"
                >vue3-cookies</a
              >
              (cookies)
            </li>
            <li>
              <a href="https://github.com/craigrileyuk/vue3-mq" target="_blank"
                >vue3-mq</a
              >
              (css media queries)
            </li>
          </ul>
        </div>

        <hr />

        <div class="col-md-8">
          <h2>Get Started</h2>
          <p>
            View the <a href="/customize">customizing your app</a> page to learn
            how to get started.
          </p>
        </div>
      </div>
    </template>
  </Layout>
</template>

<script>
import Layout from "@/layouts/default.vue";

export default {
  name: "PagesHome",
  components: {
    Layout,
  },
  data() {
    return {
      pageTitle: "Gesadfasdtting started",
    };
  },
  methods: {},
};
</script>

