import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { writeFileSync } from 'fs';
import { join } from 'path';

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

// Plugin to create .nojekyll file for GitHub Pages
const nojekyllPlugin = () => {
  return {
    name: 'nojekyll',
    writeBundle() {
      // Create .nojekyll file in dist directory after build
      // This tells GitHub Pages not to process files with Jekyll
      const outDir = 'dist';
      const nojekyllPath = join(process.cwd(), outDir, '.nojekyll');
      try {
        writeFileSync(nojekyllPath, '');
        console.log('Created .nojekyll file for GitHub Pages');
      } catch (error) {
        console.warn('Failed to create .nojekyll file:', error);
      }
    },
  };
};

export default defineConfig({
  plugins: [react(), nojekyllPlugin()],
  base: getBasePath(),
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
  },
});
