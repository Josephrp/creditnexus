import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// For GitHub Pages: if repository is 'username/creditnexus', base will be '/creditnexus/'
// For custom domain or root deployment, set base to '/'
const getBasePath = () => {
  // Check if we're building for GitHub Pages
  if (process.env.GITHUB_REPOSITORY) {
    const repoName = process.env.GITHUB_REPOSITORY.split('/')[1];
    return `/${repoName}/`;
  }
  // Default to root for local development
  return '/';
};

export default defineConfig({
  plugins: [react()],
  base: getBasePath(),
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
  },
});
