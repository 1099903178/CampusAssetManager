/**
 * CampusAssetManager/frontend/src/api/users.js
 * 用户管理相关 API
 * 
 * 功能说明：
 * - 查询用户列表（支持分页、搜索）
 * - 创建新用户
 * - 获取用户详情
 * - 更新用户信息
 * - 删除用户（软删除）
 * - 修改用户密码
 * 
 * 作者：CampusAssetManager开发团队
 * 日期：2026-01-06
 */

import http from '@/utils/request'

/**
 * 查询用户列表
 * 
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码
 * @param {number} params.page_size - 每页数量
 * @param {string} params.search - 搜索关键词
 * @param {string} params.role - 角色筛选
 * @param {boolean} params.is_active - 激活状态筛选
 * @returns {Promise} 返回Promise对象
 */
export const getUserList = (params) => {
  return http.get('/v1/users/', params)
}

/**
 * 创建新用户
 * 
 * @param {Object} data - 用户数据
 * @param {string} data.username - 用户名
 * @param {string} data.password - 密码
 * @param {string} data.real_name - 真实姓名
 * @param {string} data.phone - 联系电话
 * @param {string} data.email - 电子邮箱
 * @param {string} data.role - 角色
 * @returns {Promise} 返回Promise对象
 */
export const createUser = (data) => {
  return http.post('/v1/users/', data)
}

/**
 * 获取用户详情
 * 
 * @param {number} user_id - 用户ID
 * @returns {Promise} 返回Promise对象
 */
export const getUserById = (user_id) => {
  return http.get(`/v1/users/${user_id}`)
}

/**
 * 更新用户信息
 * 
 * @param {number} user_id - 用户ID
 * @param {Object} data - 更新数据
 * @param {string} data.real_name - 真实姓名
 * @param {string} data.phone - 联系电话
 * @param {string} data.email - 电子邮箱
 * @param {string} data.role - 角色
 * @param {boolean} data.is_active - 是否激活
 * @returns {Promise} 返回Promise对象
 */
export const updateUser = (user_id, data) => {
  return http.put(`/v1/users/${user_id}`, data)
}

/**
 * 删除用户（软删除）
 * 
 * @param {number} user_id - 用户ID
 * @returns {Promise} 返回Promise对象
 */
export const deleteUser = (user_id) => {
  return http.delete(`/v1/users/${user_id}`)
}

/**
 * 修改用户密码
 * 
 * @param {number} user_id - 用户ID
 * @param {Object} data - 密码数据
 * @param {string} data.old_password - 旧密码
 * @param {string} data.new_password - 新密码
 * @returns {Promise} 返回Promise对象
 */
export const updateUserPassword = (user_id, data) => {
  return http.put(`/v1/users/${user_id}/password`, data)
}