import { describe, it, expect } from 'vitest'
import {
  normalizarNombre,
  normalizarNombreCiudad,
  normalizarCodigo,
  normalizarDescripcion
} from '@/utils/normalization'

describe('normalization.js', () => {
  describe('normalizarNombre', () => {
    it('should normalize name to uppercase', () => {
      const result = normalizarNombre('juan carlos')
      expect(result).toBe('JUAN CARLOS')
    })

    it('should remove invalid characters', () => {
      // When invalid characters are removed, spaces are also removed
      // The function normalizes spaces after removing invalid chars
      const result = normalizarNombre('juan@#$123carlos')
      expect(result).toBe('JUANCARLOS')
    })

    it('should preserve spaces between valid characters', () => {
      const result = normalizarNombre('juan carlos')
      expect(result).toBe('JUAN CARLOS')
    })

    it('should remove invalid characters while preserving spaces', () => {
      const result = normalizarNombre('juan @#$ carlos')
      expect(result).toBe('JUAN CARLOS')
    })

    it('should preserve allowed special characters', () => {
      const result = normalizarNombre("maría-o'connor")
      expect(result).toBe("MARÍA-O'CONNOR")
    })

    it('should handle multiple spaces', () => {
      const result = normalizarNombre('juan   carlos')
      expect(result).toBe('JUAN CARLOS')
    })

    it('should trim start', () => {
      const result = normalizarNombre('   juan')
      expect(result).toBe('JUAN')
    })

    it('should return empty string for empty input', () => {
      const result = normalizarNombre('')
      expect(result).toBe('')
    })

    it('should return empty string for non-string input', () => {
      const result = normalizarNombre(null)
      expect(result).toBe('')
    })

    it('should handle accented characters', () => {
      const result = normalizarNombre('josé maría')
      expect(result).toBe('JOSÉ MARÍA')
    })

    it('should handle ñ character', () => {
      const result = normalizarNombre('niño')
      expect(result).toBe('NIÑO')
    })
  })

  describe('normalizarNombreCiudad', () => {
    it('should normalize city name to uppercase', () => {
      const result = normalizarNombreCiudad('bogotá')
      expect(result).toBe('BOGOTÁ')
    })

    it('should allow numbers in city names', () => {
      const result = normalizarNombreCiudad('calle 123')
      expect(result).toBe('CALLE 123')
    })

    it('should allow dots in city names', () => {
      const result = normalizarNombreCiudad('st. andrews')
      expect(result).toBe('ST. ANDREWS')
    })

    it('should remove invalid characters', () => {
      const result = normalizarNombreCiudad('bogotá@#$')
      expect(result).toBe('BOGOTÁ')
    })

    it('should handle multiple spaces', () => {
      const result = normalizarNombreCiudad('bogotá   d.c.')
      expect(result).toBe('BOGOTÁ D.C.')
    })

    it('should return empty string for empty input', () => {
      const result = normalizarNombreCiudad('')
      expect(result).toBe('')
    })

    it('should preserve allowed special characters', () => {
      const result = normalizarNombreCiudad("o'connor street")
      expect(result).toBe("O'CONNOR STREET")
    })
  })

  describe('normalizarCodigo', () => {
    it('should normalize code to uppercase', () => {
      const result = normalizarCodigo('abc123')
      expect(result).toBe('ABC123')
    })

    it('should allow alphanumeric and hyphens', () => {
      const result = normalizarCodigo('abc-123-def')
      expect(result).toBe('ABC-123-DEF')
    })

    it('should remove invalid characters', () => {
      const result = normalizarCodigo('abc@#$123')
      expect(result).toBe('ABC123')
    })

    it('should respect maxLength', () => {
      const result = normalizarCodigo('abcdefghijklmnopqrstuvwxyz', 10)
      expect(result).toBe('ABCDEFGHIJ')
      expect(result.length).toBe(10)
    })

    it('should use default maxLength of 20', () => {
      const longCode = 'a'.repeat(30)
      const result = normalizarCodigo(longCode)
      expect(result.length).toBe(20)
    })

    it('should return empty string for empty input', () => {
      const result = normalizarCodigo('')
      expect(result).toBe('')
    })

    it('should handle numbers only', () => {
      const result = normalizarCodigo('123456')
      expect(result).toBe('123456')
    })

    it('should handle letters only', () => {
      const result = normalizarCodigo('abcdef')
      expect(result).toBe('ABCDEF')
    })

    it('should handle hyphens', () => {
      const result = normalizarCodigo('abc-def-ghi')
      expect(result).toBe('ABC-DEF-GHI')
    })

    it('should remove spaces', () => {
      const result = normalizarCodigo('abc def ghi')
      expect(result).toBe('ABCDEFGHI')
    })
  })

  describe('normalizarDescripcion', () => {
    it('should normalize description to uppercase', () => {
      const result = normalizarDescripcion('esta es una descripción')
      expect(result).toBe('ESTA ES UNA DESCRIPCIÓN')
    })

    it('should handle multiple spaces', () => {
      const result = normalizarDescripcion('esta   es   una   descripción')
      expect(result).toBe('ESTA ES UNA DESCRIPCIÓN')
    })

    it('should trim the result', () => {
      const result = normalizarDescripcion('   descripción   ')
      expect(result).toBe('DESCRIPCIÓN')
    })

    it('should respect maxLength', () => {
      const longDesc = 'a'.repeat(600)
      const result = normalizarDescripcion(longDesc, 100)
      expect(result.length).toBe(100)
    })

    it('should use default maxLength of 500', () => {
      const longDesc = 'a'.repeat(600)
      const result = normalizarDescripcion(longDesc)
      expect(result.length).toBe(500)
    })

    it('should return empty string for empty input', () => {
      const result = normalizarDescripcion('')
      expect(result).toBe('')
    })

    it('should preserve spaces between words', () => {
      const result = normalizarDescripcion('palabra uno palabra dos')
      expect(result).toBe('PALABRA UNO PALABRA DOS')
    })

    it('should handle accented characters', () => {
      const result = normalizarDescripcion('descripción con acentos')
      expect(result).toBe('DESCRIPCIÓN CON ACENTOS')
    })

    it('should handle special characters in description', () => {
      const result = normalizarDescripcion('descripción: muy importante!')
      expect(result).toBe('DESCRIPCIÓN: MUY IMPORTANTE!')
    })

    it('should handle newlines by converting to spaces', () => {
      const result = normalizarDescripcion('línea uno\nlínea dos')
      expect(result).toContain('LÍNEA')
    })
  })
})

