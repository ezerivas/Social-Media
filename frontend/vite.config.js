import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  base: './',
  build: {
    outDir: 'dist',
    emptyOutDir: true,
  },
  server: {
    allowedHosts: ['social-media-production-c7a6.up.railway.app'],
  },
  preview: {
    allowedHosts: ['social-media-production-c7a6.up.railway.app'],
  },
});