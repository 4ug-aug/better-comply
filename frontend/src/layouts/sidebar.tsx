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
  Home, 
  FileStack,
  Building2,
} from 'lucide-react';
import { ModeToggle } from '@/components/mode-toggle';
// import { SettingsButton } from '@/components/settings-button';

/**
 * Navigation items for the sidebar
 */
const navigationItems = [
  {
    title: "Targets",
    url: "/",
    icon: Home,
    description: "Overview and targets"
  },
  {
    title: "Org Units",
    url: "/org-units",
    icon: Building2,
    description: "Manage organization units"
  },
  {
    title: "Scenarios",
    url: "/scenarios",
    icon: FileStack,
    description: "Generated scenarios"
  },
];

/**
 * AppSidebar Component
 * @returns {JSX.Element} Sidebar component
 */
export function AppSidebar() {
  const location = useLocation();

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
        {/* Main Navigation */}
        <SidebarGroup>
          <SidebarGroupLabel>Targets</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {navigationItems.map((item) => (
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
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <div className="h-2 w-2 rounded-full bg-green-500" />
            <span>System Online</span>
          </div>
          <div className="flex items-center gap-2 justify-between">
            {/* <SettingsButton isActive={isActive("/settings")} /> */}
            <ModeToggle />
          </div>
        </div>
      </SidebarFooter>
    </Sidebar>
  );
}

export default AppSidebar;
