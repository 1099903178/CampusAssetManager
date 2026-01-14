/**
 * CampusAssetManager/frontend/src/api/statistics.js
 * 统计报表相关 API
 *
 * 功能说明：
 * - 获取数据概览统计
 * - 获取库存趋势统计
 * - 获取物品排行榜统计
 * - 获取分类统计
 * - 导出报表
 *
 * 作者：CampusAssetManager开发团队
 * 日期：2026-01-05
 */

import http from '@/utils/request'

/**
 * 获取数据概览
 *
 * @returns {Promise} 返回Promise对象，包含物品总数、库存总数、今日入库、今日出库、预警数量等
 */
export const getDataOverview = () => {
  return http.get('/v1/statistics/overview')
}

/**
 * 获取库存趋势统计
 *
 * @param {Object} params - 查询参数
 * @param {string} params.start_date - 开始日期（YYYY-MM-DD格式，可选）
 * @param {string} params.end_date - 结束日期（YYYY-MM-DD格式，可选）
 * @param {number} params.goods_id - 物品ID（可选）
 * @returns {Promise} 返回Promise对象，包含库存趋势数据
 */
export const getStockTrend = (params = {}) => {
  // 直接构建查询参数
  const queryParams = new URLSearchParams()
  if (params.start_date) {
    queryParams.append('start_date', params.start_date)
  }
  if (params.end_date) {
    queryParams.append('end_date', params.end_date)
  }
  if (params.goods_id) {
    queryParams.append('goods_id', params.goods_id)
  }
  
  const queryString = queryParams.toString()
  const url = `/v1/statistics/stock-trend${queryString ? '?' + queryString : ''}`
  
  return http.get(url)
}

/**
 * 获取物品排行榜统计
 *
 * @param {Object} params - 查询参数
 * @param {string} params.ranking_type - 排行榜类型（in/入库，out/出库）
 * @param {number} params.top_n - Top N数量（1-100）
 * @returns {Promise} 返回Promise对象，包含物品排行榜数据
 */
export const getGoodsRanking = (params = { ranking_type: 'in', top_n: 10 }) => {
  const queryParams = new URLSearchParams()
  if (params.ranking_type) {
    queryParams.append('ranking_type', params.ranking_type)
  }
  if (params.top_n) {
    queryParams.append('top_n', params.top_n)
  }
  
  const queryString = queryParams.toString()
  const url = `/v1/statistics/goods-ranking${queryString ? '?' + queryString : ''}`
  
  return http.get(url)
}

/**
 * 获取分类统计
 *
 * @param {Object} params - 查询参数
 * @param {string} params.stats_type - 统计类型（stock/库存，in/入库）
 * @returns {Promise} 返回Promise对象，包含分类统计数据
 */
export const getCategoryStats = (params = { stats_type: 'stock' }) => {
  // 使用URLSearchParams构建查询参数
  const queryParams = new URLSearchParams()
  if (params.stats_type) {
    queryParams.append('stats_type', params.stats_type)
  }
  
  const queryString = queryParams.toString()
  const url = `/v1/statistics/category-stats${queryString ? '?' + queryString : ''}`
  
  return http.get(url)
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