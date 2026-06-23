import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/visitor',
  },
  {
    path: '/visitor',
    name: 'Visitor',
    component: () => import('../views/VisitorView.vue'),
  },
  {
    path: '/admin',
    component: () => import('../views/AdminView.vue'),
    redirect: '/admin/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('../components/admin/DashboardPanel.vue'),
      },
      {
        path: 'interactions',
        name: 'Interactions',
        component: () => import('../components/admin/InteractionsPanel.vue'),
      },
      {
        path: 'knowledge',
        name: 'Knowledge',
        component: () => import('../components/admin/KnowledgePanel.vue'),
      },
      {
        path: 'report',
        name: 'Report',
        component: () => import('../components/admin/ReportPanel.vue'),
      },
      {
        path: 'digital-human',
        name: 'DigitalHumanConfig',
        component: () => import('../components/admin/DigitalHumanConfig.vue'),
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
