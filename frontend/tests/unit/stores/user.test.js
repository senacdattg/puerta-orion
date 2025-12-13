import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useUserStore } from '@/stores/user'
import { usuariosService } from '@/services/usuariosService'

vi.mock('@/services/usuariosService', () => ({
  usuariosService: {
    obtenerUsuarios: vi.fn(),
    obtenerDeportistas: vi.fn(),
    obtenerAcudientes: vi.fn(),
    obtenerEntrenadores: vi.fn(),
    crearDeportista: vi.fn(),
    crearAcudiente: vi.fn(),
    crearEntrenador: vi.fn(),
    actualizarUsuario: vi.fn(),
    eliminarUsuario: vi.fn()
  }
}))

describe('User Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  describe('Initial State', () => {
    it('should initialize with default values', () => {
      const store = useUserStore()
      expect(store.users).toEqual([])
      expect(store.deportistas).toEqual([])
      expect(store.acudientes).toEqual([])
      expect(store.entrenadores).toEqual([])
      expect(store.isLoading).toBe(false)
      expect(store.error).toBeNull()
    })
  })

  describe('Computed Properties', () => {
    it('should compute totalUsers correctly', () => {
      const store = useUserStore()
      store.users = [{ id: 1 }, { id: 2 }]
      expect(store.totalUsers).toBe(2)
    })

    it('should compute totalDeportistas correctly', () => {
      const store = useUserStore()
      store.deportistas = [{ id: 1 }, { id: 2 }, { id: 3 }]
      expect(store.totalDeportistas).toBe(3)
    })

    it('should compute totalAcudientes correctly', () => {
      const store = useUserStore()
      store.acudientes = [{ id: 1 }, { id: 2 }]
      expect(store.totalAcudientes).toBe(2)
    })

    it('should compute totalEntrenadores correctly', () => {
      const store = useUserStore()
      store.entrenadores = [{ id: 1 }, { id: 2 }, { id: 3 }, { id: 4 }]
      expect(store.totalEntrenadores).toBe(4)
    })

    it('should return 0 when arrays are empty', () => {
      const store = useUserStore()
      expect(store.totalUsers).toBe(0)
      expect(store.totalDeportistas).toBe(0)
      expect(store.totalAcudientes).toBe(0)
      expect(store.totalEntrenadores).toBe(0)
    })
  })

  describe('Fetch Users', () => {
    it('should fetch users successfully', async () => {
      const mockUsers = [{ id: 1, name: 'User 1' }, { id: 2, name: 'User 2' }]
      usuariosService.obtenerUsuarios.mockResolvedValue({
        data: mockUsers
      })

      const store = useUserStore()
      const result = await store.fetchUsers()

      expect(result.success).toBe(true)
      expect(store.users).toEqual(mockUsers)
      expect(store.isLoading).toBe(false)
      expect(store.error).toBeNull()
    })

    it('should handle fetch error', async () => {
      const error = new Error('Network error')
      usuariosService.obtenerUsuarios.mockRejectedValue(error)

      const store = useUserStore()
      const result = await store.fetchUsers()

      expect(result.success).toBe(false)
      expect(result.error).toBe(error)
      expect(store.error).toBe('Network error')
      expect(store.isLoading).toBe(false)
    })

    it('should handle fetch error without message', async () => {
      // NOSONAR: S7722 - Test requires error without message to verify fallback behavior
      const error = new Error()
      delete error.message
      usuariosService.obtenerUsuarios.mockRejectedValue(error)

      const store = useUserStore()
      const result = await store.fetchUsers()

      expect(result.success).toBe(false)
      expect(store.error).toBe('Error al cargar usuarios')
      expect(store.isLoading).toBe(false)
    })

    it('should set isLoading to true during fetch', async () => {
      let isLoadingDuringFetch = false
      usuariosService.obtenerUsuarios.mockImplementation(async () => {
        const store = useUserStore()
        isLoadingDuringFetch = store.isLoading
        return { data: [] }
      })

      const store = useUserStore()
      await store.fetchUsers()

      expect(isLoadingDuringFetch).toBe(true)
    })

    it('should handle empty response data', async () => {
      usuariosService.obtenerUsuarios.mockResolvedValue({})

      const store = useUserStore()
      const result = await store.fetchUsers()

      expect(result.success).toBe(true)
      expect(store.users).toEqual([])
    })

    it('should clear error before fetching', async () => {
      const store = useUserStore()
      store.error = 'Previous error'

      usuariosService.obtenerUsuarios.mockResolvedValue({ data: [] })
      await store.fetchUsers()

      expect(store.error).toBeNull()
    })
  })

  describe('Fetch Deportistas', () => {
    it('should fetch deportistas successfully', async () => {
      const mockDeportistas = [{ id: 1, nombre: 'Deportista 1' }]
      usuariosService.obtenerDeportistas.mockResolvedValue({
        data: mockDeportistas
      })

      const store = useUserStore()
      const result = await store.fetchDeportistas()

      expect(result.success).toBe(true)
      expect(store.deportistas).toEqual(mockDeportistas)
      expect(store.isLoading).toBe(false)
      expect(store.error).toBeNull()
    })

    it('should handle fetch deportistas error', async () => {
      const error = new Error('Network error')
      usuariosService.obtenerDeportistas.mockRejectedValue(error)

      const store = useUserStore()
      const result = await store.fetchDeportistas()

      expect(result.success).toBe(false)
      expect(result.error).toBe(error)
      expect(store.error).toBe('Network error')
      expect(store.isLoading).toBe(false)
    })

    it('should handle fetch deportistas error without message', async () => {
      // NOSONAR: S7722 - Test requires error without message to verify fallback behavior
      const error = new Error()
      delete error.message
      usuariosService.obtenerDeportistas.mockRejectedValue(error)

      const store = useUserStore()
      const result = await store.fetchDeportistas()

      expect(result.success).toBe(false)
      expect(store.error).toBe('Error al cargar deportistas')
      expect(store.isLoading).toBe(false)
    })

    it('should set isLoading correctly during fetch deportistas', async () => {
      let isLoadingDuringFetch = false
      usuariosService.obtenerDeportistas.mockImplementation(async () => {
        const store = useUserStore()
        isLoadingDuringFetch = store.isLoading
        return { data: [] }
      })

      const store = useUserStore()
      await store.fetchDeportistas()

      expect(isLoadingDuringFetch).toBe(true)
      expect(store.isLoading).toBe(false)
    })

    it('should handle empty response data for deportistas', async () => {
      usuariosService.obtenerDeportistas.mockResolvedValue({})

      const store = useUserStore()
      const result = await store.fetchDeportistas()

      expect(result.success).toBe(true)
      expect(store.deportistas).toEqual([])
    })

    it('should clear error before fetching deportistas', async () => {
      const store = useUserStore()
      store.error = 'Previous error'

      usuariosService.obtenerDeportistas.mockResolvedValue({ data: [] })
      await store.fetchDeportistas()

      expect(store.error).toBeNull()
    })
  })

  describe('Fetch Acudientes', () => {
    it('should fetch acudientes successfully', async () => {
      const mockAcudientes = [{ id: 1, nombre: 'Acudiente 1' }]
      usuariosService.obtenerAcudientes.mockResolvedValue({
        data: mockAcudientes
      })

      const store = useUserStore()
      const result = await store.fetchAcudientes()

      expect(result.success).toBe(true)
      expect(store.acudientes).toEqual(mockAcudientes)
      expect(store.isLoading).toBe(false)
      expect(store.error).toBeNull()
    })

    it('should handle fetch acudientes error', async () => {
      const error = new Error('Network error')
      usuariosService.obtenerAcudientes.mockRejectedValue(error)

      const store = useUserStore()
      const result = await store.fetchAcudientes()

      expect(result.success).toBe(false)
      expect(result.error).toBe(error)
      expect(store.error).toBe('Network error')
      expect(store.isLoading).toBe(false)
    })

    it('should handle fetch acudientes error without message', async () => {
      // NOSONAR: S7722 - Test requires error without message to verify fallback behavior
      const error = new Error()
      delete error.message
      usuariosService.obtenerAcudientes.mockRejectedValue(error)

      const store = useUserStore()
      const result = await store.fetchAcudientes()

      expect(result.success).toBe(false)
      expect(store.error).toBe('Error al cargar acudientes')
      expect(store.isLoading).toBe(false)
    })

    it('should set isLoading correctly during fetch acudientes', async () => {
      let isLoadingDuringFetch = false
      usuariosService.obtenerAcudientes.mockImplementation(async () => {
        const store = useUserStore()
        isLoadingDuringFetch = store.isLoading
        return { data: [] }
      })

      const store = useUserStore()
      await store.fetchAcudientes()

      expect(isLoadingDuringFetch).toBe(true)
      expect(store.isLoading).toBe(false)
    })

    it('should handle empty response data for acudientes', async () => {
      usuariosService.obtenerAcudientes.mockResolvedValue({})

      const store = useUserStore()
      const result = await store.fetchAcudientes()

      expect(result.success).toBe(true)
      expect(store.acudientes).toEqual([])
    })

    it('should clear error before fetching acudientes', async () => {
      const store = useUserStore()
      store.error = 'Previous error'

      usuariosService.obtenerAcudientes.mockResolvedValue({ data: [] })
      await store.fetchAcudientes()

      expect(store.error).toBeNull()
    })
  })

  describe('Fetch Entrenadores', () => {
    it('should fetch entrenadores successfully', async () => {
      const mockEntrenadores = [{ id: 1, nombre: 'Entrenador 1' }]
      usuariosService.obtenerEntrenadores.mockResolvedValue({
        data: mockEntrenadores
      })

      const store = useUserStore()
      const result = await store.fetchEntrenadores()

      expect(result.success).toBe(true)
      expect(store.entrenadores).toEqual(mockEntrenadores)
      expect(store.isLoading).toBe(false)
      expect(store.error).toBeNull()
    })

    it('should handle fetch entrenadores error', async () => {
      const error = new Error('Network error')
      usuariosService.obtenerEntrenadores.mockRejectedValue(error)

      const store = useUserStore()
      const result = await store.fetchEntrenadores()

      expect(result.success).toBe(false)
      expect(result.error).toBe(error)
      expect(store.error).toBe('Network error')
      expect(store.isLoading).toBe(false)
    })

    it('should handle fetch entrenadores error without message', async () => {
      // NOSONAR: S7722 - Test requires error without message to verify fallback behavior
      const error = new Error()
      delete error.message
      usuariosService.obtenerEntrenadores.mockRejectedValue(error)

      const store = useUserStore()
      const result = await store.fetchEntrenadores()

      expect(result.success).toBe(false)
      expect(store.error).toBe('Error al cargar entrenadores')
      expect(store.isLoading).toBe(false)
    })

    it('should set isLoading correctly during fetch entrenadores', async () => {
      let isLoadingDuringFetch = false
      usuariosService.obtenerEntrenadores.mockImplementation(async () => {
        const store = useUserStore()
        isLoadingDuringFetch = store.isLoading
        return { data: [] }
      })

      const store = useUserStore()
      await store.fetchEntrenadores()

      expect(isLoadingDuringFetch).toBe(true)
      expect(store.isLoading).toBe(false)
    })

    it('should handle empty response data for entrenadores', async () => {
      usuariosService.obtenerEntrenadores.mockResolvedValue({})

      const store = useUserStore()
      const result = await store.fetchEntrenadores()

      expect(result.success).toBe(true)
      expect(store.entrenadores).toEqual([])
    })

    it('should clear error before fetching entrenadores', async () => {
      const store = useUserStore()
      store.error = 'Previous error'

      usuariosService.obtenerEntrenadores.mockResolvedValue({ data: [] })
      await store.fetchEntrenadores()

      expect(store.error).toBeNull()
    })
  })

  describe('Create Deportista', () => {
    it('should create deportista successfully', async () => {
      const newDeportista = { id: 1, nombre: 'New Deportista' }
      usuariosService.crearDeportista.mockResolvedValue({
        data: newDeportista
      })

      const store = useUserStore()
      store.deportistas = []
      const result = await store.createDeportista({ nombre: 'New Deportista' })

      expect(result.success).toBe(true)
      expect(store.deportistas).toContainEqual(newDeportista)
      expect(store.deportistas.length).toBe(1)
      expect(store.isLoading).toBe(false)
      expect(store.error).toBeNull()
    })

    it('should handle create deportista error', async () => {
      const error = new Error('Creation failed')
      usuariosService.crearDeportista.mockRejectedValue(error)

      const store = useUserStore()
      store.deportistas = []
      const result = await store.createDeportista({ nombre: 'New Deportista' })

      expect(result.success).toBe(false)
      expect(result.error).toBe(error)
      expect(store.error).toBe('Creation failed')
      expect(store.deportistas.length).toBe(0)
      expect(store.isLoading).toBe(false)
    })

    it('should handle create deportista error without message', async () => {
      // NOSONAR: S7722 - Test requires error without message to verify fallback behavior
      const error = new Error()
      delete error.message
      usuariosService.crearDeportista.mockRejectedValue(error)

      const store = useUserStore()
      const result = await store.createDeportista({ nombre: 'New Deportista' })

      expect(result.success).toBe(false)
      expect(store.error).toBe('Error al crear deportista')
      expect(store.isLoading).toBe(false)
    })

    it('should append to existing deportistas list', async () => {
      const existingDeportista = { id: 1, nombre: 'Existing' }
      const newDeportista = { id: 2, nombre: 'New Deportista' }
      usuariosService.crearDeportista.mockResolvedValue({
        data: newDeportista
      })

      const store = useUserStore()
      store.deportistas = [existingDeportista]
      await store.createDeportista({ nombre: 'New Deportista' })

      expect(store.deportistas.length).toBe(2)
      expect(store.deportistas).toContainEqual(existingDeportista)
      expect(store.deportistas).toContainEqual(newDeportista)
    })

    it('should set isLoading correctly during create deportista', async () => {
      let isLoadingDuringCreate = false
      usuariosService.crearDeportista.mockImplementation(async () => {
        const store = useUserStore()
        isLoadingDuringCreate = store.isLoading
        return { data: { id: 1 } }
      })

      const store = useUserStore()
      await store.createDeportista({})

      expect(isLoadingDuringCreate).toBe(true)
      expect(store.isLoading).toBe(false)
    })

    it('should clear error before creating deportista', async () => {
      const store = useUserStore()
      store.error = 'Previous error'

      usuariosService.crearDeportista.mockResolvedValue({ data: { id: 1 } })
      await store.createDeportista({})

      expect(store.error).toBeNull()
    })
  })

  describe('Create Acudiente', () => {
    it('should create acudiente successfully', async () => {
      const newAcudiente = { id: 1, nombre: 'New Acudiente' }
      usuariosService.crearAcudiente.mockResolvedValue({
        data: newAcudiente
      })

      const store = useUserStore()
      store.acudientes = []
      const result = await store.createAcudiente({ nombre: 'New Acudiente' })

      expect(result.success).toBe(true)
      expect(store.acudientes).toContainEqual(newAcudiente)
      expect(store.acudientes.length).toBe(1)
      expect(store.isLoading).toBe(false)
      expect(store.error).toBeNull()
    })

    it('should handle create acudiente error', async () => {
      const error = new Error('Creation failed')
      usuariosService.crearAcudiente.mockRejectedValue(error)

      const store = useUserStore()
      store.acudientes = []
      const result = await store.createAcudiente({ nombre: 'New Acudiente' })

      expect(result.success).toBe(false)
      expect(result.error).toBe(error)
      expect(store.error).toBe('Creation failed')
      expect(store.acudientes.length).toBe(0)
      expect(store.isLoading).toBe(false)
    })

    it('should handle create acudiente error without message', async () => {
      // NOSONAR: S7722 - Test requires error without message to verify fallback behavior
      const error = new Error()
      delete error.message
      usuariosService.crearAcudiente.mockRejectedValue(error)

      const store = useUserStore()
      const result = await store.createAcudiente({ nombre: 'New Acudiente' })

      expect(result.success).toBe(false)
      expect(store.error).toBe('Error al crear acudiente')
      expect(store.isLoading).toBe(false)
    })

    it('should append to existing acudientes list', async () => {
      const existingAcudiente = { id: 1, nombre: 'Existing' }
      const newAcudiente = { id: 2, nombre: 'New Acudiente' }
      usuariosService.crearAcudiente.mockResolvedValue({
        data: newAcudiente
      })

      const store = useUserStore()
      store.acudientes = [existingAcudiente]
      await store.createAcudiente({ nombre: 'New Acudiente' })

      expect(store.acudientes.length).toBe(2)
      expect(store.acudientes).toContainEqual(existingAcudiente)
      expect(store.acudientes).toContainEqual(newAcudiente)
    })

    it('should set isLoading correctly during create acudiente', async () => {
      let isLoadingDuringCreate = false
      usuariosService.crearAcudiente.mockImplementation(async () => {
        const store = useUserStore()
        isLoadingDuringCreate = store.isLoading
        return { data: { id: 1 } }
      })

      const store = useUserStore()
      await store.createAcudiente({})

      expect(isLoadingDuringCreate).toBe(true)
      expect(store.isLoading).toBe(false)
    })

    it('should clear error before creating acudiente', async () => {
      const store = useUserStore()
      store.error = 'Previous error'

      usuariosService.crearAcudiente.mockResolvedValue({ data: { id: 1 } })
      await store.createAcudiente({})

      expect(store.error).toBeNull()
    })
  })

  describe('Create Entrenador', () => {
    it('should create entrenador successfully', async () => {
      const newEntrenador = { id: 1, nombre: 'New Entrenador' }
      usuariosService.crearEntrenador.mockResolvedValue({
        data: newEntrenador
      })

      const store = useUserStore()
      store.entrenadores = []
      const result = await store.createEntrenador({ nombre: 'New Entrenador' })

      expect(result.success).toBe(true)
      expect(store.entrenadores).toContainEqual(newEntrenador)
      expect(store.entrenadores.length).toBe(1)
      expect(store.isLoading).toBe(false)
      expect(store.error).toBeNull()
    })

    it('should handle create entrenador error', async () => {
      const error = new Error('Creation failed')
      usuariosService.crearEntrenador.mockRejectedValue(error)

      const store = useUserStore()
      store.entrenadores = []
      const result = await store.createEntrenador({ nombre: 'New Entrenador' })

      expect(result.success).toBe(false)
      expect(result.error).toBe(error)
      expect(store.error).toBe('Creation failed')
      expect(store.entrenadores.length).toBe(0)
      expect(store.isLoading).toBe(false)
    })

    it('should handle create entrenador error without message', async () => {
      // NOSONAR: S7722 - Test requires error without message to verify fallback behavior
      const error = new Error()
      delete error.message
      usuariosService.crearEntrenador.mockRejectedValue(error)

      const store = useUserStore()
      const result = await store.createEntrenador({ nombre: 'New Entrenador' })

      expect(result.success).toBe(false)
      expect(store.error).toBe('Error al crear entrenador')
      expect(store.isLoading).toBe(false)
    })

    it('should append to existing entrenadores list', async () => {
      const existingEntrenador = { id: 1, nombre: 'Existing' }
      const newEntrenador = { id: 2, nombre: 'New Entrenador' }
      usuariosService.crearEntrenador.mockResolvedValue({
        data: newEntrenador
      })

      const store = useUserStore()
      store.entrenadores = [existingEntrenador]
      await store.createEntrenador({ nombre: 'New Entrenador' })

      expect(store.entrenadores.length).toBe(2)
      expect(store.entrenadores).toContainEqual(existingEntrenador)
      expect(store.entrenadores).toContainEqual(newEntrenador)
    })

    it('should set isLoading correctly during create entrenador', async () => {
      let isLoadingDuringCreate = false
      usuariosService.crearEntrenador.mockImplementation(async () => {
        const store = useUserStore()
        isLoadingDuringCreate = store.isLoading
        return { data: { id: 1 } }
      })

      const store = useUserStore()
      await store.createEntrenador({})

      expect(isLoadingDuringCreate).toBe(true)
      expect(store.isLoading).toBe(false)
    })

    it('should clear error before creating entrenador', async () => {
      const store = useUserStore()
      store.error = 'Previous error'

      usuariosService.crearEntrenador.mockResolvedValue({ data: { id: 1 } })
      await store.createEntrenador({})

      expect(store.error).toBeNull()
    })
  })

  describe('Update User', () => {
    it('should update user successfully', async () => {
      const updatedUser = { id: 1, name: 'Updated User' }
      usuariosService.actualizarUsuario.mockResolvedValue({
        data: updatedUser
      })

      const store = useUserStore()
      store.users = [{ id: 1, name: 'Old User' }]
      const result = await store.updateUser(1, { name: 'Updated User' })

      expect(result.success).toBe(true)
      expect(store.users[0]).toEqual(updatedUser)
      expect(store.isLoading).toBe(false)
      expect(store.error).toBeNull()
    })

    it('should not update user if not found in local list', async () => {
      const updatedUser = { id: 999, name: 'Updated User' }
      usuariosService.actualizarUsuario.mockResolvedValue({
        data: updatedUser
      })

      const store = useUserStore()
      store.users = [{ id: 1, name: 'Old User' }]
      const result = await store.updateUser(999, { name: 'Updated User' })

      expect(result.success).toBe(true)
      expect(store.users.length).toBe(1)
      expect(store.users[0].name).toBe('Old User')
      expect(store.users[0].id).toBe(1)
    })

    it('should handle update user error', async () => {
      const error = new Error('Update failed')
      usuariosService.actualizarUsuario.mockRejectedValue(error)

      const store = useUserStore()
      store.users = [{ id: 1, name: 'Old User' }]
      const result = await store.updateUser(1, { name: 'Updated User' })

      expect(result.success).toBe(false)
      expect(result.error).toBe(error)
      expect(store.error).toBe('Update failed')
      expect(store.users[0].name).toBe('Old User')
      expect(store.isLoading).toBe(false)
    })

    it('should handle update user error without message', async () => {
      // NOSONAR: S7722 - Test requires error without message to verify fallback behavior
      const error = new Error()
      delete error.message
      usuariosService.actualizarUsuario.mockRejectedValue(error)

      const store = useUserStore()
      const result = await store.updateUser(1, {})

      expect(result.success).toBe(false)
      expect(store.error).toBe('Error al actualizar usuario')
      expect(store.isLoading).toBe(false)
    })

    it('should set isLoading correctly during update user', async () => {
      let isLoadingDuringUpdate = false
      usuariosService.actualizarUsuario.mockImplementation(async () => {
        const store = useUserStore()
        isLoadingDuringUpdate = store.isLoading
        return { data: { id: 1 } }
      })

      const store = useUserStore()
      store.users = [{ id: 1 }]
      await store.updateUser(1, {})

      expect(isLoadingDuringUpdate).toBe(true)
      expect(store.isLoading).toBe(false)
    })

    it('should clear error before updating user', async () => {
      const store = useUserStore()
      store.error = 'Previous error'
      store.users = [{ id: 1 }]

      usuariosService.actualizarUsuario.mockResolvedValue({ data: { id: 1 } })
      await store.updateUser(1, {})

      expect(store.error).toBeNull()
    })
  })

  describe('Delete User', () => {
    it('should delete user successfully', async () => {
      usuariosService.eliminarUsuario.mockResolvedValue({})

      const store = useUserStore()
      store.users = [{ id: 1 }, { id: 2 }]
      store.deportistas = [{ id: 1 }, { id: 3 }]
      store.acudientes = [{ id: 1 }, { id: 4 }]
      store.entrenadores = [{ id: 1 }, { id: 5 }]

      const result = await store.deleteUser(1)

      expect(result.success).toBe(true)
      expect(store.users).toHaveLength(1)
      expect(store.users.find(u => u.id === 1)).toBeUndefined()
      expect(store.deportistas).toHaveLength(1)
      expect(store.deportistas.find(d => d.id === 1)).toBeUndefined()
      expect(store.acudientes).toHaveLength(1)
      expect(store.acudientes.find(a => a.id === 1)).toBeUndefined()
      expect(store.entrenadores).toHaveLength(1)
      expect(store.entrenadores.find(e => e.id === 1)).toBeUndefined()
      expect(store.isLoading).toBe(false)
      expect(store.error).toBeNull()
    })

    it('should delete user from users list only if exists', async () => {
      usuariosService.eliminarUsuario.mockResolvedValue({})

      const store = useUserStore()
      store.users = [{ id: 1 }]
      store.deportistas = []
      store.acudientes = []
      store.entrenadores = []

      await store.deleteUser(1)

      expect(store.users.length).toBe(0)
    })

    it('should delete user from deportistas list only if exists', async () => {
      usuariosService.eliminarUsuario.mockResolvedValue({})

      const store = useUserStore()
      store.users = []
      store.deportistas = [{ id: 1 }]
      store.acudientes = []
      store.entrenadores = []

      await store.deleteUser(1)

      expect(store.deportistas.length).toBe(0)
    })

    it('should delete user from acudientes list only if exists', async () => {
      usuariosService.eliminarUsuario.mockResolvedValue({})

      const store = useUserStore()
      store.users = []
      store.deportistas = []
      store.acudientes = [{ id: 1 }]
      store.entrenadores = []

      await store.deleteUser(1)

      expect(store.acudientes.length).toBe(0)
    })

    it('should delete user from entrenadores list only if exists', async () => {
      usuariosService.eliminarUsuario.mockResolvedValue({})

      const store = useUserStore()
      store.users = []
      store.deportistas = []
      store.acudientes = []
      store.entrenadores = [{ id: 1 }]

      await store.deleteUser(1)

      expect(store.entrenadores.length).toBe(0)
    })

    it('should handle delete user error', async () => {
      const error = new Error('Delete failed')
      usuariosService.eliminarUsuario.mockRejectedValue(error)

      const store = useUserStore()
      store.users = [{ id: 1 }, { id: 2 }]
      const result = await store.deleteUser(1)

      expect(result.success).toBe(false)
      expect(result.error).toBe(error)
      expect(store.error).toBe('Delete failed')
      expect(store.users.length).toBe(2)
      expect(store.isLoading).toBe(false)
    })

    it('should handle delete user error without message', async () => {
      // NOSONAR: S7722 - Test requires error without message to verify fallback behavior
      const error = new Error()
      delete error.message
      usuariosService.eliminarUsuario.mockRejectedValue(error)

      const store = useUserStore()
      const result = await store.deleteUser(1)

      expect(result.success).toBe(false)
      expect(store.error).toBe('Error al eliminar usuario')
      expect(store.isLoading).toBe(false)
    })

    it('should set isLoading correctly during delete user', async () => {
      let isLoadingDuringDelete = false
      usuariosService.eliminarUsuario.mockImplementation(async () => {
        const store = useUserStore()
        isLoadingDuringDelete = store.isLoading
      })

      const store = useUserStore()
      await store.deleteUser(1)

      expect(isLoadingDuringDelete).toBe(true)
      expect(store.isLoading).toBe(false)
    })

    it('should clear error before deleting user', async () => {
      const store = useUserStore()
      store.error = 'Previous error'

      usuariosService.eliminarUsuario.mockResolvedValue({})
      await store.deleteUser(1)

      expect(store.error).toBeNull()
    })
  })

  describe('Search Users', () => {
    it('should search users by name', () => {
      const store = useUserStore()
      store.users = [
        { id: 1, persona: { nombre_completo: 'John Doe', correo_electronico: 'john@example.com' } },
        { id: 2, persona: { nombre_completo: 'Jane Smith', correo_electronico: 'jane@example.com' } }
      ]

      const results = store.searchUsers('John')
      expect(results).toHaveLength(1)
      expect(results[0].persona.nombre_completo).toBe('John Doe')
    })

    it('should return all users for empty query', () => {
      const store = useUserStore()
      store.users = [{ id: 1 }, { id: 2 }]

      const results = store.searchUsers('')
      expect(results).toHaveLength(2)
    })

    it('should return all users for null query', () => {
      const store = useUserStore()
      store.users = [{ id: 1 }, { id: 2 }]

      const results = store.searchUsers(null)
      expect(results).toHaveLength(2)
    })

    it('should search users by email', () => {
      const store = useUserStore()
      store.users = [
        { id: 1, persona: { nombre_completo: 'John Doe', correo_electronico: 'john@example.com' } },
        { id: 2, persona: { nombre_completo: 'Jane Smith', correo_electronico: 'jane@example.com' } }
      ]

      const results = store.searchUsers('jane@example.com')
      expect(results).toHaveLength(1)
      expect(results[0].persona.correo_electronico).toBe('jane@example.com')
    })

    it('should search users by documento', () => {
      const store = useUserStore()
      store.users = [
        { id: 1, persona: { nombre_completo: 'John Doe', documento: '1234567890' } },
        { id: 2, persona: { nombre_completo: 'Jane Smith', documento: '0987654321' } }
      ]

      const results = store.searchUsers('1234567890')
      expect(results).toHaveLength(1)
      expect(results[0].persona.documento).toBe('1234567890')
    })

    it('should be case-insensitive for name search', () => {
      const store = useUserStore()
      store.users = [
        { id: 1, persona: { nombre_completo: 'John Doe', correo_electronico: 'john@example.com' } }
      ]

      const results = store.searchUsers('JOHN')
      expect(results).toHaveLength(1)
    })

    it('should be case-insensitive for email search', () => {
      const store = useUserStore()
      store.users = [
        { id: 1, persona: { nombre_completo: 'John Doe', correo_electronico: 'John@Example.com' } }
      ]

      const results = store.searchUsers('john@example.com')
      expect(results).toHaveLength(1)
    })

    it('should handle users without persona object', () => {
      const store = useUserStore()
      store.users = [
        { id: 1, persona: null },
        { id: 2, persona: { nombre_completo: 'Jane Smith' } }
      ]

      const results = store.searchUsers('Jane')
      expect(results).toHaveLength(1)
      expect(results[0].id).toBe(2)
    })

    it('should handle users with incomplete persona data', () => {
      const store = useUserStore()
      store.users = [
        { id: 1, persona: { nombre_completo: 'John Doe' } },
        { id: 2, persona: {} }
      ]

      const results = store.searchUsers('John')
      expect(results).toHaveLength(1)
      expect(results[0].id).toBe(1)
    })
  })

  describe('Search Deportistas', () => {
    it('should return all deportistas for empty query', () => {
      const store = useUserStore()
      store.deportistas = [{ id: 1 }, { id: 2 }]

      const results = store.searchDeportistas('')
      expect(results).toHaveLength(2)
      expect(results).toEqual(store.deportistas)
    })

    it('should return all deportistas for null query', () => {
      const store = useUserStore()
      store.deportistas = [{ id: 1 }, { id: 2 }]

      const results = store.searchDeportistas(null)
      expect(results).toHaveLength(2)
      expect(results).toEqual(store.deportistas)
    })

    it('should search deportistas by nombre_completo', () => {
      const store = useUserStore()
      store.deportistas = [
        { id: 1, persona: { nombre_completo: 'Juan Pérez', correo_electronico: 'juan@example.com' } },
        { id: 2, persona: { nombre_completo: 'María García', correo_electronico: 'maria@example.com' } }
      ]

      const results = store.searchDeportistas('Juan')
      expect(results).toHaveLength(1)
      expect(results[0].persona.nombre_completo).toBe('Juan Pérez')
    })

    it('should search deportistas by correo_electronico', () => {
      const store = useUserStore()
      store.deportistas = [
        { id: 1, persona: { nombre_completo: 'Juan Pérez', correo_electronico: 'juan@example.com' } },
        { id: 2, persona: { nombre_completo: 'María García', correo_electronico: 'maria@example.com' } }
      ]

      const results = store.searchDeportistas('maria@example.com')
      expect(results).toHaveLength(1)
      expect(results[0].persona.correo_electronico).toBe('maria@example.com')
    })

    it('should search deportistas by documento', () => {
      const store = useUserStore()
      store.deportistas = [
        { id: 1, persona: { nombre_completo: 'Juan Pérez', documento: '1234567890' } },
        { id: 2, persona: { nombre_completo: 'María García', documento: '0987654321' } }
      ]

      const results = store.searchDeportistas('1234567890')
      expect(results).toHaveLength(1)
      expect(results[0].persona.documento).toBe('1234567890')
    })

    it('should be case-insensitive for name search', () => {
      const store = useUserStore()
      store.deportistas = [
        { id: 1, persona: { nombre_completo: 'Juan Pérez', correo_electronico: 'juan@example.com' } }
      ]

      const results = store.searchDeportistas('JUAN')
      expect(results).toHaveLength(1)
    })

    it('should be case-insensitive for email search', () => {
      const store = useUserStore()
      store.deportistas = [
        { id: 1, persona: { nombre_completo: 'Juan Pérez', correo_electronico: 'Juan@Example.com' } }
      ]

      const results = store.searchDeportistas('juan@example.com')
      expect(results).toHaveLength(1)
    })

    it('should handle deportistas without persona object', () => {
      const store = useUserStore()
      store.deportistas = [
        { id: 1, persona: null },
        { id: 2, persona: { nombre_completo: 'María García' } }
      ]

      const results = store.searchDeportistas('María')
      expect(results).toHaveLength(1)
      expect(results[0].id).toBe(2)
    })

    it('should handle deportistas with incomplete persona data', () => {
      const store = useUserStore()
      store.deportistas = [
        { id: 1, persona: { nombre_completo: 'Juan Pérez' } },
        { id: 2, persona: {} }
      ]

      const results = store.searchDeportistas('Juan')
      expect(results).toHaveLength(1)
      expect(results[0].id).toBe(1)
    })

    it('should return empty array when no matches found', () => {
      const store = useUserStore()
      store.deportistas = [
        { id: 1, persona: { nombre_completo: 'Juan Pérez' } }
      ]

      const results = store.searchDeportistas('NonExistent')
      expect(results).toHaveLength(0)
    })
  })

  describe('Get User By ID', () => {
    it('should get user by id', () => {
      const store = useUserStore()
      store.users = [{ id: 1, name: 'User 1' }, { id: 2, name: 'User 2' }]

      const user = store.getUserById(1)
      expect(user).toEqual({ id: 1, name: 'User 1' })
    })

    it('should return undefined for non-existent user', () => {
      const store = useUserStore()
      store.users = [{ id: 1 }]

      const user = store.getUserById(999)
      expect(user).toBeUndefined()
    })

    it('should return undefined when users array is empty', () => {
      const store = useUserStore()
      store.users = []

      const user = store.getUserById(1)
      expect(user).toBeUndefined()
    })
  })

  describe('Get Deportista By ID', () => {
    it('should get deportista by id', () => {
      const store = useUserStore()
      store.deportistas = [
        { id: 1, nombre: 'Deportista 1' },
        { id: 2, nombre: 'Deportista 2' }
      ]

      const deportista = store.getDeportistaById(1)
      expect(deportista).toEqual({ id: 1, nombre: 'Deportista 1' })
    })

    it('should return undefined for non-existent deportista', () => {
      const store = useUserStore()
      store.deportistas = [{ id: 1 }]

      const deportista = store.getDeportistaById(999)
      expect(deportista).toBeUndefined()
    })

    it('should return undefined when deportistas array is empty', () => {
      const store = useUserStore()
      store.deportistas = []

      const deportista = store.getDeportistaById(1)
      expect(deportista).toBeUndefined()
    })
  })

  describe('Get Acudiente By ID', () => {
    it('should get acudiente by id', () => {
      const store = useUserStore()
      store.acudientes = [
        { id: 1, nombre: 'Acudiente 1' },
        { id: 2, nombre: 'Acudiente 2' }
      ]

      const acudiente = store.getAcudienteById(1)
      expect(acudiente).toEqual({ id: 1, nombre: 'Acudiente 1' })
    })

    it('should return undefined for non-existent acudiente', () => {
      const store = useUserStore()
      store.acudientes = [{ id: 1 }]

      const acudiente = store.getAcudienteById(999)
      expect(acudiente).toBeUndefined()
    })

    it('should return undefined when acudientes array is empty', () => {
      const store = useUserStore()
      store.acudientes = []

      const acudiente = store.getAcudienteById(1)
      expect(acudiente).toBeUndefined()
    })
  })

  describe('Clear Error', () => {
    it('should clear error', () => {
      const store = useUserStore()
      store.error = 'Some error'

      store.clearError()

      expect(store.error).toBeNull()
    })

    it('should handle clearing null error', () => {
      const store = useUserStore()
      store.error = null

      store.clearError()

      expect(store.error).toBeNull()
    })
  })

  describe('Reset', () => {
    it('should reset store to initial state', () => {
      const store = useUserStore()
      store.users = [{ id: 1 }]
      store.deportistas = [{ id: 1 }]
      store.acudientes = [{ id: 1 }]
      store.entrenadores = [{ id: 1 }]
      store.isLoading = true
      store.error = 'Some error'

      store.reset()

      expect(store.users).toEqual([])
      expect(store.deportistas).toEqual([])
      expect(store.acudientes).toEqual([])
      expect(store.entrenadores).toEqual([])
      expect(store.isLoading).toBe(false)
      expect(store.error).toBeNull()
    })

    it('should reset all computed properties to 0', () => {
      const store = useUserStore()
      store.users = [{ id: 1 }, { id: 2 }]
      store.deportistas = [{ id: 1 }]
      store.acudientes = [{ id: 1 }, { id: 2 }, { id: 3 }]
      store.entrenadores = [{ id: 1 }]

      store.reset()

      expect(store.totalUsers).toBe(0)
      expect(store.totalDeportistas).toBe(0)
      expect(store.totalAcudientes).toBe(0)
      expect(store.totalEntrenadores).toBe(0)
    })
  })
})
