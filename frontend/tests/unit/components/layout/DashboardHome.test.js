import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import DashboardHome from '@/components/layout/DashboardHome.vue'
import { useUserRole } from '@/composables/useUserRole'

// Mock composables
vi.mock('@/composables/useUserRole', () => ({
  useUserRole: vi.fn()
}))

// Mock components
vi.mock('@/components/ui/registration-banner.vue', () => ({
  default: {
    name: 'RegistrationBanner',
    template: '<div class="registration-banner">Banner</div>'
  }
}))

vi.mock('@/components/admin/admin-dashboard.vue', () => ({
  default: {
    name: 'AdminDashboard',
    template: '<div class="admin-dashboard">Admin Dashboard</div>'
  }
}))

vi.mock('@/components/ui/basic-dashboard.vue', () => ({
  default: {
    name: 'BasicDashboard',
    template: '<div class="basic-dashboard">Basic Dashboard</div>'
  }
}))

// Mock router
const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: { template: '<div>Home</div>' } },
    { path: '/deportista/dashboard', component: { template: '<div>Deportista</div>' } },
    { path: '/acudiente/dashboard', component: { template: '<div>Acudiente</div>' } },
    { path: '/admin-manager', component: { template: '<div>Admin</div>' } }
  ]
})

describe('DashboardHome Component', () => {
  let wrapper
  let mockUseUserRole

  beforeEach(async () => {
    setActivePinia(createPinia())
    vi.clearAllMocks()

    mockUseUserRole = {
      userRole: { value: 'Usuario' },
      isDeportista: { value: false },
      isAcudiente: { value: false }
    }

    useUserRole.mockReturnValue(mockUseUserRole)

    await router.push('/')
  })

  it('should render component', () => {
    wrapper = mount(DashboardHome, {
      global: {
        plugins: [router],
        stubs: {
          RegistrationBanner: true,
          AdminDashboard: true,
          BasicDashboard: true
        }
      }
    })

    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('.dashboard-home').exists()).toBe(true)
  })

  it('should show registration banner for Usuario role', () => {
    mockUseUserRole.userRole.value = 'Usuario'

    wrapper = mount(DashboardHome, {
      global: {
        plugins: [router],
        stubs: {
          RegistrationBanner: true,
          AdminDashboard: true,
          BasicDashboard: true
        }
      }
    })

    expect(wrapper.vm.showRegistrationBanner).toBe(true)
  })

  it('should redirect deportista to deportista dashboard', async () => {
    mockUseUserRole.isDeportista.value = true
    mockUseUserRole.userRole.value = 'Deportista'

    wrapper = mount(DashboardHome, {
      global: {
        plugins: [router],
        stubs: {
          RegistrationBanner: true,
          AdminDashboard: true,
          BasicDashboard: true
        }
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    expect(router.currentRoute.value.path).toBe('/deportista/dashboard')
  })

  it('should redirect acudiente to acudiente dashboard', async () => {
    mockUseUserRole.isAcudiente.value = true
    mockUseUserRole.userRole.value = 'Acudiente'

    wrapper = mount(DashboardHome, {
      global: {
        plugins: [router],
        stubs: {
          RegistrationBanner: true,
          AdminDashboard: true,
          BasicDashboard: true
        }
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    expect(router.currentRoute.value.path).toBe('/acudiente/dashboard')
  })

  it('should redirect admin to admin-manager', async () => {
    mockUseUserRole.userRole.value = 'Administrador'

    wrapper = mount(DashboardHome, {
      global: {
        plugins: [router],
        stubs: {
          RegistrationBanner: true,
          AdminDashboard: true,
          BasicDashboard: true
        }
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    expect(router.currentRoute.value.path).toBe('/admin-manager')
  })

  it('should show AdminDashboard for Entrenador role', async () => {
    mockUseUserRole.userRole.value = 'Entrenador'
    mockUseUserRole.isDeportista.value = false
    mockUseUserRole.isAcudiente.value = false

    wrapper = mount(DashboardHome, {
      global: {
        plugins: [router],
        stubs: {
          RegistrationBanner: true,
          AdminDashboard: true,
          BasicDashboard: true
        }
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    // Verificar que el componente se renderizó correctamente
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.vm.userRole.value).toBe('Entrenador')
  })

  it('should show BasicDashboard for users without specific role', async () => {
    mockUseUserRole.userRole.value = 'Usuario'
    mockUseUserRole.isDeportista.value = false
    mockUseUserRole.isAcudiente.value = false

    wrapper = mount(DashboardHome, {
      global: {
        plugins: [router],
        stubs: {
          RegistrationBanner: true,
          AdminDashboard: true,
          BasicDashboard: true
        }
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    // Verificar que el componente se renderizó correctamente
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.vm.userRole.value).toBe('Usuario')
  })
})

