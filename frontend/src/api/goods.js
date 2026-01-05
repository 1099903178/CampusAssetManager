/**
 * CampusAssetManager/frontend/src/api/goods.js
 * 物品管理相关 API
 * 
 * 功能说明：
 * - 获取物品列表
 * - 创建物品
 * - 更新物品信息
 * - 删除物品
 * 
 * 作者：CampusAssetManager开发团队
 * 日期：2026-01-05
 */

import http from '@/utils/request'

/**
 * 获取物品列表（分页）
 * 
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码
 * @param {number} params.page_size - 每页数量
 * @param {number} params.category_id - 分类ID（可选）
 * @param {string} params.goods_name - 物品名称（可选，模糊搜索）
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
 * @param {number} data.category_id - 分类ID
 * @param {string} data.specification - 规格
 * @param {number} data.unit_price - 单价
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
 * 删除物品
 * 
 * @param {number} goodsId - 物品ID
 * @returns {Promise} 返回Promise对象
 */
export const deleteGoods = (goodsId) => {
  return http.delete(`/v1/goods/${goodsId}`)
}

/**
 * 获取物品分类列表
 * 
 * @returns {Promise} 返回Promise对象
 */
export const getGoodsCategories = () => {
  return http.get('/v1/goods/categories')
}

/**
 * 创建物品分类
 * 
 * @param {Object} data - 分类数据
 * @param {string} data.category_name - 分类名称
 * @param {string} data.description - 描述（可选）
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