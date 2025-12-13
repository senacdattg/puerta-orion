import { describe, it, expect } from 'vitest'
import { parseISODateLocal, esFechaValida } from '@/utils/date-utils'

describe('date-utils.js', () => {
  describe('parseISODateLocal', () => {
    it('should return null for empty input', () => {
      const result = parseISODateLocal('')
      expect(result).toBeNull()
    })

    it('should return null for null input', () => {
      const result = parseISODateLocal(null)
      expect(result).toBeNull()
    })

    it('should return null for undefined input', () => {
      const result = parseISODateLocal(undefined)
      expect(result).toBeNull()
    })

    it('should parse date-only string (YYYY-MM-DD)', () => {
      const result = parseISODateLocal('2023-12-25')
      expect(result).toBeInstanceOf(Date)
      expect(result.getFullYear()).toBe(2023)
      expect(result.getMonth()).toBe(11) // Month is 0-indexed
      expect(result.getDate()).toBe(25)
    })

    it('should parse ISO date string', () => {
      const result = parseISODateLocal('2023-12-25T10:30:00Z')
      expect(result).toBeInstanceOf(Date)
      expect(result).not.toBeNull()
    })

    it('should return null for invalid date string', () => {
      const result = parseISODateLocal('invalid-date')
      expect(result).toBeNull()
    })

    it('should handle date string with time', () => {
      const result = parseISODateLocal('2023-12-25T14:30:00.000Z')
      expect(result).toBeInstanceOf(Date)
      expect(result).not.toBeNull()
    })

    it('should handle single digit months and days', () => {
      const result = parseISODateLocal('2023-01-05')
      expect(result).toBeInstanceOf(Date)
      expect(result.getMonth()).toBe(0) // January is 0
      expect(result.getDate()).toBe(5)
    })
  })

  describe('esFechaValida', () => {
    it('should return true for valid date string', () => {
      const result = esFechaValida('2023-12-25')
      expect(result).toBe(true)
    })

    it('should return true for valid ISO date string', () => {
      const result = esFechaValida('2023-12-25T10:30:00Z')
      expect(result).toBe(true)
    })

    it('should return false for empty string', () => {
      const result = esFechaValida('')
      expect(result).toBe(false)
    })

    it('should return false for null', () => {
      const result = esFechaValida(null)
      expect(result).toBe(false)
    })

    it('should return false for undefined', () => {
      const result = esFechaValida(undefined)
      expect(result).toBe(false)
    })

    it('should return false for invalid date string', () => {
      const result = esFechaValida('invalid-date')
      expect(result).toBe(false)
    })

    it('should return false for non-date string', () => {
      const result = esFechaValida('not-a-date')
      expect(result).toBe(false)
    })

    it('should return true for valid date in different format', () => {
      const result = esFechaValida('2023/12/25')
      // Date.parse can handle this format
      expect(result).toBe(true)
    })
  })
})

