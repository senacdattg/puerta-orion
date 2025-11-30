import { expect, afterEach, vi, beforeEach } from 'vitest'
import { cleanup } from '@testing-library/vue'
import '@testing-library/jest-dom/vitest'
import { config } from '@vue/test-utils'

// Global test utilities
globalThis.expect = expect

// Suppress console output during tests (except errors)
const originalConsole = { ...console }
const suppressedMethods = ['log', 'warn', 'info', 'debug']

beforeEach(() => {
  // Suppress console methods during tests
  suppressedMethods.forEach((method) => {
    console[method] = vi.fn()
  })
  // Keep console.error for actual errors
  console.error = originalConsole.error
})

afterEach(() => {
  cleanup()
  vi.clearAllMocks()
  // Restore console methods after tests
  suppressedMethods.forEach((method) => {
    console[method] = originalConsole[method]
  })
})

// Mock window.matchMedia
Object.defineProperty(globalThis.window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation((query) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn()
  }))
})

// Mock localStorage
const localStorageMock = (() => {
  let store = {}
  return {
    getItem: (key) => store[key] || null,
    setItem: (key, value) => {
      store[key] = value.toString()
    },
    removeItem: (key) => {
      delete store[key]
    },
    clear: () => {
      store = {}
    }
  }
})()

Object.defineProperty(globalThis.window, 'localStorage', {
  value: localStorageMock,
  writable: true
})

globalThis.localStorage = localStorageMock

// Mock fetch
globalThis.fetch = vi.fn()

// Configure Vue Test Utils
config.global.stubs = {
  'router-link': true,
  'router-view': true
}

// Mock environment variables
vi.mock('@/config/environment', () => ({
  API_CONFIG: {
    baseURL: 'http://localhost:5000'
  },
  CURRENT_CONFIG: {
    apiUrl: 'http://localhost:5000',
    debug: true,
    logLevel: 'debug'
  }
}))

