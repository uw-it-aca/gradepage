// lighthouserc.cjs
require("dotenv").config();
const port = process.env.RUNSERVER_PORT;

module.exports = {
  ci: {
    collect: {
      settings: {
        //set which categories you want to run
        onlyCategories: ["accessibility"],
        preset: "desktop",
        extraHeaders: '{"Sec-CH-Prefers-Color-Scheme": "light"}',
      },
      url: [
        // add URLs to be tested (usually matches /pages structure)
        `http://localhost:${port}/term/2013-winter`,
        `http://localhost:${port}/term/2013-spring`,
        `http://localhost:${port}/section/2013-spring-A%20B&C-101-A-FBB38FE46A7C11D5A4AE0004AC494FFE`,
        `http://localhost:${port}/section/2013-spring-TRAIN-101-B-FBB38FE46A7C11D5A4AE0004AC494FFE`,
        `http://localhost:${port}/section/2013-spring-ZERROR-101-C-FBB38FE46A7C11D5A4AE0004AC494FFE`,
        `http://localhost:${port}/section/013-spring-ZERROR-101-S1-FBB38FE46A7C11D5A4AE0004AC494FFE`,
      ],
      // specify other options like numberOfRuns, staticDistDir, etc.
      numberOfRuns: 1,
    },
    // add assert, upload, and other configuration as required
    assert: {},
    upload: {},
    server: {},
    wizard: {},
  },
};
