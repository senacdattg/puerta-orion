import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import TituloClub from '@/components/ui/titulo-club.vue'

// Mock fetch
globalThis.fetch = vi.fn()

describe('TituloClub Component', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should render the component', () => {
    const wrapper = mount(TituloClub)

    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('#titulo-club').exists()).toBe(true)
  })

  it('should render club title blocks', () => {
    const wrapper = mount(TituloClub)

    expect(wrapper.find('.bloque-amarillo').exists()).toBe(true)
    expect(wrapper.find('.bloque-azul').exists()).toBe(true)
  })

  it('should display correct text', () => {
    const wrapper = mount(TituloClub)

    expect(wrapper.find('.bloque-amarillo').text()).toBe('CLUB DEPORTIVO')
    expect(wrapper.find('.bloque-azul').text()).toBe('PUERTA DE ORIÓN')
  })

  it('should load external HTML when url prop is provided', async () => {
    const mockHtml = '<div>Custom HTML</div>'
    globalThis.fetch.mockResolvedValueOnce({
      text: async () => mockHtml
    })

    const wrapper = mount(TituloClub, {
      props: {
        url: 'https://example.com/logo.html'
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    expect(globalThis.fetch).toHaveBeenCalledWith('https://example.com/logo.html')
  })

  it('should handle fetch error gracefully', async () => {
    const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
    globalThis.fetch.mockRejectedValueOnce(new Error('Network error'))

    const wrapper = mount(TituloClub, {
      props: {
        url: 'https://example.com/logo.html'
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    expect(consoleErrorSpy).toHaveBeenCalled()
    consoleErrorSpy.mockRestore()
  })

  it('should not fetch when url prop is not provided', () => {
    mount(TituloClub)

    expect(globalThis.fetch).not.toHaveBeenCalled()
  })
})

