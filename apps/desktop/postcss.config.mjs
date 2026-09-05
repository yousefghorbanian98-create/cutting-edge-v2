/**
 * PostCSS config — S-007.
 *
 * Tailwind 4 ships its own PostCSS plugin (`@tailwindcss/postcss`); the old
 * `tailwindcss` + `autoprefixer` pair from Tailwind 3 is gone. DaisyUI 5 is
 * loaded from CSS with `@plugin "daisyui"` (see src/app/globals.css), not here.
 */
const config = {
  plugins: {
    '@tailwindcss/postcss': {},
  },
};

export default config;
