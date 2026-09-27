import { useEffect, useState } from 'react'
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import type { Session } from '@supabase/supabase-js'
import { supabase } from '@/lib/supabase'
import AuthPage from '@/pages/AuthPage'
import ChatPage from '@/pages/chat/ChatPage'

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
        <Route path="/" element={<Navigate to={session ? '/chat' : '/sign-in'} replace />} />
        <Route path="/chat" element={session ? <ChatPage /> : <Navigate to="/sign-in" replace />} />
        <Route path="/chat/:threadId" element={session ? <ChatPage /> : <Navigate to="/sign-in" replace />} />
        <Route path="*" element={<Navigate to={session ? '/' : '/sign-in'} replace />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
