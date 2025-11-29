import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useFetch, usePaginatedFetch } from '@/composables/useFetch'

describe('useFetch', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('initial state', () => {
    it('should initialize with default values', () => {
      const { data, error, isLoading, isSuccess, hasError, hasData } = useFetch()

      expect(data.value).toBeNull()
      expect(error.value).toBeNull()
      expect(isLoading.value).toBe(false)
      expect(isSuccess.value).toBe(false)
      expect(hasError.value).toBe(false)
      expect(hasData.value).toBe(false)
    })
  })

  describe('execute', () => {
    it('should execute request successfully', async () => {
      const mockData = { id: 1, name: 'Test' }
      const requestFn = vi.fn().mockResolvedValueOnce(mockData)

      const { execute, data, isSuccess, isLoading } = useFetch()

      const result = await execute(requestFn)

      expect(result.success).toBe(true)
      expect(result.data).toEqual(mockData)
      expect(data.value).toEqual(mockData)
      expect(isSuccess.value).toBe(true)
      expect(isLoading.value).toBe(false)
      expect(requestFn).toHaveBeenCalled()
    })

    it('should handle request error', async () => {
      const error = new Error('Request failed')
      const requestFn = vi.fn().mockRejectedValueOnce(error)

      const { execute, error: errorRef, isSuccess, isLoading } = useFetch()

      const result = await execute(requestFn)

      expect(result.success).toBe(false)
      expect(result.error).toBe(error)
      expect(errorRef.value).toBe('Request failed')
      expect(isSuccess.value).toBe(false)
      expect(isLoading.value).toBe(false)
    })

    it('should call onSuccess callback', async () => {
      const mockData = { id: 1 }
      const requestFn = vi.fn().mockResolvedValueOnce(mockData)
      const onSuccess = vi.fn()

      const { execute } = useFetch()

      await execute(requestFn, { onSuccess })

      expect(onSuccess).toHaveBeenCalledWith(mockData)
    })

    it('should call onError callback', async () => {
      const error = new Error('Request failed')
      const requestFn = vi.fn().mockRejectedValueOnce(error)
      const onError = vi.fn()

      const { execute } = useFetch()

      await execute(requestFn, { onError })

      expect(onError).toHaveBeenCalledWith(error)
    })

    it('should reset data when resetData is true', async () => {
      const { execute, data, setData } = useFetch()

      setData({ id: 1 })
      expect(data.value).not.toBeNull()

      const requestFn = vi.fn().mockResolvedValueOnce({ id: 2 })
      await execute(requestFn, { resetData: true })

      expect(data.value).toEqual({ id: 2 })
    })

    it('should not reset data when resetData is false', async () => {
      const { execute, data, setData } = useFetch()

      setData({ id: 1 })
      const requestFn = vi.fn().mockResolvedValueOnce({ id: 2 })
      await execute(requestFn, { resetData: false })

      expect(data.value).toEqual({ id: 2 })
    })

    it('should not show loading when showLoading is false', async () => {
      const requestFn = vi.fn().mockResolvedValueOnce({})
      const { execute, isLoading } = useFetch()

      await execute(requestFn, { showLoading: false })

      expect(isLoading.value).toBe(false)
    })
  })

  describe('get', () => {
    it('should execute GET request', async () => {
      const mockData = { id: 1 }
      const getFn = vi.fn().mockResolvedValueOnce(mockData)

      const { get, data } = useFetch()

      await get(getFn)

      expect(data.value).toEqual(mockData)
    })
  })

  describe('post', () => {
    it('should execute POST request', async () => {
      const mockData = { id: 1 }
      const postFn = vi.fn().mockResolvedValueOnce(mockData)

      const { post, data } = useFetch()

      await post(postFn)

      expect(data.value).toEqual(mockData)
    })
  })

  describe('put', () => {
    it('should execute PUT request', async () => {
      const mockData = { id: 1, updated: true }
      const putFn = vi.fn().mockResolvedValueOnce(mockData)

      const { put, data } = useFetch()

      await put(putFn)

      expect(data.value).toEqual(mockData)
    })
  })

  describe('remove', () => {
    it('should execute DELETE request', async () => {
      const mockData = { deleted: true }
      const deleteFn = vi.fn().mockResolvedValueOnce(mockData)

      const { remove, data } = useFetch()

      await remove(deleteFn)

      expect(data.value).toEqual(mockData)
    })
  })

  describe('reset', () => {
    it('should reset all state', () => {
      const { reset, data, error, isLoading, isSuccess, setData, setError } = useFetch()

      setData({ id: 1 })
      setError('Some error')
      isLoading.value = true
      isSuccess.value = true

      reset()

      expect(data.value).toBeNull()
      expect(error.value).toBeNull()
      expect(isLoading.value).toBe(false)
      expect(isSuccess.value).toBe(false)
    })
  })

  describe('setError', () => {
    it('should set error manually', () => {
      const { setError, error, isSuccess } = useFetch()

      setError('Custom error')

      expect(error.value).toBe('Custom error')
      expect(isSuccess.value).toBe(false)
    })
  })

  describe('setData', () => {
    it('should set data manually', () => {
      const { setData, data, error, isSuccess } = useFetch()

      setData({ id: 1 })

      expect(data.value).toEqual({ id: 1 })
      expect(error.value).toBeNull()
      expect(isSuccess.value).toBe(true)
    })
  })
})

describe('usePaginatedFetch', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('initial state', () => {
    it('should initialize with pagination defaults', () => {
      const {
        currentPage,
        totalPages,
        totalItems,
        itemsPerPage,
        hasNextPage,
        hasPrevPage
      } = usePaginatedFetch()

      expect(currentPage.value).toBe(1)
      expect(totalPages.value).toBe(1)
      expect(totalItems.value).toBe(0)
      expect(itemsPerPage.value).toBe(10)
      expect(hasNextPage.value).toBe(false)
      expect(hasPrevPage.value).toBe(false)
    })
  })

  describe('fetchPage', () => {
    it('should fetch page and update currentPage', async () => {
      const mockData = [{ id: 1 }, { id: 2 }]
      const fetchFn = vi.fn().mockResolvedValueOnce(mockData)

      const { fetchPage, currentPage } = usePaginatedFetch()

      const result = await fetchPage(2, fetchFn)

      expect(currentPage.value).toBe(2)
      expect(result.success).toBe(true)
      expect(result.data).toEqual(mockData)
      expect(fetchFn).toHaveBeenCalledWith(2, 10)
    })
  })

  describe('nextPage', () => {
    it('should fetch next page when available', async () => {
      const mockData = [{ id: 3 }]
      const fetchFn = vi.fn().mockResolvedValueOnce(mockData)

      const { nextPage, currentPage, totalPages } = usePaginatedFetch()

      totalPages.value = 3
      currentPage.value = 1

      await nextPage(fetchFn)

      expect(currentPage.value).toBe(2)
      expect(fetchFn).toHaveBeenCalledWith(2, 10)
    })

    it('should not fetch when no next page', async () => {
      const fetchFn = vi.fn()

      const { nextPage, currentPage, totalPages } = usePaginatedFetch()

      totalPages.value = 2
      currentPage.value = 2

      await nextPage(fetchFn)

      expect(fetchFn).not.toHaveBeenCalled()
    })
  })

  describe('prevPage', () => {
    it('should fetch previous page when available', async () => {
      const mockData = [{ id: 1 }]
      const fetchFn = vi.fn().mockResolvedValueOnce(mockData)

      const { prevPage, currentPage } = usePaginatedFetch()

      currentPage.value = 2

      await prevPage(fetchFn)

      expect(currentPage.value).toBe(1)
      expect(fetchFn).toHaveBeenCalledWith(1, 10)
    })

    it('should not fetch when no previous page', async () => {
      const fetchFn = vi.fn()

      const { prevPage, currentPage } = usePaginatedFetch()

      currentPage.value = 1

      await prevPage(fetchFn)

      expect(fetchFn).not.toHaveBeenCalled()
    })
  })

  describe('paginatedData', () => {
    it('should return array when data is array', async () => {
      const { paginatedData, fetchPage } = usePaginatedFetch()

      // Use fetchPage which uses the correct execute internally
      const mockData = [{ id: 1 }, { id: 2 }]
      const fetchFn = vi.fn().mockResolvedValueOnce(mockData)
      await fetchPage(1, fetchFn)

      expect(paginatedData.value).toEqual([{ id: 1 }, { id: 2 }])
    })

    it('should return items when data has items property', async () => {
      const { paginatedData, fetchPage } = usePaginatedFetch()

      // Use fetchPage which uses the correct execute internally
      const mockData = { items: [{ id: 1 }], total: 1 }
      const fetchFn = vi.fn().mockResolvedValueOnce(mockData)
      await fetchPage(1, fetchFn)

      expect(paginatedData.value).toEqual([{ id: 1 }])
    })

    it('should return empty array when data is null', () => {
      const { paginatedData } = usePaginatedFetch()

      expect(paginatedData.value).toEqual([])
    })
  })

  describe('resetPagination', () => {
    it('should reset pagination state', async () => {
      const fetch = usePaginatedFetch()
      const { resetPagination, currentPage, totalPages, totalItems, fetchPage } = fetch

      // Set data using fetchPage which uses the correct execute
      const fetchFn = vi.fn().mockResolvedValueOnce([{ id: 1 }])
      await fetchPage(1, fetchFn)

      currentPage.value = 3
      totalPages.value = 5
      totalItems.value = 50

      resetPagination()

      expect(currentPage.value).toBe(1)
      expect(totalPages.value).toBe(1)
      expect(totalItems.value).toBe(0)
      // reset() should clear data - paginatedData should be empty
      expect(fetch.paginatedData.value).toEqual([])
    })
  })
})
