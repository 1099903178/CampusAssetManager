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
import { useUserStore } from '@/stores'
import { getUserInfo } from '@/api/auth'

/**
 * 路由配置数组
 */
const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/LoginView.vue'),
    meta: { title: '登录', requiresAuth: false }
  },
  {
    path: '/',
    component: () => import('@/components/common/LayoutComponent.vue'),
    redirect: '/home',
    children: [
      {
        path: 'home',
        name: 'Home',
        component: () => import('@/views/HomeView.vue'),
        meta: { title: '首页', requiresAuth: true }
      },
      {
        path: 'goods',
        name: 'Goods',
        component: () => import('@/views/GoodsView.vue'),
        meta: { title: '物品管理', requiresAuth: true }
      },
      {
        path: 'category',
        name: 'Category',
        component: () => import('@/views/CategoryView.vue'),
        meta: { title: '物品分类管理', requiresAuth: true }
      },
      {
        path: 'stock',
        name: 'Stock',
        component: () => import('@/views/StockView.vue'),
        meta: { title: '库存管理', requiresAuth: true }
      },
      {
        path: 'check',
        name: 'Check',
        component: () => import('@/views/CheckView.vue'),
        meta: { title: '盘点管理', requiresAuth: true }
      },
      {
        path: 'ledger',
        name: 'Ledger',
        component: () => import('@/views/LedgerView.vue'),
        meta: { title: '库存台账', requiresAuth: true }
      },
      {
        path: 'statistics',
        name: 'Statistics',
        component: () => import('@/views/StatisticsView.vue'),
        meta: { title: '统计报表', requiresAuth: true }
      },
      {
        path: 'logs',
        name: 'Logs',
        component: () => import('@/views/LogsView.vue'),
        meta: { title: '操作日志', requiresAuth: true }
      },
      {
        path: 'users',
        name: 'Users',
        component: () => import('@/views/UsersView.vue'),
        meta: { title: '用户管理', requiresAuth: true }
      },
      {
        path: 'settings',
        name: 'Settings',
        component: () => import('@/views/SettingsView.vue'),
        meta: { title: '系统设置', requiresAuth: true }
      }
    ]
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
 *
 * 开发模式：临时禁用登录验证以便快速测试
 * 生产环境：请取消注释以启用登录验证
 */
router.beforeEach(async (to, from, next) => {
  // 设置页面标题
  document.title = `${to.meta.title || '校园物品管理系统'} - 校物通`
  
  const userStore = useUserStore()
  const token = localStorage.getItem('token')
  
  // ========== 生产模式：启用登录验证 ==========
  // 检查是否需要认证
  if (to.meta.requiresAuth) {
    if (!token) {
      next({
        path: '/login',
        query: { redirect: to.fullPath }
      })
      return
    }
    
    // 如果有token但没有用户信息，尝试获取用户信息
    if (token && !userStore.user) {
      try {
        const userInfo = await getUserInfo()
        userStore.setUser(userInfo)
        next()
        return
      } catch (error) {
        console.error('获取用户信息失败:', error)
        // 获取用户信息失败，清除token并跳转到登录页
        await userStore.logout()
        next({
          path: '/login',
          query: { redirect: to.fullPath }
        })
        return
      }
    }
    
    next()
  } else {
    // 如果已登录且访问登录页，重定向到首页
    if (to.path === '/login' && token) {
      next('/')
    } else {
      next()
    }
  }
  
  // ========== 开发模式：跳过登录验证（以下代码已注释）==========
  /*
  console.log(`[开发模式] 访问页面: ${to.path} (跳过登录验证)`)
  next()
  return
  */
})

/**
 * 导出路由实例
 */
export default router