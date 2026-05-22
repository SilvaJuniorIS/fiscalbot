import { useState } from 'react'

type Toast = {
  type: 'success' | 'error'
  message: string
}

export function useToast() {
  const [toast, setToast] = useState<Toast | null>(null)

  function showToast(type: Toast['type'], message: string) {
    setToast({ type, message })
    window.setTimeout(() => setToast(null), 3500)
  }

  function ToastView() {
    if (!toast) return null
    const color = toast.type === 'success' ? 'border-emerald-500 text-emerald-200' : 'border-red-500 text-red-200'
    return (
      <div className={`fixed right-4 top-4 z-50 rounded-lg border bg-slate-950 px-4 py-3 text-sm shadow-xl ${color}`}>
        {toast.message}
      </div>
    )
  }

  return { showToast, ToastView }
}
