import { defineConfig } from "vocs";

export default defineConfig({
  title: "papr",
  description: "Generate printable calendar PDFs and SVGs",
  basePath: "/papr",
  rootDir: "./docs",
  topNav: [
    { text: "Guide", link: "/getting-started", match: "/getting-started" },
    { text: "Layouts", link: "/layouts", match: "/layouts" },
    { text: "Reference", link: "/cli-reference", match: "/cli-reference" },
  ],
  socials: [
    { icon: "github", link: "https://github.com/peetzweg/papr" },
  ],
  editLink: {
    pattern:
      "https://github.com/peetzweg/papr/edit/master/docs/pages/:path",
    text: "Edit on GitHub",
  },
  sidebar: [
    {
      text: "Introduction",
      items: [
        { text: "Getting Started", link: "/getting-started" },
        { text: "Installation", link: "/installation" },
      ],
    },
    {
      text: "Layouts",
      items: [
        { text: "Overview", link: "/layouts" },
        { text: "month", link: "/layouts/month" },
        { text: "big", link: "/layouts/big" },
        { text: "classic", link: "/layouts/classic" },
        { text: "column", link: "/layouts/column" },
        { text: "oneyear", link: "/layouts/oneyear" },
      ],
    },
    {
      text: "Reference",
      items: [
        { text: "CLI Reference", link: "/cli-reference" },
        { text: "Batch Mode", link: "/batch-mode" },
      ],
    },
  ],
});
