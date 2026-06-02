import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Port 5175 so the enhanced dashboard can run alongside the base one (5174).
// Expose this port in your devfile the same way 5174 is exposed.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5175,
    host: true
  }
})
