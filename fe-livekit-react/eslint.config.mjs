import { dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import antfu from '@antfu/eslint-config';
import tailwind from 'eslint-plugin-tailwindcss';

export default antfu({
  react: true,
  typescript: true,

  // Configuration preferences
  // lessOpinionated: true,
  isInEditor: false,

  stylistic: {
    semi: true,
    quotes: 'single',
    singleQuote: true,
  },

  ignores: [
    'dist',
    'node_modules',
  ],

  ...tailwind.configs['flat/recommended'],
  settings: {
    tailwindcss: {
      config: `${dirname(fileURLToPath(import.meta.url))}/src/index.css`,
    },
  },

  rules: {
    'style/jsx-quotes': ['error', 'prefer-single'],
  },
});
