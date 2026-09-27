import { useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { supabase } from '@/lib/supabase'

type AuthMode = 'sign-in' | 'sign-up'

export default function AuthPage({ mode }: { mode: AuthMode }) {
  const navigate = useNavigate()
  const [pending, setPending] = useState(false)
  const [error, setError] = useState('')
  const [confirmation, setConfirmation] = useState('')
  const signingUp = mode === 'sign-up'

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (pending) return
    setError('')
    setConfirmation('')
    setPending(true)

    const form = new FormData(event.currentTarget)
    const email = String(form.get('email')).trim()
    const password = String(form.get('password'))

    try {
      if (signingUp) {
        const { data, error: authError } = await supabase.auth.signUp({ email, password })
        if (authError) throw authError
        if (data.session) navigate('/', { replace: true })
        else setConfirmation('Check your email for a confirmation link, then sign in.')
      } else {
        const { error: authError } = await supabase.auth.signInWithPassword({ email, password })
        if (authError) throw authError
        navigate('/', { replace: true })
      }
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'Authentication failed. Please try again.')
    } finally {
      setPending(false)
    }
  }

  return (
    <main className="grid min-h-screen bg-background px-5 py-12 text-left text-foreground md:grid-cols-2 md:px-0 md:py-0">
      <section className="hidden flex-col justify-between bg-slate-950 px-12 py-12 text-white md:flex lg:px-20">
        <p className="text-sm font-semibold tracking-tight">DocAssist</p>
        <div className="max-w-md">
          <div className="mb-10 h-px w-24 bg-sky-400" />
          <p className="text-4xl font-semibold leading-tight tracking-tight lg:text-5xl">Get to the source of every answer.</p>
          <p className="mt-5 text-base leading-relaxed text-slate-300">Ask questions across your documents and follow the evidence back to the page.</p>
        </div>
        <p className="text-sm text-slate-400">Answers grounded in your documents.</p>
      </section>
      <section className="flex items-center justify-center md:px-8">
        <div className="w-full max-w-sm">
          <p className="mb-10 text-sm font-semibold md:hidden">DocAssist</p>
          <h1 className="text-3xl font-semibold tracking-tight">{signingUp ? 'Create your account' : 'Welcome back'}</h1>
          <p className="mt-2 text-sm text-muted-foreground">{signingUp ? 'Use your email to get started.' : 'Sign in to continue to your documents.'}</p>
          <form className="mt-9 space-y-5" onSubmit={(event) => void handleSubmit(event)}>
            <div>
              <label htmlFor="email" className="mb-2 block text-sm font-medium">Email</label>
              <input id="email" name="email" type="email" autoComplete="email" required disabled={pending}
                className="h-11 w-full rounded-md border border-input bg-background px-3 text-sm outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:opacity-50" />
            </div>
            <div>
              <label htmlFor="password" className="mb-2 block text-sm font-medium">Password</label>
              <input id="password" name="password" type="password" autoComplete={signingUp ? 'new-password' : 'current-password'} required minLength={6} disabled={pending}
                className="h-11 w-full rounded-md border border-input bg-background px-3 text-sm outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:opacity-50" />
            </div>
            {error && <p role="alert" className="text-sm text-destructive">{error}</p>}
            {confirmation && <p role="status" className="text-sm text-foreground">{confirmation}</p>}
            <Button type="submit" disabled={pending || Boolean(confirmation)} className="h-11 w-full">
              {pending ? 'Please wait…' : signingUp ? 'Create account' : 'Sign in'}
            </Button>
          </form>
          <p className="mt-7 text-center text-sm text-muted-foreground">
            {signingUp ? 'Already have an account?' : 'New to DocAssist?'}{' '}
            <Link className="font-medium text-foreground underline underline-offset-4" to={signingUp ? '/sign-in' : '/sign-up'}>
              {signingUp ? 'Sign in' : 'Create an account'}
            </Link>
          </p>
        </div>
      </section>
    </main>
  )
}
