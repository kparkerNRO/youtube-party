import { defineConfig } from 'vite'

export default defineConfig({
  root: '.',
  publicDir: 'static',
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/ws': {
        target: 'ws://localhost:8000',
        ws: true,
      },
    },
  },
  build: {
    outDir: 'dist',
    rollupOptions: {
      input: {
        main: './index.html',
        host: './host.html',
      },
    },
  },
})
