import { describe, it, expect, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useCounterStore } from '@/stores/counter'

describe('Counter Store', () => {
  beforeEach(() => {
    // Create a fresh pinia instance for each test
    setActivePinia(createPinia())
  })

  describe('Initial State', () => {
    it('should initialize with count 0', () => {
      const store = useCounterStore()
      expect(store.count).toBe(0)
    })

    it('should have doubleCount computed property', () => {
      const store = useCounterStore()
      expect(store.doubleCount).toBe(0)
    })
  })

  describe('increment', () => {
    it('should increment count by 1', () => {
      const store = useCounterStore()
      const initialCount = store.count
      
      store.increment()
      
      expect(store.count).toBe(initialCount + 1)
    })

    it('should increment count multiple times', () => {
      const store = useCounterStore()
      
      store.increment()
      store.increment()
      store.increment()
      
      expect(store.count).toBe(3)
    })
  })

  describe('doubleCount computed', () => {
    it('should return double of count when count is 0', () => {
      const store = useCounterStore()
      expect(store.doubleCount).toBe(0)
    })

    it('should return double of count when count is 1', () => {
      const store = useCounterStore()
      store.increment()
      expect(store.doubleCount).toBe(2)
    })

    it('should return double of count when count is 5', () => {
      const store = useCounterStore()
      store.count = 5
      expect(store.doubleCount).toBe(10)
    })

    it('should update when count changes', () => {
      const store = useCounterStore()
      
      expect(store.doubleCount).toBe(0)
      
      store.increment()
      expect(store.doubleCount).toBe(2)
      
      store.increment()
      expect(store.doubleCount).toBe(4)
      
      store.increment()
      expect(store.doubleCount).toBe(6)
    })
  })

  describe('Store Isolation', () => {
    it('should create independent store instances', () => {
      const store1 = useCounterStore()
      const store2 = useCounterStore()
      
      // Both should start at 0
      expect(store1.count).toBe(0)
      expect(store2.count).toBe(0)
      
      // Incrementing one should not affect the other
      store1.increment()
      expect(store1.count).toBe(1)
      expect(store2.count).toBe(1) // Same instance in Pinia
    })
  })

  describe('Edge Cases', () => {
    it('should handle negative count values', () => {
      const store = useCounterStore()
      store.count = -5
      expect(store.doubleCount).toBe(-10)
    })

    it('should handle large count values', () => {
      const store = useCounterStore()
      store.count = 1000
      expect(store.doubleCount).toBe(2000)
    })
  })
})

