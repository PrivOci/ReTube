module.exports = {
  purge: [],
  darkMode: 'media', // or 'media' or 'class'
  i18n: {
    locales: ["en-US"],
    defaultLocale: "en-US",
  },
  theme: {
    extend: {},
  },
  variants: {
    extend: {
      backgroundColor: ["checked"],
      borderColor: ["checked"],
      inset: ["checked"],
      zIndex: ["hover", "active"],
    },
  },
  plugins: [
    require('@tailwindcss/aspect-ratio'),
  ],
};
