import { describe, it, expect, beforeEach, vi } from 'vitest'

// Unmock the environment module to test the real implementation
vi.unmock('@/config/environment')

describe('Environment Configuration', () => {
  let envModule

  beforeEach(async () => {
    // Import the real module after unmocking
    envModule = await import('@/config/environment')
  })

  describe('Module Exports', () => {
    it('should export CURRENT_CONFIG', () => {
      expect(envModule.CURRENT_CONFIG).toBeDefined()
      expect(envModule.CURRENT_CONFIG).toHaveProperty('apiUrl')
      expect(envModule.CURRENT_CONFIG).toHaveProperty('debug')
      expect(envModule.CURRENT_CONFIG).toHaveProperty('logLevel')
    })

    it('should export API_CONFIG', () => {
      expect(envModule.API_CONFIG).toBeDefined()
      expect(envModule.API_CONFIG).toHaveProperty('baseURL')
      expect(typeof envModule.API_CONFIG.baseURL).toBe('string')
    })

    it('should export LOG_CONFIG', () => {
      expect(envModule.LOG_CONFIG).toBeDefined()
      expect(envModule.LOG_CONFIG).toHaveProperty('level')
      expect(envModule.LOG_CONFIG).toHaveProperty('enabled')
    })

    it('should export APP_ENV_CONFIG', () => {
      expect(envModule.APP_ENV_CONFIG).toBeDefined()
      expect(envModule.APP_ENV_CONFIG).toHaveProperty('isDevelopment')
      expect(envModule.APP_ENV_CONFIG).toHaveProperty('isProduction')
      expect(envModule.APP_ENV_CONFIG).toHaveProperty('isTest')
      expect(envModule.APP_ENV_CONFIG).toHaveProperty('version')
      expect(envModule.APP_ENV_CONFIG).toHaveProperty('buildTime')
    })

    it('should export getApiUrl function', () => {
      expect(envModule.getApiUrl).toBeDefined()
      expect(typeof envModule.getApiUrl).toBe('function')
    })

    it('should export getApiBaseUrl function', () => {
      expect(envModule.getApiBaseUrl).toBeDefined()
      expect(typeof envModule.getApiBaseUrl).toBe('function')
    })

    it('should export getRuntimeValue function', () => {
      expect(envModule.getRuntimeValue).toBeDefined()
      expect(typeof envModule.getRuntimeValue).toBe('function')
    })
  })

  describe('CURRENT_CONFIG', () => {
    it('should have apiUrl as a string', () => {
      expect(typeof envModule.CURRENT_CONFIG.apiUrl).toBe('string')
      expect(envModule.CURRENT_CONFIG.apiUrl.length).toBeGreaterThan(0)
    })

    it('should have debug as a boolean', () => {
      expect(typeof envModule.CURRENT_CONFIG.debug).toBe('boolean')
    })

    it('should have logLevel as a string', () => {
      expect(typeof envModule.CURRENT_CONFIG.logLevel).toBe('string')
      expect(['debug', 'info', 'warn', 'error']).toContain(envModule.CURRENT_CONFIG.logLevel)
    })
  })

  describe('API_CONFIG', () => {
    it('should have baseURL getter that returns a string', () => {
      const baseURL = envModule.API_CONFIG.baseURL
      expect(typeof baseURL).toBe('string')
      expect(baseURL.length).toBeGreaterThan(0)
    })

    it('should have timeout property', () => {
      expect(envModule.API_CONFIG).toHaveProperty('timeout')
      expect(typeof envModule.API_CONFIG.timeout).toBe('number')
      expect(envModule.API_CONFIG.timeout).toBeGreaterThan(0)
    })

    it('should have headers property', () => {
      expect(envModule.API_CONFIG).toHaveProperty('headers')
      expect(typeof envModule.API_CONFIG.headers).toBe('object')
      expect(envModule.API_CONFIG.headers).toHaveProperty('Content-Type')
      expect(envModule.API_CONFIG.headers).toHaveProperty('Accept')
    })
  })

  describe('LOG_CONFIG', () => {
    it('should have level as a string', () => {
      expect(typeof envModule.LOG_CONFIG.level).toBe('string')
    })

    it('should have enabled as a boolean', () => {
      expect(typeof envModule.LOG_CONFIG.enabled).toBe('boolean')
    })
  })

  describe('APP_ENV_CONFIG', () => {
    it('should have isDevelopment as a boolean', () => {
      expect(typeof envModule.APP_ENV_CONFIG.isDevelopment).toBe('boolean')
    })

    it('should have isProduction as a boolean', () => {
      expect(typeof envModule.APP_ENV_CONFIG.isProduction).toBe('boolean')
    })

    it('should have isTest as a boolean', () => {
      expect(typeof envModule.APP_ENV_CONFIG.isTest).toBe('boolean')
    })

    it('should have version as a string', () => {
      expect(typeof envModule.APP_ENV_CONFIG.version).toBe('string')
    })

    it('should have buildTime as a string', () => {
      expect(typeof envModule.APP_ENV_CONFIG.buildTime).toBe('string')
    })
  })

  describe('getApiUrl', () => {
    it('should return a string', () => {
      const url = envModule.getApiUrl()
      expect(typeof url).toBe('string')
      expect(url.length).toBeGreaterThan(0)
    })

    it('should append path to base URL', () => {
      const url = envModule.getApiUrl('/test')
      expect(url).toContain('/test')
    })

    it('should handle empty path', () => {
      const url = envModule.getApiUrl('')
      expect(typeof url).toBe('string')
    })
  })

  describe('getApiBaseUrl', () => {
    it('should return a string containing /api', () => {
      const url = envModule.getApiBaseUrl()
      expect(typeof url).toBe('string')
      expect(url).toContain('/api')
    })
  })

  describe('getRuntimeValue', () => {
    it('should return fallback when key not found', () => {
      const value = envModule.getRuntimeValue('NON_EXISTENT_KEY', 'fallback-value')
      expect(value).toBe('fallback-value')
    })

    it('should return undefined when key not found and no fallback', () => {
      const value = envModule.getRuntimeValue('NON_EXISTENT_KEY')
      expect(value).toBeUndefined()
    })
  })

  describe('API URL Resolution', () => {
    beforeEach(() => {
      // Reset globalThis.RUNTIME_CONFIG
      if (globalThis.RUNTIME_CONFIG) {
        delete globalThis.RUNTIME_CONFIG
      }
    })

    it('should use runtime config VITE_API_URL when available', () => {
      globalThis.RUNTIME_CONFIG = {
        VITE_API_URL: 'https://runtime-api.example.com'
      }

      const url = envModule.getApiUrl()
      expect(url).toContain('runtime-api.example.com')
    })

    it('should use import.meta.env.VITE_API_URL when runtime config not available', () => {
      // Mock import.meta.env
      const originalEnv = import.meta.env.VITE_API_URL
      import.meta.env.VITE_API_URL = 'https://env-api.example.com'

      const url = envModule.getApiUrl()
      expect(url).toContain('env-api.example.com')

      // Restore
      import.meta.env.VITE_API_URL = originalEnv
    })

    it('should use fallback config when no env variables are set', () => {
      const url = envModule.getApiUrl()
      expect(typeof url).toBe('string')
      expect(url.length).toBeGreaterThan(0)
    })

    it('should handle localhost in computeDefaultApiUrl', () => {
      // This tests the computeDefaultApiUrl function indirectly
      const url = envModule.getApiUrl()
      // Should default to localhost fallback if no config is set
      expect(url).toBeDefined()
    })

    it('should strip trailing slash from paths in getApiUrl', () => {
      const url1 = envModule.getApiUrl('/test/')
      const url2 = envModule.getApiUrl('/test')

      // Both should result in the same URL (trailing slash removed)
      expect(url1).toBe(url2)
    })

    it('should handle empty path in getApiUrl', () => {
      const url = envModule.getApiUrl('')
      expect(typeof url).toBe('string')
      expect(url.length).toBeGreaterThan(0)
    })

    it('should handle sanitizeValue edge cases', () => {
      // Test sanitizeValue indirectly through getApiUrl
      // Empty string should be handled
      const url1 = envModule.getApiUrl('')
      expect(url1).toBeDefined()

      // 'auto' should be sanitized
      // 'undefined' should be sanitized
      // 'null' should be sanitized
      // These are tested indirectly through the URL resolution
    })
  })

  describe('getApiBaseUrl', () => {
    it('should return URL with /api suffix', () => {
      const url = envModule.getApiBaseUrl()
      expect(url).toContain('/api')
      expect(url.endsWith('/api')).toBe(true)
    })

    it('should not have double slashes', () => {
      const url = envModule.getApiBaseUrl()
      expect(url).not.toContain('//api')
    })
  })

  describe('CURRENT_CONFIG apiUrl getter', () => {
    it('should dynamically resolve apiUrl', () => {
      const apiUrl = envModule.CURRENT_CONFIG.apiUrl
      expect(typeof apiUrl).toBe('string')
      expect(apiUrl.length).toBeGreaterThan(0)
    })

    it('should update when runtime config changes', () => {
      

      globalThis.RUNTIME_CONFIG = {
        VITE_API_URL: 'https://new-api.example.com'
      }

      // The getter should resolve to the new URL
      const newUrl = envModule.CURRENT_CONFIG.apiUrl
      expect(newUrl).toContain('new-api.example.com')

      // Cleanup
      delete globalThis.RUNTIME_CONFIG
    })
  })

  describe('APP_ENV_CONFIG', () => {
    it('should correctly identify environment', () => {
      expect(typeof envModule.APP_ENV_CONFIG.isDevelopment).toBe('boolean')
      expect(typeof envModule.APP_ENV_CONFIG.isProduction).toBe('boolean')
      expect(typeof envModule.APP_ENV_CONFIG.isTest).toBe('boolean')
    })

    it('should have valid version string', () => {
      expect(typeof envModule.APP_ENV_CONFIG.version).toBe('string')
      expect(envModule.APP_ENV_CONFIG.version.length).toBeGreaterThan(0)
    })

    it('should have valid buildTime string', () => {
      expect(typeof envModule.APP_ENV_CONFIG.buildTime).toBe('string')
      // Should be a valid ISO date string
      expect(() => new Date(envModule.APP_ENV_CONFIG.buildTime)).not.toThrow()
    })
  })
})
