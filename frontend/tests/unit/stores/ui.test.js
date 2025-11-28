import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useUIStore } from '@/stores/ui'

describe('UI Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  describe('Initial State', () => {
    it('should initialize with default values', () => {
      const store = useUIStore()
      expect(store.isLoading).toBe(false)
      expect(store.loadingMessage).toBe('')
      expect(store.notifications).toEqual([])
      expect(store.modals).toEqual({})
      expect(store.sidebarOpen).toBe(false)
      expect(store.theme).toBe('light')
    })
  })

  describe('Loading State', () => {
    it('should set loading state', () => {
      const store = useUIStore()
      store.setLoading(true, 'Loading...')

      expect(store.isLoading).toBe(true)
      expect(store.loadingMessage).toBe('Loading...')
    })

    it('should show loading', () => {
      const store = useUIStore()
      store.showLoading('Please wait...')

      expect(store.isLoading).toBe(true)
      expect(store.loadingMessage).toBe('Please wait...')
    })

    it('should hide loading', () => {
      const store = useUIStore()
      store.showLoading('Loading...')
      store.hideLoading()

      expect(store.isLoading).toBe(false)
      expect(store.loadingMessage).toBe('')
    })
  })

  describe('Notifications', () => {
    it('should add notification', () => {
      const store = useUIStore()
      const id = store.addNotification({
        type: 'success',
        title: 'Success',
        message: 'Operation completed'
      })

      expect(store.notifications).toHaveLength(1)
      expect(store.notifications[0].id).toBe(id)
      expect(store.notifications[0].type).toBe('success')
    })

    it('should remove notification', () => {
      const store = useUIStore()
      const id = store.addNotification({ message: 'Test' })
      store.removeNotification(id)

      expect(store.notifications).toHaveLength(0)
    })

    it('should auto-remove notification after duration', () => {
      const store = useUIStore()
      const id = store.addNotification({
        message: 'Test',
        duration: 1000
      })

      expect(store.notifications).toHaveLength(1)
      vi.advanceTimersByTime(1000)
      expect(store.notifications).toHaveLength(0)
    })

    it('should clear all notifications', () => {
      const store = useUIStore()
      store.addNotification({ message: 'Test 1' })
      store.addNotification({ message: 'Test 2' })
      store.clearNotifications()

      expect(store.notifications).toHaveLength(0)
    })
  })

  describe('Notification Helpers', () => {
    it('should show success notification', () => {
      const store = useUIStore()
      store.showSuccess('Operation successful')

      expect(store.notifications[0].type).toBe('success')
      expect(store.notifications[0].message).toBe('Operation successful')
    })

    it('should show error notification', () => {
      const store = useUIStore()
      store.showError('Operation failed')

      expect(store.notifications[0].type).toBe('error')
      expect(store.notifications[0].message).toBe('Operation failed')
    })

    it('should show warning notification', () => {
      const store = useUIStore()
      store.showWarning('Warning message')

      expect(store.notifications[0].type).toBe('warning')
    })

    it('should show info notification', () => {
      const store = useUIStore()
      store.showInfo('Info message')

      expect(store.notifications[0].type).toBe('info')
    })
  })

  describe('Modals', () => {
    it('should open modal', () => {
      const store = useUIStore()
      store.openModal('testModal', { data: 'test' })

      expect(store.modals.testModal.open).toBe(true)
      expect(store.modals.testModal.data).toBe('test')
    })

    it('should close modal', () => {
      const store = useUIStore()
      store.openModal('testModal')
      store.closeModal('testModal')

      expect(store.modals.testModal.open).toBe(false)
    })

    it('should close all modals', () => {
      const store = useUIStore()
      store.openModal('modal1')
      store.openModal('modal2')
      store.closeAllModals()

      expect(Object.keys(store.modals)).toHaveLength(0)
    })
  })

  describe('Sidebar', () => {
    it('should toggle sidebar', () => {
      const store = useUIStore()
      expect(store.sidebarOpen).toBe(false)

      store.toggleSidebar()
      expect(store.sidebarOpen).toBe(true)

      store.toggleSidebar()
      expect(store.sidebarOpen).toBe(false)
    })

    it('should open sidebar', () => {
      const store = useUIStore()
      store.openSidebar()
      expect(store.sidebarOpen).toBe(true)
    })

    it('should close sidebar', () => {
      const store = useUIStore()
      store.openSidebar()
      store.closeSidebar()
      expect(store.sidebarOpen).toBe(false)
    })
  })

  describe('Theme', () => {
    it('should set theme', () => {
      const store = useUIStore()
      store.setTheme('dark')
      expect(store.theme).toBe('dark')
    })

    it('should toggle theme', () => {
      const store = useUIStore()
      expect(store.theme).toBe('light')

      store.toggleTheme()
      expect(store.theme).toBe('dark')

      store.toggleTheme()
      expect(store.theme).toBe('light')
    })
  })

  describe('Computed Properties', () => {
    it('should compute hasNotifications', () => {
      const store = useUIStore()
      expect(store.hasNotifications).toBe(false)

      store.addNotification({ message: 'Test' })
      expect(store.hasNotifications).toBe(true)
    })

    it('should compute hasActiveModals', () => {
      const store = useUIStore()
      expect(store.hasActiveModals).toBe(false)

      store.openModal('testModal')
      expect(store.hasActiveModals).toBe(true)
    })
  })

  describe('Reset', () => {
    it('should reset store to initial state', () => {
      const store = useUIStore()
      store.showLoading('Loading...')
      store.addNotification({ message: 'Test' })
      store.openModal('testModal')
      store.openSidebar()

      store.reset()

      expect(store.isLoading).toBe(false)
      expect(store.notifications).toHaveLength(0)
      expect(Object.keys(store.modals)).toHaveLength(0)
      expect(store.sidebarOpen).toBe(false)
    })
  })
})

