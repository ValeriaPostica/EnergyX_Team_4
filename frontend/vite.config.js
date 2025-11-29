import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/auth': 'http://127.0.0.1:5000',
      '/diff': 'http://127.0.0.1:5000',
      '/keys': 'http://127.0.0.1:5000',
      '/general_info': 'http://127.0.0.1:5000',
      '/tariff': 'http://127.0.0.1:5000',
      '/region': 'http://127.0.0.1:5000',
      '/ai': 'http://127.0.0.1:5000',
      '/pred': 'http://127.0.0.1:5000',
      '/consumption': 'http://127.0.0.1:5000',
      '/color': 'http://127.0.0.1:5000',
      '/simple_log': 'http://127.0.0.1:5000',
      '/calculate': 'http://127.0.0.1:5000',
      '/check-leaderboard-table': 'http://127.0.0.1:5000',
      '/leaderboard': 'http://127.0.0.1:5000',
      '/points': 'http://127.0.0.1:5000',
      '/api/status': 'http://127.0.0.1:4000'
    }
  },
  resolve: {
    alias: {
      react: path.resolve(__dirname, 'node_modules/react'),
      'react-dom': path.resolve(__dirname, 'node_modules/react-dom'),
      'react/jsx-runtime': path.resolve(__dirname, 'node_modules/react/jsx-runtime'),
    },
  },
})
