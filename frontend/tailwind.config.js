/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ['"DM Sans"', "system-ui", "sans-serif"],
      },
      boxShadow: {
        soft: "0 4px 24px -4px rgba(15, 23, 42, 0.08), 0 8px 32px -8px rgba(15, 23, 42, 0.12)",
        glow: "0 0 0 1px rgba(99, 102, 241, 0.12), 0 12px 40px -12px rgba(79, 70, 229, 0.25)",
      },
    },
  },
  plugins: [],
};
