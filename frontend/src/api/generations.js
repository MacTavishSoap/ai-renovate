import http from './http'

export function createGeneration(data) {
  return http.post('/generations', data)
}

export function listGenerations(skip = 0, limit = 20) {
  return http.get('/generations', { params: { skip, limit } })
}

export function getGeneration(id) {
  return http.get(`/generations/${id}`)
}
