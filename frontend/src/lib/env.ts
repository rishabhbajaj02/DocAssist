function required(name: string, value: unknown): string {
  if (typeof value !== 'string' || !value.trim()) {
    throw new Error(`Missing required environment variable: ${name}`)
  }
  return value.trim()
}

function requiredUrl(name: string, value: unknown): string {
  const raw = required(name, value)
  try {
    const url = new URL(raw)
    if (url.protocol === 'http:' || url.protocol === 'https:') {
      return url.toString().replace(/\/$/, '')
    }
  } catch {
    // Report the variable name rather than the configured value.
  }
  throw new Error(`Invalid URL in environment variable: ${name}`)
}

export const env = {
  apiBaseUrl: requiredUrl('VITE_API_BASE_URL', import.meta.env.VITE_API_BASE_URL),
  supabaseUrl: requiredUrl('VITE_SUPABASE_URL', import.meta.env.VITE_SUPABASE_URL),
  supabaseAnonKey: required('VITE_SUPABASE_ANON_KEY', import.meta.env.VITE_SUPABASE_ANON_KEY),
} as const
