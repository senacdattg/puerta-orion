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
      return type !== 'log' && type !== 'warn'
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
        lines: 48,
        functions: 44,
        branches: 30,
        statements: 48
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

