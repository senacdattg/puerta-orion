import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

/**
 * Store para manejar el estado de la interfaz de usuario
 * Incluye loading states, notificaciones, modales, etc.
 */
export const useUIStore = defineStore('ui', () => {
  // Estado de carga global
  const isLoading = ref(false)
  const loadingMessage = ref('')

  // Notificaciones
  const notifications = ref([])
  const notificationId = ref(0)

  // Modales
  const modals = ref({})

  // Sidebar/Drawer
  const sidebarOpen = ref(false)

  // Tema
  const theme = ref('light')

  // Computed
  const hasNotifications = computed(() => notifications.value.length > 0)
  const hasActiveModals = computed(() => Object.keys(modals.value).length > 0)

  // Métodos de carga
  const setLoading = (loading, message = '') => {
    isLoading.value = loading
    loadingMessage.value = message
  }

  const showLoading = (message = 'Cargando...') => {
    setLoading(true, message)
  }

  const hideLoading = () => {
    setLoading(false, '')
  }

  // Métodos de notificaciones
  const addNotification = (notification) => {
    const id = ++notificationId.value
    const newNotification = {
      id,
      type: 'info', // info, success, warning, error
      title: '',
      message: '',
      duration: 5000,
      closable: true,
      ...notification
    }

    notifications.value.push(newNotification)

    // Auto-remove si tiene duración
    if (newNotification.duration > 0) {
      setTimeout(() => {
        removeNotification(id)
      }, newNotification.duration)
    }

    return id
  }

  const removeNotification = (id) => {
    const index = notifications.value.findIndex(n => n.id === id)
    if (index > -1) {
      notifications.value.splice(index, 1)
    }
  }

  const clearNotifications = () => {
    notifications.value = []
  }

  // Métodos de notificaciones específicas
  const showSuccess = (message, title = 'Éxito') => {
    return addNotification({ type: 'success', title, message })
  }

  const showError = (message, title = 'Error') => {
    return addNotification({ type: 'error', title, message })
  }

  const showWarning = (message, title = 'Advertencia') => {
    return addNotification({ type: 'warning', title, message })
  }

  const showInfo = (message, title = 'Información') => {
    return addNotification({ type: 'info', title, message })
  }

  // Métodos de modales
  const openModal = (modalId, data = {}) => {
    modals.value[modalId] = {
      open: true,
      data,
      ...data
    }
  }

  const closeModal = (modalId) => {
    if (modals.value[modalId]) {
      modals.value[modalId].open = false
      // Remover después de la animación
      setTimeout(() => {
        delete modals.value[modalId]
      }, 300)
    }
  }

  const closeAllModals = () => {
    modals.value = {}
  }

  // Métodos de sidebar
  const toggleSidebar = () => {
    sidebarOpen.value = !sidebarOpen.value
  }

  const openSidebar = () => {
    sidebarOpen.value = true
  }

  const closeSidebar = () => {
    sidebarOpen.value = false
  }

  // Métodos de tema
  const setTheme = (newTheme) => {
    theme.value = newTheme
    // Aplicar tema al documento
    document.documentElement.dataset.theme = newTheme // NOSONAR: S7761
  }

  const toggleTheme = () => {
    const newTheme = theme.value === 'light' ? 'dark' : 'light'
    setTheme(newTheme)
  }

  // Métodos de utilidad
  const reset = () => {
    isLoading.value = false
    loadingMessage.value = ''
    notifications.value = []
    modals.value = {}
    sidebarOpen.value = false
  }

  return {
    // Estado
    isLoading,
    loadingMessage,
    notifications,
    modals,
    sidebarOpen,
    theme,

    // Computed
    hasNotifications,
    hasActiveModals,

    // Métodos de carga
    setLoading,
    showLoading,
    hideLoading,

    // Métodos de notificaciones
    addNotification,
    removeNotification,
    clearNotifications,
    showSuccess,
    showError,
    showWarning,
    showInfo,

    // Métodos de modales
    openModal,
    closeModal,
    closeAllModals,

    // Métodos de sidebar
    toggleSidebar,
    openSidebar,
    closeSidebar,

    // Métodos de tema
    setTheme,
    toggleTheme,

    // Utilidades
    reset
  }
})

