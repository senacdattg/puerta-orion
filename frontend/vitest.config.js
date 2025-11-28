import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./tests/setup.js'],
    outputFile: {
      junit: './coverage/test-results.xml'
    },
    silent: false,
    onConsoleLog: (log, type) => {
      // Suppress console.log and console.warn during tests
      if (type === 'log' || type === 'warn') {
        return false
      }
      return true
    },
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html', 'lcov', 'cobertura'],
      reportsDirectory: './coverage',
      exclude: [
        'node_modules/',
        'tests/',
        '**/*.config.js',
        '**/*.config.ts',
        'dist/',
        '**/*.d.ts',
        '**/main.js',
        '**/router/index.js',
        '**/App.vue',
        '**/assets/**',
        '**/public/**'
      ],
      thresholds: {
        lines: 50,
        functions: 50,
        branches: 30,
        statements: 50
      }
    },
    include: ['**/*.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx}'],
    exclude: ['node_modules', 'dist', '.idea', '.git', '.cache']
  },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  }
})

