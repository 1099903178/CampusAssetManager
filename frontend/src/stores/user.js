/**
 * CampusAssetManager/frontend/src/stores/user.js
 * 用户状态管理 Store
 * 
 * 功能说明：
 * - 管理用户登录状态
 * - 存储用户信息
 * - 管理Token
 * - 提供用户相关的getter和action
 * 
 * 作者：CampusAssetManager开发团队
 * 日期：2026-01-05
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

/**
 * 用户状态管理Store
 */
export const useUserStore = defineStore('user', () => {
  // ========== 状态定义 ==========
  
  /**
   * 用户信息对象
   */
  const user = ref(null)
  
  /**
   * 访问令牌
   */
  const token = ref(localStorage.getItem('token') || '')
  
  // ========== 计算属性 ==========
  
  /**
   * 是否已登录
   */
  const isLoggedIn = computed(() => {
    return !!token.value
  })
  
  /**
   * 用户角色
   */
  const userRole = computed(() => {
    return user.value?.role || 'guest'
  })
  
  /**
   * 用户名
   */
  const username = computed(() => {
    return user.value?.username || ''
  })
  
  // ========== Actions ==========
  
  /**
   * 设置用户信息
   * 
   * @param {Object} userInfo - 用户信息对象
   * @param {string} userInfo.username - 用户名
   * @param {string} userInfo.role - 用户角色
   * @param {number} userInfo.user_id - 用户ID
   */
  const setUser = (userInfo) => {
    user.value = userInfo
  }
  
  /**
   * 设置Token
   * 
   * @param {string} tokenValue - 访问令牌
   */
  const setToken = (tokenValue) => {
    token.value = tokenValue
    localStorage.setItem('token', tokenValue)
  }
  
  /**
   * 清除用户信息和Token
   * 用于用户登出
   */
  const logout = async () => {
    try {
      // 调用后端logout API (如果需要)
      // await logout()
    } catch (error) {
      console.error('登出API调用失败:', error)
    } finally {
      // 无论API调用成功与否，都清除本地状态
      user.value = null
      token.value = ''
      localStorage.removeItem('token')
    }
  }
  
  /**
   * 检查用户权限
   * 
   * @param {string} requiredRole - 需要的角色
   * @returns {boolean} 是否有权限
   */
  const hasPermission = (requiredRole) => {
    const roleHierarchy = {
      'super_admin': 3,
      'admin': 2,
      'user': 1,
      'guest': 0
    }
    
    return roleHierarchy[userRole.value] >= roleHierarchy[requiredRole]
  }
  
  // 返回store的状态和方法
  return {
    user,
    token,
    isLoggedIn,
    userRole,
    username,
    setUser,
    setToken,
    logout,
    hasPermission
  }
})