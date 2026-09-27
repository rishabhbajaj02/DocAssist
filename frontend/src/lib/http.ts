import { env } from '@/lib/env'
import { supabase } from '@/lib/supabase'

const TIMEOUT_MS = 15_000

export class ApiError extends Error {
  readonly status: number | null
  readonly isNetworkError: boolean

  constructor(
    message: string,
    status: number | null,
    isNetworkError: boolean,
  ) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.isNetworkError = isNetworkError
  }
}

export async function request<T>(
  method: string,
  path: string,
  body?: unknown,
): Promise<T> {
  const { data: { session } } = await supabase.auth.getSession()
  const headers = new Headers({ Accept: 'application/json' })
  if (body !== undefined) headers.set('Content-Type', 'application/json')
  if (session?.access_token) headers.set('Authorization', `Bearer ${session.access_token}`)

  let response: Response
  try {
    response = await fetch(`${env.apiBaseUrl}/${path.replace(/^\/+/, '')}`, {
      method,
      headers,
      body: body === undefined ? undefined : JSON.stringify(body),
      signal: AbortSignal.timeout(TIMEOUT_MS),
    })
  } catch (error) {
    throw new ApiError(
      error instanceof Error && error.name === 'TimeoutError'
        ? 'Request timed out'
        : 'Could not connect to the API',
      null,
      true,
    )
  }

  if (response.status === 204) return undefined as T

  const payload: unknown = await response.json()
  if (!response.ok) {
    const detail = typeof payload === 'object' && payload !== null && 'detail' in payload
      ? payload.detail
      : undefined
    throw new ApiError(
      typeof detail === 'string' ? detail : `Request failed (${response.status})`,
      response.status,
      false,
    )
  }
  return payload as T
}
