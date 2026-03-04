import {
  LayoutDashboard,
  Settings,
} from 'lucide-react'

import Dashboard from '../pages/Dashboard'
import SettingsPage from '../pages/Settings'

export const coreRoutes = [
  {
    id: 'dashboard',
    path: '/',
    label: 'Dashboard',
    icon: LayoutDashboard,
    component: Dashboard,
    getProps: ({ status, loading }) => ({ status, loading }),
    sidebar: true,
  },
  {
    id: 'settings',
    path: '/settings',
    label: 'Settings',
    icon: Settings,
    component: SettingsPage,
    getProps: () => ({}),
    sidebar: true,
  },
]

export const coreExternalLinks = []
