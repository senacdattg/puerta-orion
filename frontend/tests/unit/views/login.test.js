import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import LoginView from '@/views/login.vue'

// Importar el componente Login para asegurar que se ejecute
import Login from '@/components/ui/login.vue'

describe('LoginView', () => {
  let wrapper

  beforeEach(() => {
    setActivePinia(createPinia())
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  it('should render the view', () => {
    wrapper = mount(LoginView, {
      global: {
        stubs: {
          Login: {
            name: 'Login',
            template: '<div class="login-component">Login Component</div>'
          }
        }
      }
    })

    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('main').exists()).toBe(true)
  })

  it('should render Login component', () => {
    wrapper = mount(LoginView, {
      global: {
        stubs: {
          Login: {
            name: 'Login',
            template: '<div class="login-component">Login Component</div>'
          }
        }
      }
    })

    expect(wrapper.find('.login-component').exists()).toBe(true)
  })

  it('should have correct component name', () => {
    expect(LoginView.name || LoginView.__name).toBe('LoginView')
  })

  it('should execute script setup code', () => {
    wrapper = mount(LoginView, {
      global: {
        stubs: {
          Login: {
            name: 'Login',
            template: '<div class="login-component">Login Component</div>'
          }
        }
      }
    })

    // Access component properties to ensure script setup is executed
    expect(LoginView.name || LoginView.__name).toBeDefined()
    expect(wrapper.vm).toBeDefined()
  })

  it('should have Login component imported', () => {
    // Verify that Login component is available
    expect(Login).toBeDefined()
  })
})

