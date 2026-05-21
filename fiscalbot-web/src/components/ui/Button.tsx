import type { ButtonHTMLAttributes } from 'react'

export default function Button({
  variant = 'primary',
  className = '',
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: 'primary' | 'ghost' | 'danger' }) {
  const base =
    'rounded-lg px-3 py-2 text-sm font-medium transition disabled:opacity-50 disabled:cursor-not-allowed'
  const variants = {
    primary: 'bg-emerald-600 hover:bg-emerald-500 text-white',
    ghost: 'border border-slate-700 hover:bg-slate-800 text-slate-200',
    danger: 'bg-red-700 hover:bg-red-600 text-white',
  }
  return <button className={`${base} ${variants[variant]} ${className}`} {...props} />
}
