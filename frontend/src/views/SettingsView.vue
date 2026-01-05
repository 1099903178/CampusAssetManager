/**
 * CampusAssetManager/frontend/src/views/SettingsView.vue
 * 系统设置页面
 * 
 * 功能说明：
 * - 系统配置管理
 * - 操作日志查询
 * - 用户权限设置
 * 
 * 作者：CampusAssetManager开发团队
 * 日期：2026-01-05
 */

<template>
    <div class="settings-container">
      <el-tabs v-model="activeTab" type="border-card">
        <!-- 系统配置 -->
        <el-tab-pane label="系统配置" name="config">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>系统配置</span>
                <el-button type="primary" @click="handleSaveConfig" :loading="loading">保存配置</el-button>
              </div>
            </template>
            
            <el-form :model="configForm" label-width="150px">
              <el-form-item label="系统名称">
                <el-input v-model="configForm.system_name" placeholder="请输入系统名称" />
              </el-form-item>
              
              <el-form-item label="最小库存预警">
                <el-input-number v-model="configForm.min_stock_alert" :min="0" />
              </el-form-item>
              
              <el-form-item label="最大库存预警">
                <el-input-number v-model="configForm.max_stock_alert" :min="0" />
              </el-form-item>
              
              <el-form-item label="盘点周期">
                <el-select v-model="configForm.check_period" placeholder="请选择盘点周期">
                  <el-option label="每日" value="daily" />
                  <el-option label="每周" value="weekly" />
                  <el-option label="每月" value="monthly" />
                </el-select>
              </el-form-item>
            </el-form>
          </el-card>
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
            
            <el-form :inline="true" :model="logSearchForm">
              <el-form-item label="操作人">
                <el-input v-model="logSearchForm.username" placeholder="请输入操作人" clearable />
              </el-form-item>
              
              <el-form-item label="操作类型">
                <el-select v-model="logSearchForm.operation_type" placeholder="请选择操作类型" clearable>
                  <el-option label="登录" value="login" />
                  <el-option label="入库" value="stock_in" />
                  <el-option label="出库" value="stock_out" />
                  <el-option label="盘点" value="check" />
                </el-select>
              </el-form-item>
              
              <el-form-item label="时间范围">
                <el-date-picker
                  v-model="logSearchForm.dateRange"
                  type="daterange"
                  range-separator="至"
                  start-placeholder="开始日期"
                  end-placeholder="结束日期"
                />
              </el-form-item>
              
              <el-form-item>
                <el-button type="primary" @click="loadOperationLogs">搜索</el-button>
                <el-button @click="logSearchForm = {}">重置</el-button>
              </el-form-item>
            </el-form>
            
            <TableComponent
              :data="logList"
              :loading="loading"
              :show-pagination="true"
              :page="logPagination.page"
              :limit="logPagination.limit"
              :total="logPagination.total"
              @update:page="handleLogPageChange"
              @update:limit="handleLogSizeChange"
            >
              <template #columns>
                <el-table-column prop="log_id" label="ID" width="80" align="center" />
                <el-table-column prop="username" label="操作人" width="120" />
                <el-table-column prop="operation_type" label="操作类型" width="120" />
                <el-table-column prop="operation_detail" label="操作详情" min-width="200" show-overflow-tooltip />
                <el-table-column prop="ip_address" label="IP地址" width="140" />
                <el-table-column prop="operation_time" label="操作时间" width="180" />
              </template>
            </TableComponent>
          </el-card>
        </el-tab-pane>
        
        <!-- 用户管理 -->
        <el-tab-pane label="用户管理" name="users">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>用户管理</span>
                <el-button type="primary" size="small" @click="handleAddUser">新增用户</el-button>
              </div>
            </template>
            
            <TableComponent
              :data="userList"
              :loading="loading"
              :show-pagination="true"
              :page="userPagination.page"
              :limit="userPagination.limit"
              :total="userPagination.total"
              @update:page="handleUserPageChange"
              @update:limit="handleUserSizeChange"
            >
              <template #columns>
                <el-table-column prop="user_id" label="ID" width="80" align="center" />
                <el-table-column prop="username" label="用户名" width="150" />
                <el-table-column prop="role" label="角色" width="120">
                  <template #default="{ row }">
                    <el-tag :type="getRoleType(row.role)">
                      {{ getRoleText(row.role) }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="create_time" label="创建时间" width="180" />
                <el-table-column label="操作" width="180" align="center">
                  <template #default="{ row }">
                    <el-button type="primary" link @click="handleEditUser(row)">编辑</el-button>
                    <el-button type="danger" link @click="handleDeleteUser(row)">删除</el-button>
                  </template>
                </el-table-column>
              </template>
            </TableComponent>
          </el-card>
        </el-tab-pane>
      </el-tabs>
    </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import TableComponent from '@/components/common/TableComponent.vue'
import { getConfigs, updateConfig, getOperationLogs } from '@/api'

/**
 * 当前激活的Tab
 */
const activeTab = ref('config')

/**
 * 加载状态
 */
const loading = ref(false)

/**
 * 配置表单
 */
const configForm = reactive({
  system_name: '校物通校园物品管理系统',
  min_stock_alert: 10,
  max_stock_alert: 1000,
  check_period: 'monthly'
})

/**
 * 日志搜索表单
 */
const logSearchForm = reactive({
  username: '',
  operation_type: '',
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
  limit: 20,
  total: 0
})

/**
 * 用户列表
 */
const userList = ref([])

/**
 * 用户分页数据
 */
const userPagination = reactive({
  page: 1,
  limit: 20,
  total: 0
})

/**
 * 获取角色类型
 * 
 * @param {string} role - 角色
 * @returns {string} 类型
 */
const getRoleType = (role) => {
  const roleMap = {
    'super_admin': 'danger',
    'admin': 'warning',
    'user': 'success'
  }
  return roleMap[role] || 'info'
}

/**
 * 获取角色文本
 * 
 * @param {string} role - 角色
 * @returns {string} 文本
 */
const getRoleText = (role) => {
  const roleMap = {
    'super_admin': '超级管理员',
    'admin': '管理员',
    'user': '普通用户'
  }
  return roleMap[role] || '未知'
}

/**
 * 处理保存配置
 */
const handleSaveConfig = async () => {
  try {
    loading.value = true
    await updateConfig(configForm)
    ElMessage.success('配置保存成功')
  } catch (error) {
    ElMessage.error('配置保存失败')
  } finally {
    loading.value = false
  }
}

/**
 * 加载操作日志
 */
const loadOperationLogs = async () => {
  try {
    loading.value = true
    const response = await getOperationLogs({
      page: logPagination.page,
      page_size: logPagination.limit,
      ...logSearchForm
    })
    logList.value = response.items
    logPagination.total = response.total
  } catch (error) {
    ElMessage.error('加载操作日志失败')
  } finally {
    loading.value = false
  }
}

/**
 * 处理日志页码变化
 * 
 * @param {number} page - 页码
 */
const handleLogPageChange = (page) => {
  logPagination.page = page
  loadOperationLogs()
}

/**
 * 处理日志每页数量变化
 * 
 * @param {number} limit - 每页数量
 */
const handleLogSizeChange = (limit) => {
  logPagination.limit = limit
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
 * 处理新增用户
 */
const handleAddUser = () => {
  ElMessage.info('新增用户功能待实现')
}

/**
 * 处理编辑用户
 * 
 * @param {Object} row - 行数据
 */
const handleEditUser = (row) => {
  ElMessage.info(`编辑用户：${row.username}`)
}

/**
 * 处理删除用户
 * 
 * @param {Object} row - 行数据
 */
const handleDeleteUser = (row) => {
  ElMessageBox.confirm(
    `确定要删除用户"${row.username}"吗？`,
    '删除确认',
    {
      type: 'warning'
    }
  ).then(() => {
    ElMessage.info('删除用户功能待实现')
  })
}

/**
 * 处理用户页码变化
 * 
 * @param {number} page - 页码
 */
const handleUserPageChange = (page) => {
  userPagination.page = page
  ElMessage.info('加载用户列表功能待实现')
}

/**
 * 处理用户每页数量变化
 * 
 * @param {number} limit - 每页数量
 */
const handleUserSizeChange = (limit) => {
  userPagination.limit = limit
  userPagination.page = 1
  ElMessage.info('加载用户列表功能待实现')
}

/**
 * 加载系统配置
 */
const loadConfig = async () => {
  try {
    const response = await getConfigs()
    Object.assign(configForm, response)
  } catch (error) {
    console.error('加载系统配置失败:', error)
  }
}

/**
 * 组件挂载时加载数据
 */
onMounted(() => {
  loadConfig()
})
</script>

<script>
import { onMounted } from 'vue'
export default {
  name: 'SettingsView'
}
</script>

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
</style>