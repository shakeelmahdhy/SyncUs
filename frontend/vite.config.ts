import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

const backendTarget = 'http://127.0.0.1:8000';
const apiProxy = { target: backendTarget, changeOrigin: true };

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: '127.0.0.1',
    proxy: {
      '/accounts': apiProxy,
      '/jobs': apiProxy,
      '/matching': apiProxy,
      '/tracking': apiProxy,
      '/search': apiProxy,
      '/health': apiProxy,
    },
  },
});
