import { fileURLToPath, URL } from "url";

import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

// TODO: remove automatic bs-vue-next comp registering later
import Components from 'unplugin-vue-components/vite'
import { BootstrapVueNextResolver } from "bootstrap-vue-next";

// https://vitejs.dev/config/
export default defineConfig({
  // MARK: start vite build config

  // vite creates a manifest and assets during the build process (local and prod)
  // django collectstatics will put assets in '/static/app_name/assets'
  // django will put the manifest in '/static/manifest.json'
  // vite manifest prefaces all files with the path 'app_name/assets/xxxx'
  build: {
    manifest: true,
    rollupOptions: {
      input: [
        // list all entry points
        "./course_grader_vue/main.js",
      ],
    },
    outDir: "./course_grader/static/", // relative path to django's static directory
    assetsDir: "course_grader/assets", // default ('assets')... this is the namespaced subdirectory of outDir that vite uses
    emptyOutDir: false, // set to false to ensure favicon is not overwritten
  },
  base: "/static/", // allows for proper css url path creation during the build process

  // MARK: standard vite/vue plugin and resolver config
  plugins: [
    vue(),
    Components({
      resolvers: [BootstrapVueNextResolver()],
    }),
  ],
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./course_grader_vue", import.meta.url)),
    },
  },
});
