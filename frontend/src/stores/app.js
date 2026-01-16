/**
 * CampusAssetManager/frontend/src/stores/app.js
 * 应用全局状态管理 Store
 * 
 * 功能说明：
 * - 管理应用全局状态
 * - 处理设备类型（移动端/PC端）
 * - 管理侧边栏状态
 * - 管理加载状态
 * 
 * 作者：CampusAssetManager开发团队
 * 日期：2026-01-05
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

/**
 * 应用状态管理Store
 */
export const useAppStore = defineStore('app', () => {
  // ========== 状态定义 ==========
  
  /**
   * 设备类型：mobile 或 desktop
   */
  const device = ref('desktop')
  
  /**
   * 侧边栏是否折叠
   */
  const sidebarCollapsed = ref(false)
  
  /**
   * 全局加载状态
   */
  const loading = ref(false)
  
  /**
   * 当前页面标题
   */
  const pageTitle = ref('')
  
  // ========== 计算属性 ==========
  
  /**
   * 是否为移动端设备
   */
  const isMobile = computed(() => {
    return device.value === 'mobile'
  })
  
  /**
   * 是否为PC端设备
   */
  const isDesktop = computed(() => {
    return device.value === 'desktop'
  })
  
  // ========== Actions ==========
  
  /**
   * 切换侧边栏状态
   */
  const toggleSidebar = () => {
    sidebarCollapsed.value = !sidebarCollapsed.value
  }
  
  /**
   * 设置侧边栏状态
   * 
   * @param {boolean} collapsed - 是否折叠
   */
  const setSidebarCollapsed = (collapsed) => {
    sidebarCollapsed.value = collapsed
  }
  
  /**
   * 设置设备类型
   * 
   * @param {string} deviceType - 设备类型
   */
  const setDevice = (deviceType) => {
    device.value = deviceType
  }
  
  /**
   * 设置加载状态
   * 
   * @param {boolean} isLoading - 是否加载中
   */
  const setLoading = (isLoading) => {
    loading.value = isLoading
  }
  
  /**
   * 设置页面标题
   * 
   * @param {string} title - 页面标题
   */
  const setPageTitle = (title) => {
    pageTitle.value = title
  }
  
  /**
   * 初始化设备类型
   * 根据屏幕宽度判断设备类型
   */
  const initDevice = () => {
    const width = window.innerWidth
    if (width <= 768) {
      device.value = 'mobile'
      sidebarCollapsed.value = true
    } else {
      device.value = 'desktop'
      sidebarCollapsed.value = false
    }
  }
  
  // 返回store的状态和方法
  return {
    device,
    sidebarCollapsed,
    loading,
    pageTitle,
    isMobile,
    isDesktop,
    toggleSidebar,
    setSidebarCollapsed,
    setDevice,
    setLoading,
    setPageTitle,
    initDevice
  }
})