/**
 * CampusAssetManager/frontend/src/api/stock.js
 * 库存管理相关 API
 * 
 * 功能说明：
 * - 入库操作
 * - 出库操作
 * - 获取库存列表
 * - 库存盘点
 * 
 * 作者：CampusAssetManager开发团队
 * 日期：2026-01-05
 */

import http from '@/utils/request'

/**
 * 获取库存列表（分页）
 * 
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码
 * @param {number} params.page_size - 每页数量
 * @param {number} params.goods_id - 物品ID（可选）
 * @param {string} params.goods_name - 物品名称（可选，模糊搜索）
 * @returns {Promise} 返回Promise对象
 */
export const getStockList = (params) => {
  return http.get('/v1/stock/', params)
}

/**
 * 获取物品库存详情
 * 
 * @param {number} stockId - 库存ID
 * @returns {Promise} 返回Promise对象
 */
export const getStockDetail = (stockId) => {
  return http.get(`/v1/stock/${stockId}`)
}

/**
 * 入库操作
 * 
 * @param {Object} data - 入库数据
 * @param {number} data.goods_id - 物品ID
 * @param {number} data.quantity - 入库数量
 * @param {string} data.batch_no - 批次号
 * @param {string} data.remark - 备注（可选）
 * @returns {Promise} 返回Promise对象
 */
export const stockIn = (data) => {
  return http.post('/v1/stock/in', data)
}

/**
 * 出库操作
 * 
 * @param {Object} data - 出库数据
 * @param {number} data.goods_id - 物品ID
 * @param {number} data.quantity - 出库数量
 * @param {string} data.target - 出库目标
 * @param {string} data.remark - 备注（可选）
 * @returns {Promise} 返回Promise对象
 */
export const stockOut = (data) => {
  return http.post('/v1/stock/out', data)
}

/**
 * 获取入库记录列表（分页）
 * 
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码
 * @param {number} params.page_size - 每页数量
 * @param {Date} params.start_date - 开始日期（可选）
 * @param {Date} params.end_date - 结束日期（可选）
 * @returns {Promise} 返回Promise对象
 */
export const getStockInList = (params) => {
  return http.get('/v1/stock/in/records', params)
}

/**
 * 获取出库记录列表（分页）
 * 
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码
 * @param {number} params.page_size - 每页数量
 * @param {Date} params.start_date - 开始日期（可选）
 * @param {Date} params.end_date - 结束日期（可选）
 * @returns {Promise} 返回Promise对象
 */
export const getStockOutList = (params) => {
  return http.get('/v1/stock/out/records', params)
}

/**
 * 创建盘点单
 * 
 * @param {Object} data - 盘点数据
 * @param {string} data.check_name - 盘点单名称
 * @param {string} data.check_date - 盘点日期
 * @param {string} data.remark - 备注（可选）
 * @returns {Promise} 返回Promise对象
 */
export const createCheck = (data) => {
  return http.post('/v1/stock/check', data)
}

/**
 * 获取盘点列表（分页）
 * 
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码
 * @param {number} params.page_size - 每页数量
 * @returns {Promise} 返回Promise对象
 */
export const getCheckList = (params) => {
  return http.get('/v1/stock/check', params)
}

/**
 * 获取盘点详情
 * 
 * @param {number} checkId - 盘点单ID
 * @returns {Promise} 返回Promise对象
 */
export const getCheckDetail = (checkId) => {
  return http.get(`/v1/stock/check/${checkId}`)
}

/**
 * 提交盘点结果
 * 
 * @param {number} checkId - 盘点单ID
 * @param {Array} data - 盘点明细
 * @returns {Promise} 返回Promise对象
 */
export const submitCheck = (checkId, data) => {
  return http.post(`/v1/stock/check/${checkId}/submit`, data)
}