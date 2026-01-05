/**
 * CampusAssetManager/frontend/src/router/index.js
 * Vue Router 路由配置文件
 * 
 * 功能说明：
 * - 配置应用路由
 * - 定义路由守卫
 * - 实现权限控制
 * 
 * 作者：CampusAssetManager开发团队
 * 日期：2026-01-05
 */

import { createRouter, createWebHistory } from 'vue-router'

/**
 * 路由配置数组
 */
const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/HomeView.vue'),
    meta: { title: '首页', requiresAuth: false }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/LoginView.vue'),
    meta: { title: '登录', requiresAuth: false }
  },
  {
    path: '/goods',
    name: 'Goods',
    component: () => import('@/views/GoodsView.vue'),
    meta: { title: '物品管理', requiresAuth: true }
  },
  {
    path: '/stock',
    name: 'Stock',
    component: () => import('@/views/StockView.vue'),
    meta: { title: '库存管理', requiresAuth: true }
  },
  {
    path: '/check',
    name: 'Check',
    component: () => import('@/views/CheckView.vue'),
    meta: { title: '盘点管理', requiresAuth: true }
  },
  {
    path: '/statistics',
    name: 'Statistics',
    component: () => import('@/views/StatisticsView.vue'),
    meta: { title: '统计报表', requiresAuth: true }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('@/views/SettingsView.vue'),
    meta: { title: '系统设置', requiresAuth: true }
  }
]

/**
 * 创建路由实例
 */
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

/**
 * 全局前置守卫
 * 用于验证用户权限
 */
router.beforeEach((to, from, next) => {
  // 设置页面标题
  document.title = `${to.meta.title || '校园物品管理系统'} - 校物通`
  
  // 检查是否需要认证
  if (to.meta.requiresAuth) {
    const token = localStorage.getItem('token')
    if (!token) {
      next({
        path: '/login',
        query: { redirect: to.fullPath }
      })
    } else {
      next()
    }
  } else {
    // 如果已登录且访问登录页，重定向到首页
    if (to.path === '/login' && localStorage.getItem('token')) {
      next('/')
    } else {
      next()
    }
  }
})

/**
 * 导出路由实例
 */
export default router