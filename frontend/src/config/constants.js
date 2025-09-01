// Archivo de constantes del proyecto
// Siguiendo el principio SRP - este archivo solo maneja constantes

export const APP_CONFIG = {
  name: 'ORION',
  fullName: 'Club Deportivo Puerta de Orión',
  description: 'Escuela de Voleibol - Excelencia • Pasión • Deporte',
  founded: 1999,
  contact: {
    phone: '+57 300 123 4567',
    email: 'info@puertadeorion.com',
    address: 'Calle Principal #123'
  }
}

export const NAVIGATION_ITEMS = [
  {
    id: 'calendario',
    title: 'Ver Calendario',
    route: '/calendario',
    icon: 'fas fa-calendar-alt',
    colorClass: 'nav-card--blue'
  },
  {
    id: 'galeria',
    title: 'Galería',
    route: '/galeria',
    icon: 'fas fa-images',
    colorClass: 'nav-card--gray'
  },
  {
    id: 'admin',
    title: 'Panel Admin',
    route: '/admin-manager',
    icon: 'fas fa-cog',
    colorClass: 'nav-card--red'
  },
  {
    id: 'deportistas',
    title: 'Deportistas',
    route: '/deportistas',
    icon: 'fas fa-users',
    colorClass: 'nav-card--green'
  }
]

export const CLUB_STATS = [
  { number: '12', label: 'Actividades' },
  { number: '3', label: 'Próximos Eventos' }
]

export const SOCIAL_LINKS = [
  { name: 'Facebook', icon: 'fab fa-facebook', url: '#' },
  { name: 'Instagram', icon: 'fab fa-instagram', url: '#' },
  { name: 'WhatsApp', icon: 'fab fa-whatsapp', url: '#' }
]

export const ROUTES = {
  home: '/',
  calendario: '/calendario',
  galeria: '/galeria',
  deportistas: '/deportistas',
  mensualidades: '/mensualidades',
  login: '/login',
  registro: '/roles-registro',
  admin: '/admin-manager'
}

