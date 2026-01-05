/**
 * CampusAssetManager/frontend/src/views/CheckView.vue
 * 盘点管理页面
 * 
 * 功能说明：
 * - 盘点单列表展示
 * - 创建盘点单
 * - 提交盘点结果
 * 
 * 作者：CampusAssetManager开发团队
 * 日期：2026-01-05
 */

<template>
  <LayoutComponent>
    <div class="check-container">
      <!-- 工具栏 -->
      <el-card class="toolbar-card">
        <el-button type="primary" @click="handleCreateCheck">创建盘点单</el-button>
      </el-card>
      
      <!-- 盘点单列表 -->
      <el-card class="table-card">
        <TableComponent
          :data="checkList"
          :loading="loading"
          :show-selection="false"
          :page="pagination.page"
          :limit="pagination.limit"
          :total="pagination.total"
          @update:page="handlePageChange"
          @update:limit="handleSizeChange"
        >
          <template #columns>
            <el-table-column prop="check_id" label="ID" width="80" align="center" />
            <el-table-column prop="check_name" label="盘点单名称" min-width="150" />
            <el-table-column prop="check_date" label="盘点日期" width="120" />
            <el-table-column prop="status" label="状态" width="100" align="center">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)">
                  {{ getStatusText(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="create_time" label="创建时间" width="180" />
            <el-table-column label="操作" width="180" align="center">
              <template #default="{ row }">
                <el-button type="primary" link @click="handleDetail(row)">详情</el-button>
                <el-button type="success" link @click="handleSubmit(row)" v-if="row.status === 'pending'">提交</el-button>
              </template>
            </el-table-column>
          </template>
        </TableComponent>
      </el-card>
    </div>
  </LayoutComponent>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import LayoutComponent from '@/components/common/LayoutComponent.vue'
import TableComponent from '@/components/common/TableComponent.vue'
import { getCheckList } from '@/api'

/**
 * 加载状态
 */
const loading = ref(false)

/**
 * 盘点单列表
 */
const checkList = ref([])

/**
 * 分页数据
 */
const pagination = reactive({
  page: 1,
  limit: 20,
  total: 0
})

/**
 * 获取状态类型
 * 
 * @param {string} status - 状态
 * @returns {string} 类型
 */
const getStatusType = (status) => {
  const statusMap = {
    'pending': 'warning',
    'completed': 'success'
  }
  return statusMap[status] || 'info'
}

/**
 * 获取状态文本
 * 
 * @param {string} status - 状态
 * @returns {string} 文本
 */
const getStatusText = (status) => {
  const statusMap = {
    'pending': '待盘点',
    'completed': '已完成'
  }
  return statusMap[status] || '未知'
}

/**
 * 加载盘点单列表
 */
const loadCheckList = async () => {
  try {
    loading.value = true
    const response = await getCheckList({
      page: pagination.page,
      page_size: pagination.limit
    })
    checkList.value = response.items
    pagination.total = response.total
  } catch (error) {
    ElMessage.error('加载盘点单列表失败')
  } finally {
    loading.value = false
  }
}

/**
 * 处理页码变化
 * 
 * @param {number} page - 页码
 */
const handlePageChange = (page) => {
  pagination.page = page
  loadCheckList()
}

/**
 * 处理每页数量变化
 * 
 * @param {number} limit - 每页数量
 */
const handleSizeChange = (limit) => {
  pagination.limit = limit
  pagination.page = 1
  loadCheckList()
}

/**
 * 处理创建盘点单
 */
const handleCreateCheck = () => {
  ElMessage.info('创建盘点单功能待实现')
}

/**
 * 处理详情
 * 
 * @param {Object} row - 行数据
 */
const handleDetail = (row) => {
  ElMessage.info(`查看盘点详情：${row.check_name}`)
}

/**
 * 处理提交
 * 
 * @param {Object} row - 行数据
 */
const handleSubmit = (row) => {
  ElMessage.info(`提交盘点：${row.check_name}`)
}

/**
 * 组件挂载时加载数据
 */
onMounted(() => {
  loadCheckList()
})
</script>

<style scoped>
.check-container {
  padding: 20px;
}

.toolbar-card {
  margin-bottom: 20px;
}

.table-card {
  height: calc(100vh - 250px);
}
</style>