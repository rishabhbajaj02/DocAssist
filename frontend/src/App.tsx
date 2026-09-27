import { useEffect, useState } from 'react'
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import type { Session } from '@supabase/supabase-js'
import { Button } from '@/components/ui/button'
import { supabase } from '@/lib/supabase'
import AuthPage from '@/pages/AuthPage'

function App() {
  const [session, setSession] = useState<Session | null | undefined>(undefined)

  useEffect(() => {
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, nextSession) => {
      setSession(nextSession)
    })
    return () => subscription.unsubscribe()
  }, [])

  if (session === undefined) {
    return <div className="grid min-h-screen place-items-center text-sm text-muted-foreground">Loading…</div>
  }

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/sign-in" element={session ? <Navigate to="/" replace /> : <AuthPage mode="sign-in" />} />
        <Route path="/sign-up" element={session ? <Navigate to="/" replace /> : <AuthPage mode="sign-up" />} />
        <Route path="/" element={session ? (
          <main className="mx-auto flex min-h-screen max-w-3xl flex-col justify-center gap-5 px-6 text-left">
            <p className="text-sm font-medium text-muted-foreground">DocAssist</p>
            <h1 className="text-4xl font-semibold tracking-tight">You're signed in.</h1>
            <p className="text-muted-foreground">Your document workspace is on its way.</p>
            <Button className="w-fit" variant="outline" onClick={() => void supabase.auth.signOut()}>Sign out</Button>
          </main>
        ) : <Navigate to="/sign-in" replace />} />
        <Route path="*" element={<Navigate to={session ? '/' : '/sign-in'} replace />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
