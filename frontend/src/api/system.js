/**
 * CampusAssetManager/frontend/src/api/system.js
 * 系统配置相关 API
 * 
 * 功能说明：
 * - 获取系统配置
 * - 更新系统配置
 * - 获取操作日志
 * 
 * 作者：CampusAssetManager开发团队
 * 日期：2026-01-05
 */

import http from '@/utils/request'

/**
 * 获取系统配置列表
 * 
 * @returns {Promise} 返回Promise对象
 */
export const getConfigs = () => {
  return http.get('/v1/system/configs')
}

/**
 * 更新系统配置
 * 
 * @param {Object} data - 配置数据
 * @returns {Promise} 返回Promise对象
 */
export const updateConfig = (data) => {
  return http.put('/v1/system/configs', data)
}

/**
 * 获取操作日志列表（分页）
 * 
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码
 * @param {number} params.page_size - 每页数量
 * @param {string} params.start_date - 开始日期（可选）
 * @param {string} params.end_date - 结束日期（可选）
 * @returns {Promise} 返回Promise对象
 */
export const getOperationLogs = (params) => {
  return http.get('/v1/system/logs', params)
}

/**
 * 导出操作日志
 * 
 * @param {Object} params - 查询参数
 * @returns {Promise} 返回Promise对象
 */
export const exportLogs = (params) => {
  return http.download('/v1/system/logs/export', params, 'operation_logs.xlsx')
}