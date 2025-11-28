import { describe, it, expect, beforeEach, vi } from 'vitest'
import {
  formatDate,
  formatDateTime,
  calculateAge,
  isValidDate,
  capitalize,
  capitalizeWords,
  truncate,
  generateSlug,
  isValidEmail,
  isValidPhone,
  isValidDocument,
  hasRole,
  hasAnyRole,
  hasPermission,
  getPrimaryRole,
  formatCurrency,
  formatNumber,
  formatPercentage,
  removeDuplicates,
  groupBy,
  sortBy,
  deepClone,
  deepMerge,
  setStorage,
  getStorage,
  removeStorage,
  debounce,
  throttle,
  buildURL,
  getURLParams
} from '@/utils/helpers'
import { ROLES } from '@/config/constants'

describe('Helpers - Date Utilities', () => {
  describe('formatDate', () => {
    it('should format a valid date', () => {
      const date = new Date('2024-01-15')
      const formatted = formatDate(date)
      expect(formatted).toBeTruthy()
      expect(typeof formatted).toBe('string')
    })

    it('should return empty string for null date', () => {
      expect(formatDate(null)).toBe('')
    })

    it('should return empty string for invalid date', () => {
      expect(formatDate('invalid')).toBe('')
    })

    it('should format date string', () => {
      const formatted = formatDate('2024-01-15')
      expect(formatted).toBeTruthy()
    })
  })

  describe('formatDateTime', () => {
    it('should format date and time', () => {
      const date = new Date('2024-01-15T10:30:00')
      const formatted = formatDateTime(date)
      expect(formatted).toBeTruthy()
      expect(typeof formatted).toBe('string')
    })

    it('should return empty string for null date', () => {
      expect(formatDateTime(null)).toBe('')
    })
  })

  describe('calculateAge', () => {
    it('should calculate age correctly', () => {
      const birthDate = new Date('2000-01-01')
      const age = calculateAge(birthDate)
      expect(age).toBeGreaterThan(20)
      expect(age).toBeLessThan(30)
    })

    it('should return 0 for null date', () => {
      expect(calculateAge(null)).toBe(0)
    })

    it('should calculate age from string', () => {
      const age = calculateAge('2000-01-01')
      expect(age).toBeGreaterThan(20)
    })
  })

  describe('isValidDate', () => {
    it('should return true for valid date', () => {
      expect(isValidDate(new Date())).toBe(true)
      expect(isValidDate('2024-01-15')).toBe(true)
    })

    it('should return false for invalid date', () => {
      expect(isValidDate(null)).toBe(false)
      expect(isValidDate('invalid')).toBe(false)
    })
  })
})

describe('Helpers - String Utilities', () => {
  describe('capitalize', () => {
    it('should capitalize first letter', () => {
      expect(capitalize('hello')).toBe('Hello')
      expect(capitalize('HELLO')).toBe('Hello')
    })

    it('should return empty string for null', () => {
      expect(capitalize(null)).toBe('')
    })
  })

  describe('capitalizeWords', () => {
    it('should capitalize each word', () => {
      expect(capitalizeWords('hello world')).toBe('Hello World')
    })
  })

  describe('truncate', () => {
    it('should truncate long strings', () => {
      const long = 'a'.repeat(100)
      const truncated = truncate(long, 50)
      expect(truncated.length).toBe(53) // 50 + '...'
      expect(truncated).toContain('...')
    })

    it('should not truncate short strings', () => {
      expect(truncate('hello', 10)).toBe('hello')
    })
  })

  describe('generateSlug', () => {
    it('should generate slug from string', () => {
      expect(generateSlug('Hello World')).toBe('hello-world')
      expect(generateSlug('Test@#$%')).toBe('test')
    })

    it('should handle empty string', () => {
      expect(generateSlug('')).toBe('')
    })
  })
})

describe('Helpers - Validation Utilities', () => {
  describe('isValidEmail', () => {
    it('should validate correct emails', () => {
      expect(isValidEmail('test@example.com')).toBe(true)
      expect(isValidEmail('user.name@domain.co.uk')).toBe(true)
    })

    it('should reject invalid emails', () => {
      expect(isValidEmail('invalid')).toBe(false)
      expect(isValidEmail('test@')).toBe(false)
      expect(isValidEmail('@example.com')).toBe(false)
      expect(isValidEmail(null)).toBe(false)
    })
  })

  describe('isValidPhone', () => {
    it('should validate correct phones', () => {
      expect(isValidPhone('1234567890')).toBe(true)
      expect(isValidPhone('+57 300 123 4567')).toBe(true)
    })

    it('should reject invalid phones', () => {
      expect(isValidPhone('abc')).toBe(false)
      expect(isValidPhone(null)).toBe(false)
    })
  })

  describe('isValidDocument', () => {
    it('should validate cedula', () => {
      expect(isValidDocument('1234567890', 'cedula')).toBe(true)
      expect(isValidDocument('123456', 'cedula')).toBe(false)
    })

    it('should validate pasaporte', () => {
      expect(isValidDocument('AB123456', 'pasaporte')).toBe(true)
    })
  })
})

describe('Helpers - Role and Permission Utilities', () => {
  describe('hasRole', () => {
    it('should check if user has role', () => {
      const userRoles = ['Deportista', 'Acudiente']
      expect(hasRole(userRoles, 'Deportista')).toBe(true)
      expect(hasRole(userRoles, 'Administrador')).toBe(false)
    })

    it('should handle role objects', () => {
      const userRoles = [{ nombre_rol: 'Deportista' }]
      expect(hasRole(userRoles, 'Deportista')).toBe(true)
    })

    it('should return false for invalid input', () => {
      expect(hasRole(null, 'Deportista')).toBe(false)
      expect(hasRole([], 'Deportista')).toBe(false)
    })
  })

  describe('hasAnyRole', () => {
    it('should check if user has any role', () => {
      const userRoles = ['Deportista']
      expect(hasAnyRole(userRoles, ['Deportista', 'Admin'])).toBe(true)
      expect(hasAnyRole(userRoles, ['Admin', 'Entrenador'])).toBe(false)
    })
  })

  describe('getPrimaryRole', () => {
    it('should return primary role', () => {
      const userRoles = ['Deportista', 'Acudiente']
      expect(getPrimaryRole(userRoles)).toBe(ROLES.DEPORTISTA)
    })

    it('should return default role for empty array', () => {
      expect(getPrimaryRole([])).toBe(ROLES.USUARIO)
    })
  })
})

describe('Helpers - Formatting Utilities', () => {
  describe('formatCurrency', () => {
    it('should format currency', () => {
      const formatted = formatCurrency(1000, 'COP')
      expect(formatted).toContain('1')
    })

    it('should handle invalid numbers', () => {
      expect(formatCurrency(NaN)).toBe('$0')
    })
  })

  describe('formatNumber', () => {
    it('should format number', () => {
      expect(formatNumber(1000)).toBe('1.000')
    })
  })

  describe('formatPercentage', () => {
    it('should format percentage', () => {
      expect(formatPercentage(50)).toBe('50.0%')
    })
  })
})

describe('Helpers - Array Utilities', () => {
  describe('removeDuplicates', () => {
    it('should remove duplicates', () => {
      expect(removeDuplicates([1, 2, 2, 3])).toEqual([1, 2, 3])
    })

    it('should remove duplicates by key', () => {
      const arr = [{ id: 1 }, { id: 2 }, { id: 1 }]
      expect(removeDuplicates(arr, 'id')).toHaveLength(2)
    })
  })

  describe('groupBy', () => {
    it('should group array by key', () => {
      const arr = [
        { type: 'A', value: 1 },
        { type: 'B', value: 2 },
        { type: 'A', value: 3 }
      ]
      const grouped = groupBy(arr, 'type')
      expect(grouped.A).toHaveLength(2)
      expect(grouped.B).toHaveLength(1)
    })
  })

  describe('sortBy', () => {
    it('should sort array by key', () => {
      const arr = [{ name: 'B' }, { name: 'A' }, { name: 'C' }]
      const sorted = sortBy(arr, 'name', 'asc')
      expect(sorted[0].name).toBe('A')
    })
  })
})

describe('Helpers - Object Utilities', () => {
  describe('deepClone', () => {
    it('should deep clone object', () => {
      const obj = { a: { b: 1 } }
      const cloned = deepClone(obj)
      cloned.a.b = 2
      expect(obj.a.b).toBe(1)
    })

    it('should clone arrays', () => {
      const arr = [1, 2, 3]
      const cloned = deepClone(arr)
      cloned[0] = 10
      expect(arr[0]).toBe(1)
    })
  })
})

describe('Helpers - Storage Utilities', () => {
  beforeEach(() => {
    localStorage.clear()
    vi.clearAllMocks()
  })

  describe('setStorage', () => {
    it('should save to localStorage', () => {
      const result = setStorage('test', { key: 'value' })
      expect(result).toBe(true)
      // Verify the value was actually stored
      const stored = localStorage.getItem('test')
      expect(stored).toBeTruthy()
      expect(JSON.parse(stored)).toEqual({ key: 'value' })
    })
  })

  describe('getStorage', () => {
    it('should get from localStorage', () => {
      localStorage.setItem('test', JSON.stringify({ key: 'value' }))
      const result = getStorage('test')
      expect(result).toEqual({ key: 'value' })
    })

    it('should return default for missing key', () => {
      expect(getStorage('missing', 'default')).toBe('default')
    })
  })

  describe('removeStorage', () => {
    it('should remove from localStorage', () => {
      localStorage.setItem('test', 'value')
      expect(localStorage.getItem('test')).toBe('value')
      
      const result = removeStorage('test')
      expect(result).toBe(true)
      expect(localStorage.getItem('test')).toBeNull()
    })
  })
})

describe('Helpers - Function Utilities', () => {
  describe('debounce', () => {
    it('should debounce function calls', async () => {
      const fn = vi.fn()
      const debounced = debounce(fn, 100)
      
      debounced()
      debounced()
      debounced()
      
      await new Promise(resolve => setTimeout(resolve, 150))
      expect(fn).toHaveBeenCalledTimes(1)
    })
  })

  describe('throttle', () => {
    it('should throttle function calls', () => {
      const fn = vi.fn()
      const throttled = throttle(fn, 100)
      
      throttled()
      throttled()
      
      expect(fn).toHaveBeenCalledTimes(1)
    })
  })
})

describe('Helpers - URL Utilities', () => {
  describe('buildURL', () => {
    it('should build URL with params', () => {
      const url = buildURL('http://example.com', { key: 'value' })
      expect(url).toContain('key=value')
    })
  })

  describe('getURLParams', () => {
    it('should get URL params', () => {
      const params = getURLParams('http://example.com?key=value')
      expect(params.key).toBe('value')
    })
  })
})

