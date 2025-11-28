import { vi } from 'vitest'

/**
 * Mocks for services
 */

export const mockAuthService = {
  login: vi.fn(),
  register: vi.fn(),
  logout: vi.fn(),
  verifyToken: vi.fn(),
  getProfile: vi.fn(),
  getProfileDetail: vi.fn(),
  getUserPermissions: vi.fn(),
  getRolePermissions: vi.fn(),
  forgotPassword: vi.fn(),
  resetPassword: vi.fn(),
  updateUser: vi.fn(),
  getRoleOptions: vi.fn(),
  activateRole: vi.fn()
}

export const mockDeportistasService = {
  getAll: vi.fn(),
  getById: vi.fn(),
  create: vi.fn(),
  update: vi.fn(),
  delete: vi.fn()
}

export const mockMensualidadesService = {
  getAll: vi.fn(),
  getById: vi.fn(),
  create: vi.fn(),
  update: vi.fn()
}

export const mockPagosEfectivoService = {
  create: vi.fn(),
  getAll: vi.fn()
}

export const mockCalendarioService = {
  getAll: vi.fn(),
  getById: vi.fn(),
  create: vi.fn(),
  update: vi.fn(),
  delete: vi.fn()
}

export const mockGaleriaService = {
  getAll: vi.fn(),
  upload: vi.fn(),
  delete: vi.fn()
}

export const mockCatalogosService = {
  getAll: vi.fn(),
  getByType: vi.fn()
}

export const mockPersonasService = {
  getAll: vi.fn(),
  getById: vi.fn(),
  update: vi.fn()
}

export const mockUsuariosService = {
  getAll: vi.fn(),
  getById: vi.fn(),
  update: vi.fn(),
  delete: vi.fn()
}

