import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'

/**
 * Creates a test router instance
 */
export const createTestRouter = (routes = []) => {
  return createRouter({
    history: createWebHistory(),
    routes: [
      { path: '/', component: { template: '<div>Home</div>' } },
      ...routes
    ]
  })
}

/**
 * Creates a test Pinia instance
 */
export const createTestPinia = () => {
  const pinia = createPinia()
  setActivePinia(pinia)
  return pinia
}

/**
 * Mounts a component with default test setup
 */
export const mountComponent = (component, options = {}) => {
  const pinia = options.pinia || createTestPinia()
  const router = options.router || createTestRouter()

  return mount(component, {
    global: {
      plugins: [pinia, router],
      stubs: {
        'router-link': true,
        'router-view': true,
        ...options.stubs
      },
      mocks: {
        ...options.mocks
      }
    },
    ...options
  })
}

/**
 * Waits for next tick
 */
export const waitForNextTick = () => {
  return new Promise(resolve => setTimeout(resolve, 0))
}

/**
 * Waits for a condition to be true
 */
export const waitFor = async (condition, timeout = 5000) => {
  const start = Date.now()
  while (!condition() && Date.now() - start < timeout) {
    await waitForNextTick()
  }
  if (!condition()) {
    throw new Error('Timeout waiting for condition')
  }
}

