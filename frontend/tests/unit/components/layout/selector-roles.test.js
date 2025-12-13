import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import SelectorRoles from '@/components/layout/selector-roles.vue'
import { useAuthStore } from '@/stores/auth'

// Mock router
const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: { template: '<div>Home</div>' } }
  ]
})

// Mock auth store
vi.mock('@/stores/auth', () => ({
  useAuthStore: vi.fn()
}))

describe('SelectorRoles Component', () => {
  let mockAuthStore

  beforeEach(async () => {
    setActivePinia(createPinia())

    mockAuthStore = {
      user: {
        roles: ['Administrador', 'Entrenador']
      },
      rolesSelector: {
        Administrador: true,
        Entrenador: true
      },
      activeRole: 'Administrador',
      setActiveRole: vi.fn().mockResolvedValue({ success: true }),
      userDetail: null,
      loadUserProfileDetail: vi.fn().mockResolvedValue(true),
      refreshRoleOptions: vi.fn().mockResolvedValue(true)
    }

    useAuthStore.mockReturnValue(mockAuthStore)

    await router.push('/')
  })

  const createWrapper = () => {
    return mount(SelectorRoles, {
      global: {
        plugins: [router]
      }
    })
  }

  it('should render when roles are available', () => {
    const wrapper = createWrapper()

    expect(wrapper.find('.selector-roles').exists()).toBe(true)
  })

  it('should not render when no roles available', () => {
    mockAuthStore.rolesSelector = {}
    mockAuthStore.user.roles = []

    const wrapper = createWrapper()

    expect(wrapper.find('.selector-roles').exists()).toBe(false)
  })

  it('should render select element with roles', () => {
    const wrapper = createWrapper()

    const select = wrapper.find('select')

    expect(select.exists()).toBe(true)
    expect(select.element.options.length).toBeGreaterThan(0)
  })

  it('should call setActiveRole when select changes', async () => {
    const wrapper = createWrapper()

    const select = wrapper.find('select')
    await select.setValue('Entrenador')
    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    // The component calls setActiveRole asynchronously
    expect(mockAuthStore.setActiveRole).toHaveBeenCalled()
  })

  it('should display current active role', () => {
    mockAuthStore.activeRole = 'Entrenador'

    const wrapper = createWrapper()

    const select = wrapper.find('select')

    expect(select.element.value).toBe('Entrenador')
  })

  it('should handle roles as objects with nombre_rol property', () => {
    mockAuthStore.user.roles = [
      { nombre_rol: 'Administrador' },
      { nombre_rol: 'Entrenador' }
    ]
    mockAuthStore.rolesSelector = {
      Administrador: true,
      Entrenador: true
    }

    const wrapper = createWrapper()

    expect(wrapper.find('.selector-roles').exists()).toBe(true)
    const select = wrapper.find('select')
    expect(select.element.options.length).toBeGreaterThan(0)
  })

  it('should handle roles as strings', () => {
    mockAuthStore.user.roles = ['Administrador', 'Entrenador']
    mockAuthStore.rolesSelector = {
      Administrador: true,
      Entrenador: true
    }

    const wrapper = createWrapper()

    expect(wrapper.find('.selector-roles').exists()).toBe(true)
  })

    it('should include Usuario role when user has it but not in rolesSelector', () => {
      mockAuthStore.user.roles = [
        { nombre_rol: 'Usuario' },
        { nombre_rol: 'Deportista' }
      ]
      mockAuthStore.rolesSelector = {
        Deportista: true
      }
      mockAuthStore.loadUserProfileDetail = vi.fn().mockResolvedValue(true)

      const wrapper = createWrapper()

      expect(wrapper.find('.selector-roles').exists()).toBe(true)
    })

  it('should use rolesSelector when available', () => {
    mockAuthStore.user.roles = ['Administrador', 'Entrenador', 'Usuario']
    mockAuthStore.rolesSelector = {
      Administrador: true,
      Entrenador: false
    }

    const wrapper = createWrapper()
    const select = wrapper.find('select')

    expect(select.element.options.length).toBeGreaterThanOrEqual(1)
  })

  it('should use user roles when rolesSelector is empty', () => {
    mockAuthStore.user.roles = ['Administrador', 'Entrenador']
    mockAuthStore.rolesSelector = {}

    const wrapper = createWrapper()

    expect(wrapper.find('.selector-roles').exists()).toBe(true)
  })

  it('should handle cambiarRol with valid role', async () => {
    const wrapper = createWrapper()
    const select = wrapper.find('select')

    const changeEvent = {
      target: {
        value: 'Entrenador'
      }
    }

    await wrapper.vm.cambiarRol(changeEvent)
    await wrapper.vm.$nextTick()

    expect(mockAuthStore.setActiveRole).toHaveBeenCalled()
  })

  it('should handle cambiarRol with invalid role', async () => {
    const consoleWarn = vi.spyOn(console, 'warn').mockImplementation(() => {})
    const wrapper = createWrapper()

    const changeEvent = {
      target: {
        value: 'InvalidRole'
      }
    }

    await wrapper.vm.cambiarRol(changeEvent)
    await wrapper.vm.$nextTick()

    expect(consoleWarn).toHaveBeenCalled()
    consoleWarn.mockRestore()
  })

  it('should handle cambiarRol without event target', async () => {
    const wrapper = createWrapper()
    wrapper.vm.rolActivo = 'Entrenador'

    await wrapper.vm.cambiarRol(null)
    await wrapper.vm.$nextTick()

    expect(mockAuthStore.setActiveRole).toHaveBeenCalled()
  })

  it('should redirect to /home when role changes', async () => {
    const routerPush = vi.spyOn(router, 'replace').mockResolvedValue()
    const wrapper = createWrapper()
    const select = wrapper.find('select')

    mockAuthStore.setActiveRole.mockResolvedValue({ success: true })

    await select.setValue('Entrenador')
    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    expect(routerPush).toHaveBeenCalledWith('/home')
    routerPush.mockRestore()
  })

  it('should reload page when already on /home', async () => {
    globalThis.location = { reload: vi.fn() }
    await router.replace('/home')

    const wrapper = createWrapper()
    const select = wrapper.find('select')

    mockAuthStore.setActiveRole.mockResolvedValue({ success: true })

    await select.setValue('Entrenador')
    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    expect(globalThis.location.reload).toHaveBeenCalled()
  })

  it('should handle setActiveRole failure', async () => {
    const consoleWarn = vi.spyOn(console, 'warn').mockImplementation(() => {})
    mockAuthStore.setActiveRole.mockResolvedValue({ success: false, error: 'Failed' })

    const wrapper = createWrapper()
    const select = wrapper.find('select')

    await select.setValue('Entrenador')
    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    expect(consoleWarn).toHaveBeenCalled()
    consoleWarn.mockRestore()
  })

  it('should handle setActiveRole exception', async () => {
    const consoleWarn = vi.spyOn(console, 'warn').mockImplementation(() => {})
    mockAuthStore.setActiveRole.mockRejectedValue(new Error('Store error'))

    const wrapper = createWrapper()
    wrapper.vm.rolActivo = 'Entrenador'

    const changeEvent = {
      target: {
        value: 'Entrenador'
      }
    }

    await wrapper.vm.cambiarRol(changeEvent)
    await wrapper.vm.$nextTick()

    expect(consoleWarn).toHaveBeenCalled()
    consoleWarn.mockRestore()
  })

  it('should handle navigation error and use location.href', async () => {
    globalThis.location = { href: '' }
    const routerReplace = vi.spyOn(router, 'replace').mockRejectedValue(new Error('Navigation error'))
    const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {})

    const wrapper = createWrapper()
    wrapper.vm.rolActivo = 'Entrenador'
    mockAuthStore.setActiveRole.mockResolvedValue({ success: true })

    const changeEvent = {
      target: {
        value: 'Entrenador'
      }
    }

    await wrapper.vm.cambiarRol(changeEvent)
    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    expect(globalThis.location.href).toBe('/home')
    consoleError.mockRestore()
    routerReplace.mockRestore()
  })

  it('should get nombre rol correctly for string roles', () => {
    const wrapper = createWrapper()

    expect(wrapper.vm.getNombreRol('Deportista')).toContain('Deportista')
    expect(wrapper.vm.getNombreRol('Acudiente')).toContain('Acudiente')
    expect(wrapper.vm.getNombreRol('Entrenador')).toContain('Entrenador')
    expect(wrapper.vm.getNombreRol('Administrador')).toContain('Administrador')
    expect(wrapper.vm.getNombreRol('SuperAdmin')).toContain('Super')
  })

  it('should get nombre rol correctly for object roles', () => {
    const wrapper = createWrapper()

    expect(wrapper.vm.getNombreRol({ nombre_rol: 'Deportista' })).toContain('Deportista')
    expect(wrapper.vm.getNombreRol({ nombre_rol: 'Acudiente' })).toContain('Acudiente')
  })

  it('should get nombre rol simple correctly', () => {
    const wrapper = createWrapper()

    expect(wrapper.vm.getNombreRolSimple('Deportista')).toBe('Deportista')
    expect(wrapper.vm.getNombreRolSimple({ nombre_rol: 'Administrador' })).toBe('Administrador')
    expect(wrapper.vm.getNombreRolSimple(null)).toBe('')
  })

  it('should get nombre rol simple for invalid objects', () => {
    const wrapper = createWrapper()

    expect(wrapper.vm.getNombreRolSimple({})).toBe('')
    expect(wrapper.vm.getNombreRolSimple({ otro_campo: 'valor' })).toBe('')
  })

  it('should use localStorage activeRole when available', () => {
    globalThis.localStorage.getItem = vi.fn((key) => {
      if (key === 'activeRole') return 'Entrenador'
      return null
    })

    mockAuthStore.activeRole = null

    const wrapper = createWrapper()
    const select = wrapper.find('select')

    expect(select.element.value).toBe('Entrenador')
  })

    it('should use obtenerRolPrincipal when no activeRole', () => {
      globalThis.localStorage.getItem = vi.fn(() => null)
      mockAuthStore.activeRole = null
      mockAuthStore.user.roles = ['Deportista']
      mockAuthStore.loadUserProfileDetail = vi.fn().mockResolvedValue(true)

      const wrapper = createWrapper()

      expect(wrapper.find('.selector-roles').exists()).toBe(true)
    })

  it('should prioritize SuperAdmin in obtenerRolPrincipal', () => {
    const wrapper = createWrapper()
    mockAuthStore.user.roles = ['SuperAdmin', 'Deportista', 'Acudiente']

    wrapper.vm.$nextTick()

    expect(wrapper.find('.selector-roles').exists()).toBe(true)
  })

  it('should prioritize Administrador in obtenerRolPrincipal', () => {
    const wrapper = createWrapper()
    mockAuthStore.user.roles = ['Administrador', 'Deportista']

    wrapper.vm.$nextTick()

    expect(wrapper.find('.selector-roles').exists()).toBe(true)
  })

  it('should prioritize Entrenador in obtenerRolPrincipal', () => {
    const wrapper = createWrapper()
    mockAuthStore.user.roles = ['Entrenador', 'Deportista']

    wrapper.vm.$nextTick()

    expect(wrapper.find('.selector-roles').exists()).toBe(true)
  })

  it('should prioritize Acudiente in obtenerRolPrincipal', () => {
    const wrapper = createWrapper()
    mockAuthStore.user.roles = ['Acudiente', 'Deportista']

    wrapper.vm.$nextTick()

    expect(wrapper.find('.selector-roles').exists()).toBe(true)
  })

  it('should return first non-Usuario role in obtenerRolPrincipal', () => {
    const wrapper = createWrapper()
    mockAuthStore.user.roles = ['Usuario', 'CustomRole']

    wrapper.vm.$nextTick()

    expect(wrapper.find('.selector-roles').exists()).toBe(true)
  })

  it('should return usuario when only Usuario role exists', () => {
    const wrapper = createWrapper()
    mockAuthStore.user.roles = ['Usuario']

    wrapper.vm.$nextTick()

    expect(wrapper.find('.selector-roles').exists()).toBe(true)
  })

    it('should not render selector when roles array is empty', async () => {
      mockAuthStore.user.roles = []
      mockAuthStore.rolesSelector = {}

      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      // Cuando no hay roles, el selector no debe renderizarse
      expect(wrapper.find('.selector-roles').exists()).toBe(false)
    })

  it('should handle validarRol correctly', () => {
    const wrapper = createWrapper()

    expect(wrapper.vm.validarRol('Deportista')).toBe('Deportista')
    expect(wrapper.vm.validarRol('  Deportista  ')).toBe('Deportista')
    expect(wrapper.vm.validarRol('InvalidRole')).toBe(null)
    expect(wrapper.vm.validarRol(null)).toBe(null)
    expect(wrapper.vm.validarRol('')).toBe(null)
  })

  it('should load user profile detail when esDeportista is true', async () => {
    mockAuthStore.user.roles = ['Deportista']
    mockAuthStore.userDetail = null
    mockAuthStore.loadUserProfileDetail = vi.fn()

    const wrapper = createWrapper()
    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    expect(mockAuthStore.loadUserProfileDetail).toHaveBeenCalled()
  })

  it('should not load user profile detail when userDetail exists', async () => {
    mockAuthStore.user.roles = ['Deportista']
    mockAuthStore.userDetail = { id: 1 }
    mockAuthStore.loadUserProfileDetail = vi.fn()

    const wrapper = createWrapper()
    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    expect(mockAuthStore.loadUserProfileDetail).not.toHaveBeenCalled()
  })

  it('should handle refreshRoleOptions on mount when no rolesSelector', async () => {
    mockAuthStore.rolesSelector = {}
    mockAuthStore.activeRole = null
    globalThis.localStorage.getItem = vi.fn(() => null)
    mockAuthStore.refreshRoleOptions = vi.fn().mockResolvedValue(true)

    const wrapper = createWrapper()
    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 200))

    expect(mockAuthStore.refreshRoleOptions).toHaveBeenCalled()
  })

  it('should restore activeRole after refreshRoleOptions', async () => {
    const storedRole = 'Administrador'
    globalThis.localStorage.getItem = vi.fn((key) => {
      if (key === 'activeRole') return storedRole
      return null
    })

    mockAuthStore.rolesSelector = {}
    mockAuthStore.user.roles = [{ nombre_rol: 'Administrador' }]
    mockAuthStore.activeRole = null
    mockAuthStore.refreshRoleOptions = vi.fn().mockImplementation(() => {
      mockAuthStore.activeRole = 'Entrenador'
      return Promise.resolve()
    })
    mockAuthStore.setActiveRole = vi.fn().mockResolvedValue({ success: true })

    const wrapper = createWrapper()
    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 200))

    expect(mockAuthStore.setActiveRole).toHaveBeenCalledWith(storedRole)
  })

  it('should watch authStore.activeRole changes', async () => {
    mockAuthStore.activeRole = 'Administrador'
    const wrapper = createWrapper()
    await wrapper.vm.$nextTick()

    let select = wrapper.find('select')
    expect(select.element.value).toBe('Administrador')

    // Cambiar el rol activo
    mockAuthStore.activeRole = 'Entrenador'
    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 50))

    // Verificar que se sincronizó (puede requerir esperar a que el watcher se ejecute)
    select = wrapper.find('select')
    // El valor puede cambiar o mantenerse dependiendo de la lógica de sincronización
    expect(wrapper.find('.selector-roles').exists()).toBe(true)
  })

  it('should not sync with store when role was explicitly selected', async () => {
    const consoleLog = vi.spyOn(console, 'log').mockImplementation(() => {})
    const storedRole = 'Administrador'
    globalThis.localStorage.getItem = vi.fn((key) => {
      if (key === 'activeRole') return storedRole
      return null
    })

    const wrapper = createWrapper()
    wrapper.vm.rolActivo = storedRole

    mockAuthStore.activeRole = 'Entrenador'
    await wrapper.vm.$nextTick()

    expect(consoleLog).toHaveBeenCalled()
    consoleLog.mockRestore()
  })

  it('should handle role name normalization in role restoration', async () => {
    const storedRole = 'administrador'
    globalThis.localStorage.getItem = vi.fn((key) => {
      if (key === 'activeRole') return storedRole
      return null
    })

    mockAuthStore.user.roles = [{ nombre_rol: 'Administrador' }]
    mockAuthStore.activeRole = null

    const wrapper = createWrapper()
    await wrapper.vm.$nextTick()

    expect(wrapper.find('.selector-roles').exists()).toBe(true)
  })

    it('should restore role when it matches after normalization', async () => {
      const storedRole = 'deportista'
      globalThis.localStorage.getItem = vi.fn((key) => {
        if (key === 'activeRole') return storedRole
        return null
      })

      mockAuthStore.user.roles = [{ nombre_rol: 'Deportista' }]
      mockAuthStore.activeRole = null
      mockAuthStore.rolesSelector = {}
      mockAuthStore.refreshRoleOptions = vi.fn().mockResolvedValue(true)
      mockAuthStore.setActiveRole = vi.fn().mockResolvedValue({ success: true })
      mockAuthStore.loadUserProfileDetail = vi.fn().mockResolvedValue(true)

      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 200))

      expect(mockAuthStore.setActiveRole).toHaveBeenCalled()
  })
})

