/**
 * CampusAssetManager/frontend/src/views/SettingsView.vue
 * 系统设置页面
 * 
 * 功能说明：
 * - 系统配置管理
 * - 操作日志查询
 *
 * 作者：CampusAssetManager开发团队
 * 日期：2026-01-10
 */

<template>
    <div class="settings-container">
      <el-tabs v-model="activeTab" type="border-card">
        <!-- 系统配置 -->
        <el-tab-pane label="系统配置" name="config">
          <el-card v-for="group in configGroups" :key="group.category" style="margin-bottom: 20px;">
            <template #header>
              <div class="card-header">
                <span>{{ group.category_name }}</span>
              </div>
            </template>
            
            <el-form :model="configForm" label-width="150px">
              <el-form-item
                v-for="config in group.configs"
                :key="config.config_id"
                :label="config.config_name"
              >
                <!-- 字符串类型 -->
                <el-input
                  v-if="config.config_type === 'string'"
                  v-model="configForm[config.config_key]"
                  :placeholder="'请输入' + config.config_name"
                />
                
                <!-- 数字类型 -->
                <el-input-number
                  v-else-if="config.config_type === 'number'"
                  v-model="configForm[config.config_key]"
                  :min="0"
                />
                
                <!-- 布尔类型 -->
                <el-switch
                  v-else-if="config.config_type === 'boolean'"
                  v-model="configForm[config.config_key]"
                />
                
                <!-- JSON类型 -->
                <el-input
                  v-else-if="config.config_type === 'json'"
                  v-model="configForm[config.config_key]"
                  type="textarea"
                  :placeholder="'请输入' + config.config_name + '（JSON格式）'"
                />
              </el-form-item>
            </el-form>
          </el-card>
          
          <div style="text-align: right; margin-top: 20px;">
            <el-button type="primary" @click="handleSaveConfig" :loading="loading">保存配置</el-button>
          </div>
        </el-tab-pane>
        
        <!-- 操作日志 -->
        <el-tab-pane label="操作日志" name="logs">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>操作日志</span>
                <el-button type="primary" size="small" @click="handleExportLogs">导出日志</el-button>
              </div>
            </template>
            
            <div class="filter-form">
              <div class="filter-item">
                <label>
                  <span class="label-text">操作人：</span>
                </label>
                <el-input v-model="logSearchForm.username" placeholder="请输入操作人" clearable style="width: 150px;" />
              </div>
              
              <div class="filter-item">
                <label>
                  <span class="label-text">操作类型：</span>
                </label>
                <el-select v-model="logSearchForm.operation" placeholder="请选择操作类型" clearable style="width: 150px;">
                  <el-option label="登录" value="login" />
                  <el-option label="创建" value="create" />
                  <el-option label="更新" value="update" />
                  <el-option label="删除" value="delete" />
                  <el-option label="入库" value="stock_in" />
                  <el-option label="出库" value="stock_out" />
                  <el-option label="盘点" value="check" />
                </el-select>
              </div>
              
              <div class="filter-item">
                <label>
                  <span class="label-text">模块：</span>
                </label>
                <el-select v-model="logSearchForm.module" placeholder="请选择模块" clearable style="width: 150px;">
                  <el-option label="认证" value="auth" />
                  <el-option label="物品" value="goods" />
                  <el-option label="库存" value="stock" />
                  <el-option label="用户" value="user" />
                  <el-option label="系统" value="system" />
                </el-select>
              </div>
              
              <div class="filter-item">
                <label>
                  <span class="label-text">时间范围：</span>
                </label>
                <el-date-picker
                  v-model="logSearchForm.dateRange"
                  type="daterange"
                  range-separator="至"
                  start-placeholder="开始日期"
                  end-placeholder="结束日期"
                  size="default"
                />
              </div>
              
              <div class="filter-item">
                <el-button type="primary" @click="handleSearch">搜索</el-button>
                <el-button @click="handleResetLogs">重置</el-button>
              </div>
            </div>
            
            <el-table
              :data="logList"
              style="width: 100%"
              v-loading="loading"
            >
              <el-table-column prop="log_id" label="ID" width="80" align="center" />
              <el-table-column prop="username" label="操作人" width="120" />
              <el-table-column prop="operation" label="操作类型" width="120">
                <template #default="{ row }">
                  <el-tag :type="getOperationType(row.operation)">
                    {{ getOperationText(row.operation) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="module" label="模块" width="100" />
              <el-table-column prop="url" label="请求URL" min-width="200" show-overflow-tooltip />
              <el-table-column prop="result" label="结果" width="100">
                <template #default="{ row }">
                  <el-tag :type="row.result === 'success' ? 'success' : 'danger'">
                    {{ row.result === 'success' ? '成功' : '失败' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="ip_address" label="IP地址" width="140" />
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
              style="margin-top: 20px; justify-content: flex-end;"
            />
          </el-card>
        </el-tab-pane>
      </el-tabs>
    </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { getConfigs, updateConfig, getOperationLogs } from '@/api'

/**
 * 当前激活的Tab
 */
const activeTab = ref('config')

/**
 * 标记Tab是否已加载过（避免重复加载）
 */
const tabLoaded = reactive({
  config: false,
  logs: false
})

/**
 * 加载状态
 */
const loading = ref(false)

/**
 * 配置分组列表
 */
const configGroups = ref([])

/**
 * 配置表单（按config_key组织）
 */
const configForm = reactive({})

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
 * 获取操作类型标签样式
 *
 * @param {string} operation - 操作类型
 * @returns {string} 标签样式类型
 */
const getOperationType = (operation) => {
  const typeMap = {
    'login': 'success',
    'create': 'primary',
    'update': 'warning',
    'delete': 'danger',
    'stock_in': 'success',
    'stock_out': 'warning',
    'check': 'info'
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
    'query_config': '查看配置'
  }
  return textMap[operation] || operation
}

/**
 * 格式化日期时间
 *
 * @param {string} datetime - 日期时间字符串
 * @returns {string} 格式化后的日期时间
 */
const formatDateTime = (datetime) => {
  if (!datetime) return ''
  const date = new Date(datetime)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

/**
 * 加载系统配置
 */
const loadConfig = async () => {
  try {
    const response = await getConfigs()
    configGroups.value = response.configs
    
    // 将配置值绑定到configForm
    Object.keys(configForm).forEach(key => delete configForm[key])
    
    configGroups.value.forEach(group => {
      group.configs.forEach(config => {
        // 根据类型转换值
        if (config.config_type === 'number') {
          configForm[config.config_key] = Number(config.config_value)
        } else if (config.config_type === 'boolean') {
          configForm[config.config_key] = config.config_value === 'true'
        } else {
          configForm[config.config_key] = config.config_value
        }
      })
    })
  } catch (error) {
    console.error('加载系统配置失败:', error)
    ElMessage.error('加载系统配置失败')
  }
}

/**
 * 处理保存配置
 */
const handleSaveConfig = async () => {
  try {
    loading.value = true
    
    // 构建批量更新请求数据
    const configs = []
    configGroups.value.forEach(group => {
      group.configs.forEach(config => {
        configs.push({
          config_key: config.config_key,
          config_value: String(configForm[config.config_key])
        })
      })
    })
    
    await updateConfig({ configs })
    ElMessage.success('配置保存成功')
  } catch (error) {
    console.error('保存配置失败:', error)
    ElMessage.error('配置保存失败')
  } finally {
    loading.value = false
  }
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
  loadConfig()
  loadOperationLogs() // 页面加载时直接加载日志
})


/**
 * 监听Tab切换
 */
watch(activeTab, (newTab, oldTab) => {
  if (newTab === 'logs' && !tabLoaded.logs) {
    loadOperationLogs()
    tabLoaded.logs = true
  } else if (newTab === 'config' && !tabLoaded.config) {
    loadConfig()
    tabLoaded.config = true
  }
})
</script>

<!-- 强制 Vite 重新编译 -->
<style scoped>
.settings-container {
  padding: 20px;
}

/**
 * 卡片头部
 */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 16px;
  font-weight: 600;
}

/**
 * 筛选表单布局
 */
.filter-form {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  align-items: center;
  margin-bottom: 20px;
}

/**
 * 筛选项布局
 */
.filter-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-item label {
  white-space: nowrap;
  margin-right: 8px;
}

.label-text {
  display: inline-block;
}
</style>