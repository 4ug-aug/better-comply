import React from 'react'
import { SidebarTrigger } from '@/components/ui/sidebar'
import { Button } from '@/components/ui/button'
import { useAuth } from '@/context/AuthContext'

const Header: React.FC = () => {
  const { user, logout } = useAuth()
  return (
    <header className="flex h-14 items-center gap-2 border-b px-4">
      <SidebarTrigger />
      <div className="font-semibold">Better Comply</div>
      <div className="ml-auto flex items-center gap-3">
        <span className="text-sm opacity-70">{user?.username}</span>
        <Button variant="outline" size="sm" onClick={logout}>Logout</Button>
      </div>
    </header>
  )
}

export default Header


