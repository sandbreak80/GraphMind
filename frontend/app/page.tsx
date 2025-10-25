'use client'

import { AuthWrapper } from '@/components/AuthWrapper'
import { UIEnhancements } from '@/components/UIEnhancements'

export default function Home() {
  // Just render the AuthWrapper - it will handle login/chat display
  // No need to redirect or create chats automatically
  return (
    <>
      <UIEnhancements />
      <AuthWrapper />
    </>
  )
}