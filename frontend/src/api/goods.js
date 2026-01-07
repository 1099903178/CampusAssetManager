/**
 * CampusAssetManager/frontend/src/api/goods.js
 * 物品管理相关 API
 *
 * 功能说明：
 * - 物品分类管理：查询、创建、更新、删除
 * - 物品信息管理：查询、创建、更新、删除
 * - 物品导入导出：批量导入、导出、下载模板
 *
 * 作者：CampusAssetManager开发团队
 * 日期：2026-01-06
 */

import http from '@/utils/request'

// ==================== 物品分类管理 ====================

/**
 * 获取物品分类列表
 *
 * @returns {Promise} 返回Promise对象
 */
export const getGoodsCategories = () => {
  return http.get('/v1/goods/categories')
}

/**
 * 获取分类详情
 *
 * @param {number} categoryId - 分类ID
 * @returns {Promise} 返回Promise对象
 */
export const getCategoryDetail = (categoryId) => {
  return http.get(`/v1/goods/categories/${categoryId}`)
}

/**
 * 创建物品分类
 *
 * @param {Object} data - 分类数据
 * @param {string} data.category_name - 分类名称
 * @param {string} data.category_code - 分类编码
 * @param {number} data.parent_id - 父分类ID（可选）
 * @param {string} data.description - 描述（可选）
 * @param {number} data.sort_order - 排序号（可选）
 * @param {number} data.is_active - 是否启用（1启用/0禁用）
 * @returns {Promise} 返回Promise对象
 */
export const createCategory = (data) => {
  return http.post('/v1/goods/categories', data)
}

/**
 * 更新物品分类
 *
 * @param {number} categoryId - 分类ID
 * @param {Object} data - 更新数据
 * @param {string} data.category_name - 分类名称
 * @param {string} data.description - 描述（可选）
 * @param {number} data.sort_order - 排序号（可选）
 * @param {number} data.is_active - 是否启用（1启用/0禁用）
 * @returns {Promise} 返回Promise对象
 */
export const updateCategory = (categoryId, data) => {
  return http.put(`/v1/goods/categories/${categoryId}`, data)
}

/**
 * 删除物品分类
 *
 * @param {number} categoryId - 分类ID
 * @returns {Promise} 返回Promise对象
 */
export const deleteCategory = (categoryId) => {
  return http.delete(`/v1/goods/categories/${categoryId}`)
}

// ==================== 物品信息管理 ====================

/**
 * 获取物品列表（分页）
 *
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码
 * @param {number} params.page_size - 每页数量
 * @param {string} params.search - 搜索关键词（物品名称、编码）
 * @param {number} params.category_id - 分类ID（可选）
 * @param {number} params.status - 状态筛选（1正常/2报废/3维修中）
 * @returns {Promise} 返回Promise对象
 */
export const getGoodsList = (params) => {
  return http.get('/v1/goods/', params)
}

/**
 * 获取物品详情
 *
 * @param {number} goodsId - 物品ID
 * @returns {Promise} 返回Promise对象
 */
export const getGoodsDetail = (goodsId) => {
  return http.get(`/v1/goods/${goodsId}`)
}

/**
 * 创建物品
 *
 * @param {Object} data - 物品数据
 * @param {string} data.goods_name - 物品名称
 * @param {string} data.goods_code - 物品编码
 * @param {number} data.category_id - 分类ID
 * @param {string} data.specification - 规格（可选）
 * @param {string} data.unit - 计量单位
 * @param {number} data.purchase_price - 采购单价
 * @param {number} data.retail_price - 零售单价（可选）
 * @param {string} data.description - 描述（可选）
 * @param {number} data.status - 状态（1正常/2报废/3维修中）
 * @returns {Promise} 返回Promise对象
 */
export const createGoods = (data) => {
  return http.post('/v1/goods/', data)
}

/**
 * 更新物品信息
 *
 * @param {number} goodsId - 物品ID
 * @param {Object} data - 更新数据
 * @returns {Promise} 返回Promise对象
 */
export const updateGoods = (goodsId, data) => {
  return http.put(`/v1/goods/${goodsId}`, data)
}

/**
 * 删除物品（软删除）
 *
 * @param {number} goodsId - 物品ID
 * @returns {Promise} 返回Promise对象
 */
export const deleteGoods = (goodsId) => {
  return http.delete(`/v1/goods/${goodsId}`)
}

// ==================== 物品导入导出管理 ====================

/**
 * 下载物品导入模板
 *
 * @returns {Promise} 返回Promise对象，响应为Blob类型
 */
export const downloadImportTemplate = () => {
  return http.get('/v1/goods/import-template', {
    responseType: 'blob'
  })
}

/**
 * 批量导入物品
 *
 * @param {File} file - Excel文件（.xlsx或.xls格式）
 * @returns {Promise} 返回Promise对象
 */
export const importGoods = (file) => {
  const formData = new FormData()
  formData.append('file', file)
  return http.post('/v1/goods/import', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 导出物品列表
 *
 * @param {Object} params - 查询参数
 * @param {string} params.search - 搜索关键词（物品名称、编码）
 * @param {number} params.category_id - 分类ID（可选）
 * @param {number} params.status - 状态筛选（1正常/2报废/3维修中）
 * @returns {Promise} 返回Promise对象，响应为Blob类型
 */
export const exportGoods = (params = {}) => {
  return http.get('/v1/goods/export', {
    params: params,
    responseType: 'blob'
  })
}