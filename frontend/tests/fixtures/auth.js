/**
 * Fixtures for authentication tests
 */

export const mockUser = {
  id_usuario: 1,
  usuario: 'test@example.com',
  persona: {
    id_persona: 1,
    primer_nombre: 'Test',
    segundo_nombre: 'User',
    primer_apellido: 'Example',
    segundo_apellido: 'Test',
    correo_electronico: 'test@example.com',
    telefono: '1234567890',
    nombre_completo: 'Test User Example Test'
  },
  roles: ['Deportista'],
  roles_selector: {
    Deportista: true
  },
  paneles: ['deportista'],
  rol_activo: 'Deportista'
}

export const mockAdminUser = {
  id_usuario: 2,
  usuario: 'admin@example.com',
  persona: {
    id_persona: 2,
    primer_nombre: 'Admin',
    primer_apellido: 'User',
    correo_electronico: 'admin@example.com',
    nombre_completo: 'Admin User'
  },
  roles: ['Administrador'],
  roles_selector: {
    Administrador: true
  },
  paneles: ['admin'],
  rol_activo: 'Administrador'
}

export const mockToken = 'mock-jwt-token-12345'

export const mockLoginCredentials = {
  tipo_documento: 'CC',
  numero_documento: '1234567890',
  password: 'password123'
}

export const mockRegisterData = {
  tipo_documento: 'CC',
  numero_documento: '1234567890',
  primer_nombre: 'Test',
  segundo_nombre: 'User',
  primer_apellido: 'Example',
  segundo_apellido: 'Test',
  fecha_nacimiento: '2000-01-01',
  correo_electronico: 'test@example.com',
  telefono: '1234567890',
  password: 'password123',
  confirm_password: 'password123'
}

export const mockLoginResponse = {
  success: true,
  token: mockToken,
  user: mockUser
}

export const mockPermissions = [
  'ver_evento',
  'ver_calendario',
  'ver_perfil',
  'editar_perfil'
]

export const mockAdminPermissions = [
  'crear_evento',
  'editar_evento',
  'eliminar_evento',
  'ver_evento',
  'ver_calendario',
  'gestionar_usuarios',
  'acceso_panel_admin'
]

