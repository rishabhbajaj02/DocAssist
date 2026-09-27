import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { useChat } from '@ai-sdk/react'
import { DefaultChatTransport, type UIMessage } from 'ai'
import { Button } from '@/components/ui/button'
import { api } from '@/lib/api'
import { env } from '@/lib/env'
import { supabase } from '@/lib/supabase'

type Thread = { id: string; title: string; created_at: string; updated_at: string }
type StoredMessage = { id: string; role: 'user' | 'assistant'; content: string; message_json: UIMessage | null }
type ThreadDetail = { thread: Thread; messages: StoredMessage[] }

function ChatConversation({ threadId, initialMessages, onComplete }: {
  threadId: string
  initialMessages: UIMessage[]
  onComplete: () => void
}) {
  const [input, setInput] = useState('')
  const { messages, sendMessage, status, error } = useChat({
    id: threadId,
    messages: initialMessages,
    transport: new DefaultChatTransport({
      api: `${env.apiBaseUrl}/chat/stream`,
      body: { threadId },
      headers: async () => {
        const { data: { session } } = await supabase.auth.getSession()
        const headers = new Headers()
        if (session) headers.set('Authorization', `Bearer ${session.access_token}`)
        return headers
      },
    }),
    onFinish: onComplete,
  })

  return <div className="flex min-h-0 flex-1 flex-col">
    <div className="flex-1 space-y-5 overflow-y-auto p-6" aria-live="polite">
      {messages.length === 0 && <p className="text-muted-foreground">Ask a question to start this chat.</p>}
      {messages.map(message => <div key={message.id} className={message.role === 'user' ? 'ml-auto max-w-[80%] rounded-2xl bg-primary p-4 text-primary-foreground' : 'max-w-[80%] rounded-2xl bg-muted p-4'}>
        <p className="mb-1 text-xs font-semibold uppercase opacity-70">{message.role}</p>
        {message.parts.filter(part => part.type === 'text').map((part, index) => <p key={index} className="whitespace-pre-wrap">{part.text}</p>)}
      </div>)}
      {status === 'streaming' && <p className="text-sm text-muted-foreground">Streaming response…</p>}
      {status === 'submitted' && <p className="text-sm text-muted-foreground">Thinking…</p>}
      {error && <p role="alert" className="text-sm text-destructive">{error.message}</p>}
    </div>
    <form className="flex gap-3 border-t p-4" onSubmit={event => {
      event.preventDefault()
      if (!input.trim() || status !== 'ready') return
      void sendMessage({ text: input.trim() })
      setInput('')
    }}>
      <input className="min-w-0 flex-1 rounded-md border bg-background px-3 py-2" aria-label="Message" placeholder="Ask about a filing…" value={input} onChange={event => setInput(event.target.value)} />
      <Button type="submit" disabled={!input.trim() || status !== 'ready'}>Send</Button>
    </form>
  </div>
}

export default function ChatPage() {
  const { threadId } = useParams()
  const navigate = useNavigate()
  const [threads, setThreads] = useState<Thread[]>([])
  const [detail, setDetail] = useState<ThreadDetail | null>(null)
  const [error, setError] = useState('')

  const refreshThreads = () => { void api.get<Thread[]>('/chat/threads').then(setThreads).catch(err => setError(String(err))) }

  useEffect(() => { refreshThreads() }, [])
  useEffect(() => {
    if (!threadId) return
    void api.get<ThreadDetail>(`/chat/threads/${threadId}`).then(setDetail).catch(err => setError(String(err)))
  }, [threadId])

  async function createThread() {
    try {
      const thread = await api.post<Thread>('/chat/threads')
      refreshThreads()
      navigate(`/chat/${thread.id}`)
    } catch (err) { setError(String(err)) }
  }

  const initialMessages: UIMessage[] = detail?.messages.map(message => ({
    id: message.id,
    role: message.role,
    parts: message.message_json?.parts ?? [{ type: 'text', text: message.content }],
  })) ?? []

  return <div className="flex h-screen bg-background text-foreground">
    <aside className="flex w-64 shrink-0 flex-col border-r p-4">
      <h1 className="mb-4 text-lg font-semibold">DocAssist</h1>
      <Button onClick={() => void createThread()}>New chat</Button>
      <nav className="mt-5 flex-1 space-y-1 overflow-y-auto" aria-label="Past conversations">
        {threads.map(thread => <Link key={thread.id} to={`/chat/${thread.id}`} className={`block truncate rounded-md px-3 py-2 text-sm hover:bg-muted ${thread.id === threadId ? 'bg-muted font-medium' : ''}`}>{thread.title}</Link>)}
        {threads.length === 0 && <p className="text-sm text-muted-foreground">No chats yet.</p>}
      </nav>
      <Button variant="outline" onClick={() => void supabase.auth.signOut()}>Sign out</Button>
    </aside>
    <main className="flex min-w-0 flex-1 flex-col">
      {error && <p role="alert" className="border-b p-4 text-destructive">{error}</p>}
      {threadId && (!detail || detail.thread.id !== threadId) ? <p className="p-6">Loading chat…</p> : threadId && detail ?
        <ChatConversation key={threadId} threadId={threadId} initialMessages={initialMessages} onComplete={refreshThreads} /> :
        <div className="grid flex-1 place-items-center text-muted-foreground">Choose a chat or start a new one.</div>}
    </main>
  </div>
}
