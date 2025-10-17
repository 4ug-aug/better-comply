/**
 * AppSidebar Component
 * Main sidebar navigation for the application
 */

import { Link, useLocation } from 'react-router-dom';
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from '@/components/ui/sidebar';
import { 
  ListChecks,
  Globe,
  LogOutIcon,
  Activity,
  FileText,
} from 'lucide-react';
import { ModeToggle } from '@/components/mode-toggle';
import { useAuth } from '@/context/AuthContext';
import { Button } from '@/components/ui/button';
// import { SettingsButton } from '@/components/settings-button';

/**
 * Navigation items for the sidebar
 */
const schedulingNavigationItems = [
  {
    title: "Subscriptions",
    url: "/subscriptions",
    icon: ListChecks,
    description: "Manage subscriptions"
  },
  {
    title: "Sources",
    url: "/sources",
    icon: Globe,
    description: "Manage content sources"
  },
  {
    title: "Observability",
    url: "/observability",
    icon: Activity,
    description: "Live dashboard"
  },
];

const documentsNavigationItems = [
  {
    title: "Documents",
    url: "/documents",
    icon: FileText,
    description: "Manage documents"
  },
];
/**
 * AppSidebar Component
 * @returns {JSX.Element} Sidebar component
 */
export function AppSidebar() {
  const location = useLocation();
  const { user, logout } = useAuth()

  /**
   * Check if a menu item is active
   * @param {string} url - URL to check
   * @returns {boolean} Whether the item is active
   */
  const isActive = (url: string) => {
    if (url === '/') {
      return location.pathname === '/';
    }
    return location.pathname.startsWith(url);
  };

  return (
    <Sidebar collapsible="icon">
      <SidebarHeader>
        <div className="flex items-center gap-2 px-2 py-2">
          <div className="flex flex-col">
            <span className="text-sm font-semibold">Better Comply</span>
            <span className="text-xs text-muted-foreground">Compliance Automation</span>
          </div>
        </div>
      </SidebarHeader>

      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>Documents</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {documentsNavigationItems.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton 
                    asChild 
                    isActive={isActive(item.url)}
                    tooltip={item.description}
                    className="text-sm"
                  >
                    <Link to={item.url}>
                      <item.icon className="h-4 w-4" />
                      <span>{item.title}</span>
                    </Link>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
        {/* Main Navigation */}
        <SidebarGroup>
          <SidebarGroupLabel>Scheduling</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {schedulingNavigationItems.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton 
                    asChild 
                    isActive={isActive(item.url)}
                    tooltip={item.description}
                    className="text-sm"
                  >
                    <Link to={item.url}>
                      <item.icon className="h-4 w-4" />
                      <span>{item.title}</span>
                    </Link>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

      </SidebarContent>

      <SidebarFooter>
        <div className="p-2 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-sm opacity-70">{user?.username}</span>
          </div>
          <div className="flex items-center gap-2 justify-between">
            {/* <SettingsButton isActive={isActive("/settings")} /> */}
            <ModeToggle />
            <Button variant="ghost" size="icon" onClick={logout}>
              <LogOutIcon className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </SidebarFooter>
    </Sidebar>
  );
}

export default AppSidebar;
