/**
 * CampusAssetManager/frontend/src/utils/request.js
 * Axios 请求工具类
 * 
 * 功能说明：
 * - 创建 Axios 实例
 * - 配置请求拦截器（添加Token等）
 * - 配置响应拦截器（统一处理错误、响应数据格式化）
 * - 提供通用的请求方法
 * 
 * 作者：CampusAssetManager开发团队
 * 日期：2026-01-05
 */

import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/stores'

/**
 * API 基础配置
 */
const config = {
  // 优先使用本地存储的API地址，否则使用环境变量
  baseURL: localStorage.getItem('api_base_url') && localStorage.getItem('api_base_url').trim() !== ''
    ? localStorage.getItem('api_base_url')
    : import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json;charset=UTF-8'
  }
}

/**
 * 设置API基础URL
 * @param {string} url - API地址
 */
export function setApiBaseUrl(url) {
  config.baseURL = url
  localStorage.setItem('api_base_url', url)
  console.log('API地址已更新:', url)
}

/**
 * 创建 Axios 实例
 */
const service = axios.create(config)

/**
 * 请求拦截器
 * 在请求发送前进行统一处理
 */
service.interceptors.request.use(
  (config) => {
    /**
     * 从Pinia Store中获取Token
     */
    const userStore = useUserStore()
    
    /**
     * 如果存在Token，在请求头中添加 Authorization 字段
     * 格式：Bearer {token}
     */
    if (userStore.token) {
      config.headers.Authorization = `Bearer ${userStore.token}`
    }
    
    /**
      * 添加请求时间戳，防止浏览器缓存
      */
    if (config.method === 'get') {
      // 确保params存在且不为undefined，避免参数丢失
      if (!config.params) {
        config.params = {}
      }
      config.params._t = Date.now()
    }
    
    return config
  },
  (error) => {
    /**
     * 请求错误处理
     * 
     * @param {Object} error - 错误对象
     */
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

/**
 * 响应拦截器
 * 在接收到响应后进行统一处理
 */
service.interceptors.response.use(
  (response) => {
    /**
      * 如果是文件流响应（responseType === 'blob'），返回包含数据和响应头的对象
      * 用于文件下载场景，需要从响应头提取文件名
      */
    if (response.config.responseType === 'blob') {
      return {
        data: response.data,
        headers: response.headers
      }
    }
    
    /**
     * 从响应中提取数据
     * 后端返回格式：
     * {
     *   "code": 200,
     *   "message": "成功",
     *   "data": {}
     * }
     */
    const { code, message, data } = response.data
    
    /**
     * 请求成功（code: 200）
     * 直接返回数据
     */
    if (code === 200) {
      return data
    }
    
    /**
     * 业务错误（code != 200）
     * 显示错误提示
     */
    ElMessage.error(message || '请求失败')
    return Promise.reject(new Error(message || '请求失败'))
  },
  (error) => {
    /**
     * 响应错误处理
     * 
     * @param {Object} error - 错误对象
     */
    console.error('响应错误:', error)
    
    /**
     * 判断错误类型
     */
    if (error.response) {
      /**
       * 服务器返回了错误状态码
       */
      const { status, data } = error.response
      
      switch (status) {
        case 401:
          /**
           * 未授权（未登录或Token过期）
           * 清除用户信息并跳转到登录页
           */
          const userStore = useUserStore()
          userStore.logout()
          ElMessageBox.confirm(
            '登录状态已过期，请重新登录',
            '系统提示',
            {
              confirmButtonText: '重新登录',
              cancelButtonText: '取消',
              type: 'warning'
            }
          ).then(() => {
            window.location.href = '/login'
          })
          break
          
        case 403:
          /**
           * 禁止访问（权限不足）
           */
          ElMessage.error('权限不足，无法访问该资源')
          break
          
        case 404:
          /**
           * 资源不存在
           */
          ElMessage.error('请求的资源不存在')
          break
          
        case 500:
          /**
           * 服务器内部错误
           */
          ElMessage.error('服务器内部错误，请稍后重试')
          break
          
        default:
          /**
           * 其他错误
           */
          ElMessage.error(data?.message || `请求失败，状态码：${status}`)
      }
    } else if (error.request) {
      /**
       * 请求已发送但没有收到响应
       * 可能是网络问题
       */
      ElMessage.error('网络异常，请检查网络连接')
    } else {
      /**
       * 请求配置错误
       */
      ElMessage.error('请求配置错误')
    }
    
    return Promise.reject(error)
  }
)

/**
 * 导出请求方法
 */
export default service

/**
 * 导出快捷请求方法
 */
export const http = {
  /**
   * GET 请求
   *
   * @param {string} url - 请求地址
   * @param {Object} params - 请求参数
   * @param {Object} config - 请求配置
   * @returns {Promise} 返回Promise对象
   */
  get(url, params = {}, config = {}) {
    // 确保params是一个对象，避免undefined
    const requestParams = params || {}
    
    // 创建完整配置对象，确保params包含在config中
    const fullConfig = {
      ...config,
      params: requestParams
    }
    
    return service.get(url, fullConfig)
  },
  
  /**
   * POST 请求
   * 
   * @param {string} url - 请求地址
   * @param {Object} data - 请求数据
   * @param {Object} config - 请求配置
   * @returns {Promise} 返回Promise对象
   */
  post(url, data = {}, config = {}) {
    return service.post(url, data, config)
  },
  
  /**
   * PUT 请求
   * 
   * @param {string} url - 请求地址
   * @param {Object} data - 请求数据
   * @param {Object} config - 请求配置
   * @returns {Promise} 返回Promise对象
   */
  put(url, data = {}, config = {}) {
    return service.put(url, data, config)
  },
  
  /**
   * DELETE 请求
   * 
   * @param {string} url - 请求地址
   * @param {Object} params - 请求参数
   * @param {Object} config - 请求配置
   * @returns {Promise} 返回Promise对象
   */
  delete(url, params = {}, config = {}) {
    return service.delete(url, {
      params,
      ...config
    })
  },
  
  /**
   * 文件上传
   * 
   * @param {string} url - 请求地址
   * @param {FormData} formData - 文件数据
   * @param {Object} config - 请求配置
   * @returns {Promise} 返回Promise对象
   */
  upload(url, formData, config = {}) {
    return service.post(url, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      ...config
    })
  },
  
  /**
   * 文件下载
   * 
   * @param {string} url - 请求地址
   * @param {Object} params - 请求参数
   * @param {string} filename - 保存的文件名
   * @returns {Promise} 返回Promise对象
   */
  download(url, params = {}, filename = 'download') {
    return service.get(url, {
      params,
      responseType: 'blob'
    }).then((data) => {
      /**
       * 创建Blob对象
       */
      const blob = new Blob([data])
      
      /**
       * 创建下载链接
       */
      const link = document.createElement('a')
      link.href = window.URL.createObjectURL(blob)
      link.download = filename
      link.click()
      
      /**
       * 释放URL对象
       */
      window.URL.revokeObjectURL(link.href)
      
      return data
    })
  }
}