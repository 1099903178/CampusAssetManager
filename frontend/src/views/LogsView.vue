/**
 * CampusAssetManager/frontend/src/views/LogsView.vue
 * 操作日志页面
 * 
 * 功能说明：
 * - 操作日志查询
 * - 按用户名、操作类型、模块、时间范围筛选
 * - 日志列表展示
 * 
 * 作者：CampusAssetManager开发团队
 * 日期：2026-01-13
 */

<template>
  <div class="page-container">
    <div class="glass-toolbar">
      <div class="toolbar-left">
        <h2 class="page-title">操作日志</h2>
      </div>
      
      <div class="toolbar-center">
        <el-input
          v-model="logSearchForm.username"
          placeholder="搜索操作人..."
          :prefix-icon="Search"
          clearable
          class="search-input-inline"
          @clear="handleSearch"
          @keyup.enter="handleSearch"
        />
        
        <el-select
          v-model="logSearchForm.operation"
          placeholder="操作类型"
          clearable
          class="filter-select-inline"
          @change="handleSearch"
        >
          <el-option label="登录" value="login" />
          <el-option label="创建" value="create" />
          <el-option label="更新" value="update" />
          <el-option label="删除" value="delete" />
          <el-option label="入库" value="stock_in" />
          <el-option label="出库" value="stock_out" />
          <el-option label="盘点" value="check" />
          <el-option label="查询" value="query" />
          <el-option label="修改配置" value="update_config" />
          <el-option label="系统重置" value="reset" />
        </el-select>
        
        <el-select
          v-model="logSearchForm.module"
          placeholder="模块"
          clearable
          class="filter-select-inline"
          @change="handleSearch"
        >
          <el-option label="认证" value="auth" />
          <el-option label="物品" value="goods" />
          <el-option label="库存" value="stock" />
          <el-option label="用户" value="user" />
          <el-option label="系统" value="system" />
        </el-select>
        
        <el-date-picker
          v-model="logSearchForm.dateRange"
          type="daterange"
          range-separator="-"
          start-placeholder="开始"
          end-placeholder="结束"
          value-format="YYYY-MM-DD"
          @change="handleSearch"
          class="date-picker-inline"
          size="default"
        />
      </div>
      
      <div class="toolbar-right">
        <el-button @click="handleResetLogs">重置</el-button>
        <el-button type="primary" @click="handleExportLogs">
          <el-icon><Download /></el-icon>
          导出日志
        </el-button>
      </div>
    </div>
    
    <div class="content-card">
      <el-table
        :data="logList"
        style="width: 100%"
        v-loading="loading"
      >
        <el-table-column prop="log_id" label="ID" width="80" align="center">
          <template #default="{ row }">
            <span class="num-font secondary-num">{{ row.log_id }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="username" label="操作人" width="120" />
        <el-table-column prop="operation" label="操作类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getOperationType(row.operation)">
              {{ getOperationText(row.operation) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="module" label="模块" width="100">
          <template #default="{ row }">
            {{ getModuleText(row.module) }}
          </template>
        </el-table-column>
        <el-table-column prop="url" label="请求URL" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">
            <span class="code-text">{{ row.url }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="result" label="结果" width="100" align="center">
          <template #default="{ row }">
            <div class="status-pill" :class="getResultClass(row.result)">
              <span class="dot"></span>
              <span>{{ getResultText(row.result) }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="ip_address" label="IP地址" width="140">
          <template #default="{ row }">
            <span class="code-text">{{ row.ip_address }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="create_time" label="操作时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.create_time) }}
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <el-pagination
        :current-page="logPagination.page"
        :page-size="logPagination.page_size"
        :page-sizes="[10, 20, 50, 100]"
        :total="logPagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleLogSizeChange"
        @current-change="handleLogPageChange"
        class="pagination-wrapper"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Download } from '@element-plus/icons-vue'
import { getOperationLogs } from '@/api'

/**
 * 日志搜索表单
 */
const logSearchForm = reactive({
  username: '',
  operation: '',
  module: '',
  dateRange: []
})

/**
 * 日志列表
 */
const logList = ref([])

/**
 * 日志分页数据
 */
const logPagination = reactive({
  page: 1,
  page_size: 20,
  total: 0
})

/**
 * 加载状态
 */
const loading = ref(false)

/**
 * 获取结果样式类名
 *
 * @param {string} result - 结果
 * @returns {string} 样式类名
 */
const getResultClass = (result) => {
  return result === 'success' ? 's-active' : 's-danger'
}

/**
 * 获取结果文本
 *
 * @param {string} result - 结果
 * @returns {string} 结果文本
 */
const getResultText = (result) => {
  return result === 'success' ? '成功' : '失败'
}

/**
 * 获取模块文本
 *
 * @param {string} module - 模块
 * @returns {string} 模块中文文本
 */
const getModuleText = (module) => {
  const moduleMap = {
    'auth': '认证',
    'goods': '物品',
    'stock': '库存',
    'user': '用户',
    'system': '系统'
  }
  return moduleMap[module] || module
}

/**
 * 获取操作类型标签样式
 *
 * @param {string} operation - 操作类型
 * @returns {string} 标签样式类型
 */
const getOperationType = (operation) => {
  const typeMap = {
    '登录': 'success',
    '创建': 'primary',
    '更新': 'warning',
    '删除': 'danger',
    '入库': 'success',
    '出库': 'warning',
    '盘点': 'info',
    '查询': 'info',
    '修改配置': 'warning',
    '查看配置': 'info',
    '系统重置': 'danger',
    'unknown': 'info',
    '未知模块': 'info',
    'login': 'success',
    'create': 'primary',
    'update': 'warning',
    'delete': 'danger',
    'stock_in': 'success',
    'stock_out': 'warning',
    'check': 'info',
    'query': 'info',
    'update_config': 'warning',
    'query_config': 'info'
  }
  return typeMap[operation] || 'info'
}

/**
 * 获取操作类型文本
 *
 * @param {string} operation - 操作类型
 * @returns {string} 操作类型文本
 */
const getOperationText = (operation) => {
  const textMap = {
    'login': '登录',
    'create': '创建',
    'update': '更新',
    'delete': '删除',
    'stock_in': '入库',
    'stock_out': '出库',
    'check': '盘点',
    'query': '查询',
    'update_config': '修改配置',
    'query_config': '查看配置',
    'query_check': '查询盘点',
    'reset': '系统重置',
    '系统重置': '系统重置',
    'unknown': '未知',
    '未知模块': '未知模块'
  }
  return textMap[operation] || operation
}

/**
 * 格式化日期时间（UTC+8时区）
 *
 * @param {string} datetime - 日期时间字符串（UTC）
 * @returns {string} 格式化后的日期时间（本地时间 UTC+8）
 */
const formatDateTime = (datetime) => {
  if (!datetime) return ''
  const date = new Date(datetime)
  
  // 转换为本地时间（UTC+8小时）
  const localTime = new Date(date.getTime() + 8 * 60 * 60 * 1000)
  
  // 手动拼接格式化字符串
  const year = localTime.getFullYear()
  const month = String(localTime.getMonth() + 1).padStart(2, '0')
  const day = String(localTime.getDate()).padStart(2, '0')
  const hours = String(localTime.getHours()).padStart(2, '0')
  const minutes = String(localTime.getMinutes()).padStart(2, '0')
  const seconds = String(localTime.getSeconds()).padStart(2, '0')
  
  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
}

/**
 * 加载操作日志
 * @param {number} overridePage - 可选：覆盖当前页码（用于处理响应式更新延迟）
 * @param {number} overridePageSize - 可选：覆盖每页大小（用于处理响应式更新延迟）
 */
const loadOperationLogs = async (overridePage = null, overridePageSize = null) => {
  try {
    loading.value = true
    
    // 构建查询参数（使用传入的覆盖值，或当前值）
    const params = {
      page: overridePage !== null ? overridePage : logPagination.page,
      page_size: overridePageSize !== null ? overridePageSize : logPagination.page_size
    }
    
    // 只有当值不为空时才添加参数
    if (logSearchForm.username) {
      params.username = logSearchForm.username
    }
    if (logSearchForm.operation) {
      params.operation = logSearchForm.operation
    }
    if (logSearchForm.module) {
      params.module = logSearchForm.module
    }
    
    // 处理时间范围
    if (logSearchForm.dateRange && logSearchForm.dateRange.length === 2) {
      params.start_date = formatDateToString(logSearchForm.dateRange[0])
      params.end_date = formatDateToString(logSearchForm.dateRange[1])
    }
    
    const response = await getOperationLogs(params)
    logList.value = response.items
    logPagination.total = response.total
    logPagination.page = response.page
    logPagination.page_size = response.page_size
  } catch (error) {
    console.error('加载操作日志失败:', error)
    ElMessage.error('加载操作日志失败')
  } finally {
    loading.value = false
  }
}

/**
 * 格式化日期为字符串
 *
 * @param {Date} date - 日期对象
 * @returns {string} 日期字符串
 */
const formatDateToString = (date) => {
  if (!date) return ''
  const d = new Date(date)
  return d.toISOString().split('T')[0]
}

/**
 * 处理日志页码变化
 *
 * @param {number} page - 页码
 */
const handleLogPageChange = (page) => {
  logPagination.page = page
  // 使用 nextTick 确保状态更新完成后再发送请求
  nextTick(() => {
    loadOperationLogs(page, logPagination.page_size)
  })
}

/**
 * 处理日志每页数量变化
 *
 * @param {number} size - 每页数量
 */
const handleLogSizeChange = (size) => {
  logPagination.page_size = size
  // 直接传递每页大小和当前页码，避免响应式更新延迟
  loadOperationLogs(logPagination.page, size)
}

/**
 * 处理搜索按钮点击
 */
const handleSearch = () => {
  logPagination.page = 1
  loadOperationLogs()
}

/**
 * 处理导出日志
 */
const handleExportLogs = () => {
  ElMessage.info('导出日志功能待实现')
}

/**
 * 处理重置日志搜索
 */
const handleResetLogs = () => {
  logSearchForm.username = ''
  logSearchForm.operation = ''
  logSearchForm.module = ''
  logSearchForm.dateRange = []
  logPagination.page = 1
  loadOperationLogs()
}

/**
 * 组件挂载时加载数据
 */
onMounted(() => {
  loadOperationLogs()
})
</script>

<style scoped>
.page-container {
  padding: 20px;
  animation: fadeIn 0.4s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* 悬浮工具栏 */
.glass-toolbar {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(241, 245, 249, 0.8);
  padding: 12px 20px;
  border-radius: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  box-shadow: 0 4px 20px -5px rgba(0, 0, 0, 0.05);
  position: sticky;
  top: 20px;
  z-index: 10;
  flex-wrap: wrap;
  gap: 12px;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.toolbar-center {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.toolbar-right {
  display: flex;
  gap: 8px;
  align-items: center;
}

.page-title {
  font-size: 20px;
  font-weight: 700;
  color: #1e293b;
  margin: 0;
  letter-spacing: -0.3px;
  white-space: nowrap;
}

.search-input-inline {
  width: 180px;
}

.filter-select-inline {
  width: 130px;
}

.date-picker-inline {
  width: 300px;
}

/* 内容卡片 */
.content-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(241, 245, 249, 0.8);
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 4px 20px -5px rgba(0, 0, 0, 0.05);
}

/* 表格样式 */
.content-card :deep(.el-table) {
  border-radius: 12px;
  overflow: hidden;
}

.content-card :deep(.el-table th) {
  background-color: #f8fafc;
  color: #475569;
  font-weight: 600;
  padding: 14px 0;
}

.content-card :deep(.el-table td) {
  padding: 14px 0;
  border-top: 1px solid #f1f5f9;
}

.content-card :deep(.el-table__body tr:hover > td) {
  background-color: #f8fafc;
}

/* 分页样式 */
.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.pagination-wrapper :deep(.el-pagination) {
  color: #64748b;
}

.pagination-wrapper :deep(.el-pagination.is-background .el-pager li:not(.disabled).active) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

/* 字体样式 */
.num-font {
  font-family: 'Oswald', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  letter-spacing: -0.2px;
}

.secondary-num {
  color: #94a3b8;
  font-size: 13px;
}

.code-text {
  font-family: 'Courier New', Consolas, monospace;
  font-size: 12px;
  color: #64748b;
  background: #f1f5f9;
  padding: 2px 8px;
  border-radius: 6px;
}

/* 状态标签设计 */
.status-pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
}

.dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.s-active {
  background: #f0fdf4;
  color: #16a34a;
}

.s-active .dot {
  background: #10b981;
  box-shadow: 0 0 6px #10b981;
}

.s-danger {
  background: #fef2f2;
  color: #dc2626;
}

.s-danger .dot {
  background: #ef4444;
}

/* 响应式适配 */
@media (max-width: 1200px) {
  .glass-toolbar {
    flex-direction: column;
    align-items: stretch;
    position: static;
  }
  
  .toolbar-left {
    width: 100%;
  }
  
  .toolbar-center {
    width: 100%;
    flex-wrap: wrap;
  }
  
  .toolbar-right {
    width: 100%;
    justify-content: flex-start;
  }
  
  .search-input-inline,
  .filter-select-inline,
  .date-picker-inline {
    width: 100% !important;
  }
}
</style>