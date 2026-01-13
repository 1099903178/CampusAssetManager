/**
 * CampusAssetManager/frontend/src/api/stock.js
 * 库存管理相关 API
 * 
 * 功能说明：
 * - 入库操作
 * - 出库操作
 * - 获取入库记录列表
 * - 获取出库记录列表
 * - 获取入库详情
 * - 获取出库详情
 * 
 * 作者：CampusAssetManager开发团队
 * 日期：2026-01-07
 */

import http from '@/utils/request'

/**
 * 创建入库记录
 * 
 * @param {Object} data - 入库数据
 * @param {number} data.goods_id - 物品ID
 * @param {number} data.in_quantity - 入库数量
 * @param {number} data.unit_price - 入库单价
 * @param {number} data.total_amount - 入库总金额
 * @param {string} data.batch_no - 批次号（可选）
 * @param {string} data.supplier - 供应商（可选）
 * @param {string} data.remark - 备注（可选）
 * @returns {Promise} 返回Promise对象
 */
export const createStockIn = (data) => {
  return http.post('/v1/stock/in', data)
}

/**
 * 获取入库记录列表（分页）
 * 
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码
 * @param {number} params.page_size - 每页数量
 * @param {string} params.search - 搜索关键词（入库单号、物品名称，可选）
 * @param {number} params.goods_id - 按物品ID筛选（可选）
 * @param {string} params.start_date - 开始日期（YYYY-MM-DD，可选）
 * @param {string} params.end_date - 结束日期（YYYY-MM-DD，可选）
 * @returns {Promise} 返回Promise对象
 */
export const getStockInList = (params) => {
  return http.get('/v1/stock/in', { params })
}

/**
 * 获取入库详情
 * 
 * @param {number} inId - 入库记录ID
 * @returns {Promise} 返回Promise对象
 */
export const getStockInDetail = (inId) => {
  return http.get(`/v1/stock/in/${inId}`)
}

/**
 * 创建出库记录
 * 
 * @param {Object} data - 出库数据
 * @param {number} data.goods_id - 物品ID
 * @param {number} data.out_quantity - 出库数量
 * @param {number} data.unit_price - 出库单价
 * @param {number} data.total_amount - 出库总金额
 * @param {string} data.receiver - 接收人（可选）
 * @param {string} data.department - 接收部门（可选）
 * @param {string} data.purpose - 用途说明（可选）
 * @param {string} data.remark - 备注（可选）
 * @returns {Promise} 返回Promise对象
 */
export const createStockOut = (data) => {
  return http.post('/v1/stock/out', data)
}

/**
 * 获取出库记录列表（分页）
 * 
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码
 * @param {number} params.page_size - 每页数量
 * @param {string} params.search - 搜索关键词（出库单号、物品名称，可选）
 * @param {number} params.goods_id - 按物品ID筛选（可选）
 * @param {string} params.start_date - 开始日期（YYYY-MM-DD，可选）
 * @param {string} params.end_date - 结束日期（YYYY-MM-DD，可选）
 * @returns {Promise} 返回Promise对象
 */
export const getStockOutList = (params) => {
  return http.get('/v1/stock/out', { params })
}

/**
 * 获取出库详情
 * 
 * @param {number} outId - 出库记录ID
 * @returns {Promise} 返回Promise对象
 */
export const getStockOutDetail = (outId) => {
  return http.get(`/v1/stock/out/${outId}`)
}

/**
 * 创建盘点记录
 *
 * @param {Object} data - 盘点数据
 * @param {number} data.goods_id - 物品ID
 * @param {number} data.actual_stock - 实际库存数量
 * @param {string} data.remark - 备注说明（可选）
 * @returns {Promise} 返回Promise对象
 */
export const createStockCheck = (data) => {
  return http.post('/v1/stock/check', data)
}

/**
 * 获取盘点记录列表（分页）
 *
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码
 * @param {number} params.page_size - 每页数量
 * @param {string} params.search - 搜索关键词（盘点单号、物品名称，可选）
 * @param {number} params.goods_id - 按物品ID筛选（可选）
 * @param {string} params.check_result - 按盘点结果筛选（normal/over/short，可选）
 * @param {string} params.start_date - 开始日期（YYYY-MM-DD，可选）
 * @param {string} params.end_date - 结束日期（YYYY-MM-DD，可选）
 * @returns {Promise} 返回Promise对象
 */
export const getStockCheckList = (params) => {
  return http.get('/v1/stock/check', { params })
}

/**
 * 获取盘点详情
 *
 * @param {number} checkId - 盘点记录ID
 * @returns {Promise} 返回Promise对象
 */
export const getStockCheckDetail = (checkId) => {
  return http.get(`/v1/stock/check/${checkId}`)
}

/**
 * 手动调整库存
 *
 * @param {Object} data - 调整数据
 * @param {number} data.goods_id - 物品ID
 * @param {number} data.adjust_quantity - 调整数量（正数为增加，负数为减少）
 * @param {string} data.adjust_reason - 调整原因
 * @returns {Promise} 返回Promise对象
 */
export const adjustStock = (data) => {
  return http.put('/v1/stock/adjust', data)
}

/**
 * 查询库存台账
 *
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码
 * @param {number} params.page_size - 每页数量
 * @param {string} params.search - 搜索关键词（操作单号、物品名称，可选）
 * @param {number} params.goods_id - 按物品ID筛选（可选）
 * @param {string} params.operation_type - 按操作类型筛选（in/out/check，可选）
 * @param {string} params.start_date - 开始日期（YYYY-MM-DD，可选）
 * @param {string} params.end_date - 结束日期（YYYY-MM-DD，可选）
 * @returns {Promise} 返回Promise对象
 */
export const getStockLedger = (params) => {
  return http.get('/v1/stock/ledger', { params })
}

/**
 * 增强库存查询
 *
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码
 * @param {number} params.page_size - 每页数量
 * @param {string} params.search - 搜索关键词（物品名称、编码，可选）
 * @param {number} params.category_id - 按分类ID筛选（可选）
 * @param {string} params.stock_status - 按库存状态筛选（normal/low/over，可选）
 * @param {boolean} params.min_stock_only - 只显示低于最小库存的物品
 * @returns {Promise} 返回Promise对象
 */
export const getStockListEnhanced = (params) => {
  return http.get('/v1/stock/list/enhanced', { params })
}

/**
 * 获取库存列表（兼容旧接口）
 *
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码
 * @param {number} params.page_size - 每页数量
 * @returns {Promise} 返回Promise对象
 */
export const getStockList = (params) => {
  return http.get('/v1/stock/list', { params })
}

/**
 * 同步库存阈值
 *
 * @param {Object} params - 同步参数
 * @param {number} params.min_stock - 最小库存阈值
 * @param {number} params.max_stock - 最大库存阈值
 * @returns {Promise} 返回Promise对象
 */
export const syncStockThresholds = (params) => {
  return http.put('/v1/stock/thresholds/sync', null, { params })
}

/**
 * 更新物品库存阈值
 *
 * @param {Object} data - 库存阈值数据
 * @param {number} data.goods_id - 物品ID
 * @param {number} data.min_stock - 最小库存阈值
 * @param {number} data.max_stock - 最大库存阈值（可选）
 * @returns {Promise} 返回Promise对象
 */
export const updateStockThreshold = (data) => {
  return http.put('/v1/stock/thresholds', data)
}

/**
 * 批量更新库存阈值
 *
 * @param {Object} data - 批量更新数据
 * @param {number} data.min_stock - 最小库存阈值
 * @param {number} data.max_stock - 最大库存阈值（可选）
 * @returns {Promise} 返回Promise对象
 */
export const batchUpdateStockThresholds = (data) => {
  return http.put('/v1/stock/thresholds/batch', data)
}