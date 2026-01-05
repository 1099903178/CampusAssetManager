/**
 * CampusAssetManager/frontend/src/api/statistics.js
 * 统计报表相关 API
 * 
 * 功能说明：
 * - 获取库存统计
 * - 获取出入库统计
 * - 获取物品分类统计
 * - 导出报表
 * 
 * 作者：CampusAssetManager开发团队
 * 日期：2026-01-05
 */

import http from '@/utils/request'

/**
 * 获取库存统计概览
 * 
 * @returns {Promise} 返回Promise对象
 */
export const getStockOverview = () => {
  return http.get('/v1/statistics/stock-overview')
}

/**
 * 获取物品分类统计
 * 
 * @returns {Promise} 返回Promise对象
 */
export const getCategoryStatistics = () => {
  return http.get('/v1/statistics/category')
}

/**
 * 获取出入库趋势统计
 * 
 * @param {Object} params - 查询参数
 * @param {string} params.start_date - 开始日期
 * @param {string} params.end_date - 结束日期
 * @param {string} params.type - 类型（in/out）
 * @returns {Promise} 返回Promise对象
 */
export const getTrendStatistics = (params) => {
  return http.get('/v1/statistics/trend', params)
}

/**
 * 获取库存预警列表
 * 
 * @returns {Promise} 返回Promise对象
 */
export const getStockAlert = () => {
  return http.get('/v1/statistics/stock-alert')
}

/**
 * 导出入库报表
 * 
 * @param {Object} params - 查询参数
 * @param {string} params.start_date - 开始日期
 * @param {string} params.end_date - 结束日期
 * @param {string} params.type - 类型（in/out）
 * @returns {Promise} 返回Promise对象
 */
export const exportStockReport = (params) => {
  return http.download('/v1/statistics/export', params, 'stock_report.xlsx')
}

/**
 * 导出盘点报告
 * 
 * @param {number} checkId - 盘点单ID
 * @returns {Promise} 返回Promise对象
 */
export const exportCheckReport = (checkId) => {
  return http.download(`/v1/statistics/check/${checkId}`, {}, 'check_report.xlsx')
}