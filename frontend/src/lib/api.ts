import axios from 'axios'

export const api = axios.create({ baseURL: '/api' })

export const fetchJSON = async <T>(url: string, params?: Record<string, unknown>): Promise<T> => {
  const { data } = await api.get<T>(url, { params })
  return data
}
