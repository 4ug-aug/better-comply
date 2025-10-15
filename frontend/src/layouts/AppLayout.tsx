import React from 'react'
import {
  SidebarInset,
  SidebarProvider,
} from '@/components/ui/sidebar'
import Header from '@/components/layout/Header'
import { Outlet } from 'react-router-dom'
import { AppSidebar } from './sidebar'

const AppLayout: React.FC = () => {
  return (
    <SidebarProvider>
        <AppSidebar />
        <SidebarInset>
        <main className="flex-1">
            <div className="flex h-screen">
              {/* Main Content Area */}
              <div className="flex-1 flex flex-col overflow-hidden mt-2">
                {/* Page Content */}
                <div className="flex-1 overflow-auto pl-6 pr-4 border rounded-tl-2xl bg-center-background">
                  <Header />
                  <div className="p-4">
                    <Outlet />
                  </div>
                </div>
              </div>
            </div>
          </main>
        </SidebarInset>
    </SidebarProvider>
  );
};

export default AppLayout;
