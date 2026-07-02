import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'home',
    component: () => import('@/components/HomePage.vue'),
    meta: { title: '面试虎' }
  },
  {
    path: '/interview',
    name: 'interview',
    component: () => import('@/components/InterviewPage.vue'),
    meta: { title: '面试中 - 面试虎' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to) => {
  document.title = (to.meta.title as string) || '面试虎'
})

export default router
