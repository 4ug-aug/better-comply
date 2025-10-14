import React from 'react'
import {
  Sidebar,
  SidebarContent,
  SidebarHeader,
  SidebarInset,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarProvider,
  SidebarSeparator,
} from '@/components/ui/sidebar'
import Header from '@/components/layout/Header'
import { Outlet, NavLink } from 'react-router-dom'

const AppLayout: React.FC = () => {
  return (
    <SidebarProvider>
      <div className="flex min-h-svh">
        <Sidebar>
          <SidebarHeader className="font-semibold">Navigation</SidebarHeader>
          <SidebarContent>
            <SidebarMenu>
              <SidebarMenuItem>
                <SidebarMenuButton asChild isActive>
                  <NavLink to="/">Dashboard</NavLink>
                </SidebarMenuButton>
              </SidebarMenuItem>
            </SidebarMenu>
            <SidebarSeparator />
          </SidebarContent>
        </Sidebar>
        <SidebarInset>
          <Header />
          <div className="p-4">
            <Outlet />
          </div>
        </SidebarInset>
      </div>
    </SidebarProvider>
  )
}

export default AppLayout


