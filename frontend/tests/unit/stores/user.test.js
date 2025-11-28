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
    })

    it('should handle fetch error', async () => {
      usuariosService.obtenerUsuarios.mockRejectedValue(new Error('Network error'))

      const store = useUserStore()
      const result = await store.fetchUsers()

      expect(result.success).toBe(false)
      expect(store.error).toBeTruthy()
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
    })
  })

  describe('Create Deportista', () => {
    it('should create deportista successfully', async () => {
      const newDeportista = { id: 1, nombre: 'New Deportista' }
      usuariosService.crearDeportista.mockResolvedValue({
        data: newDeportista
      })

      const store = useUserStore()
      const result = await store.createDeportista({ nombre: 'New Deportista' })

      expect(result.success).toBe(true)
      expect(store.deportistas).toContainEqual(newDeportista)
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
    })
  })

  describe('Delete User', () => {
    it('should delete user successfully', async () => {
      usuariosService.eliminarUsuario.mockResolvedValue({})

      const store = useUserStore()
      store.users = [{ id: 1 }, { id: 2 }]
      const result = await store.deleteUser(1)

      expect(result.success).toBe(true)
      expect(store.users).toHaveLength(1)
      expect(store.users.find(u => u.id === 1)).toBeUndefined()
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
  })

  describe('Reset', () => {
    it('should reset store to initial state', () => {
      const store = useUserStore()
      store.users = [{ id: 1 }]
      store.deportistas = [{ id: 1 }]
      store.isLoading = true
      store.error = 'Some error'

      store.reset()

      expect(store.users).toEqual([])
      expect(store.deportistas).toEqual([])
      expect(store.isLoading).toBe(false)
      expect(store.error).toBeNull()
    })
  })
})

