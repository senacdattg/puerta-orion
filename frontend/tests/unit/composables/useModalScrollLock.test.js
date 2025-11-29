import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { ref } from 'vue'
import { useModalScrollLock } from '@/composables/useModalScrollLock'

describe('useModalScrollLock', () => {
  let mostrar
  let originalBodyClassList
  let originalDocumentElementClassList
  let originalBodyStyle
  let originalDocumentElementStyle

  beforeEach(() => {
    mostrar = ref(false)

    // Save original values
    originalBodyClassList = document.body.classList
    originalDocumentElementClassList = document.documentElement.classList
    originalBodyStyle = document.body.style
    originalDocumentElementStyle = document.documentElement.style

    // Mock window methods
    global.window.scrollTo = vi.fn()
    global.window.pageYOffset = 100
    global.document.documentElement.scrollTop = 100
    global.document.body.scrollTop = 100

    // Mock getComputedStyle
    global.window.getComputedStyle = vi.fn(() => ({
      scrollBehavior: 'smooth'
    }))

    // Mock requestAnimationFrame
    global.requestAnimationFrame = vi.fn((callback) => {
      callback()
      return 1
    })
  })

  afterEach(() => {
    // Clean up
    document.body.classList.remove('modal-open')
    document.documentElement.classList.remove('modal-open')
    document.body.style.top = ''
    document.documentElement.style.scrollBehavior = ''
    document.body.style.scrollBehavior = ''
  })

  it('should add modal-open class when mostrar is true', () => {
    useModalScrollLock(mostrar)

    mostrar.value = true

    // Wait for watch to execute
    vi.waitFor(() => {
      expect(document.body.classList.contains('modal-open')).toBe(true)
      expect(document.documentElement.classList.contains('modal-open')).toBe(true)
    })
  })

  it('should set body top position when modal opens', () => {
    global.window.pageYOffset = 200

    useModalScrollLock(mostrar)

    mostrar.value = true

    vi.waitFor(() => {
      expect(document.body.style.top).toBe('-200px')
    })
  })

  it('should remove modal-open class when mostrar is false', () => {
    useModalScrollLock(mostrar)

    mostrar.value = true
    vi.waitFor(() => {
      expect(document.body.classList.contains('modal-open')).toBe(true)
    })

    mostrar.value = false
    vi.waitFor(() => {
      expect(document.body.classList.contains('modal-open')).toBe(false)
      expect(document.documentElement.classList.contains('modal-open')).toBe(false)
    })
  })

  it('should restore scroll position when modal closes', () => {
    global.window.pageYOffset = 150

    useModalScrollLock(mostrar)

    mostrar.value = true
    vi.waitFor(() => {
      expect(document.body.style.top).toBe('-150px')
    })

    mostrar.value = false
    vi.waitFor(() => {
      expect(global.window.scrollTo).toHaveBeenCalledWith({
        top: 150,
        left: 0,
        behavior: 'auto'
      })
    })
  })

  it('should restore scroll behavior after closing modal', () => {
    document.documentElement.style.scrollBehavior = 'smooth'

    useModalScrollLock(mostrar)

    mostrar.value = true
    vi.waitFor(() => {
      expect(document.documentElement.style.scrollBehavior).toBe('auto')
    })

    mostrar.value = false
    vi.waitFor(() => {
      // After requestAnimationFrame callbacks
      expect(document.documentElement.style.scrollBehavior).toBe('smooth')
    })
  })

  it('should clean up on unmount', () => {
    const { onUnmounted } = require('vue')
    const cleanup = vi.fn()

    useModalScrollLock(mostrar)

    mostrar.value = true
    vi.waitFor(() => {
      expect(document.body.classList.contains('modal-open')).toBe(true)
    })

    // Simulate unmount
    onUnmounted()

    expect(document.body.classList.contains('modal-open')).toBe(false)
    expect(document.documentElement.classList.contains('modal-open')).toBe(false)
    expect(document.body.style.top).toBe('')
  })

  it('should handle multiple requestAnimationFrame calls', () => {
    let callCount = 0
    global.requestAnimationFrame = vi.fn((callback) => {
      callCount++
      if (callCount === 1) {
        callback()
        return 1
      } else if (callCount === 2) {
        callback()
        return 2
      }
      return callCount
    })

    useModalScrollLock(mostrar)

    mostrar.value = true
    mostrar.value = false

    vi.waitFor(() => {
      expect(global.requestAnimationFrame).toHaveBeenCalled()
    })
  })
})

