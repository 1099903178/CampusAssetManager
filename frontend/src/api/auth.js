/**
 * CampusAssetManager/frontend/src/api/auth.js
 * 认证相关 API
 * 
 * 功能说明：
 * - 用户登录
 * - 用户登出
 * - 获取用户信息
 * 
 * 作者：CampusAssetManager开发团队
 * 日期：2026-01-05
 */

import http from '@/utils/request'

/**
 * 用户登录
 * 
 * @param {Object} data - 登录数据
 * @param {string} data.username - 用户名
 * @param {string} data.password - 密码
 * @returns {Promise} 返回Promise对象
 */
export const login = (data) => {
  return http.post('/v1/auth/login', data)
}

/**
 * 用户登出
 * 
 * @returns {Promise} 返回Promise对象
 */
export const logout = () => {
  return http.post('/v1/auth/logout')
}

/**
 * 获取当前用户信息
 * 
 * @returns {Promise} 返回Promise对象
 */
export const getUserInfo = () => {
  return http.get('/v1/auth/user-info')
}

/**
 * 修改密码
 * 
 * @param {Object} data - 密码数据
 * @param {string} data.old_password - 旧密码
 * @param {string} data.new_password - 新密码
 * @returns {Promise} 返回Promise对象
 */
export const changePassword = (data) => {
  return http.post('/v1/auth/change-password', data)
}