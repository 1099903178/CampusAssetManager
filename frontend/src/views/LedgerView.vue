/**
 * CampusAssetManager/frontend/src/views/LedgerView.vue
 * 库存台账查询页面
 * 
 * 功能说明：
 * - 查询库存台账（合并入库、出库、盘点记录）
 * - 支持时间范围筛选
 * - 支持操作类型筛选（入库/出库/盘点）
 * - 显示台账详情
 * 
 * 作者：CampusAssetManager开发团队
 * 日期：2026-01-13
 */

<template>
  <div class="ledger-container">
    <!-- 工具栏 -->
    <el-card class="toolbar-card">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索操作单号、物品名称"
            clearable
            @clear="handleSearch"
            @keyup.enter="handleSearch"
          >
            <template #append>
              <el-button @click="handleSearch">搜索</el-button>
            </template>
          </el-input>
        </el-col>
        <el-col :span="4">
          <el-select
            v-model="operationTypeFilter"
            placeholder="操作类型"
            clearable
            @change="handleSearch"
          >
            <el-option label="入库" value="in" />
            <el-option label="出库" value="out" />
            <el-option label="盘点" value="check" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
            @change="handleSearch"
          />
        </el-col>
        <el-col :span="8" style="text-align: right;">
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-col>
      </el-row>
    </el-card>
    
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stats-card">
          <div class="stats-content">
            <div class="stats-label">总记录数</div>
            <div class="stats-value">{{ pagination.total }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stats-card stats-in">
          <div class="stats-content">
            <div class="stats-label">入库次数</div>
            <div class="stats-value">{{ stats.inCount }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stats-card stats-out">
          <div class="stats-content">
            <div class="stats-label">出库次数</div>
            <div class="stats-value">{{ stats.outCount }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stats-card stats-check">
          <div class="stats-content">
            <div class="stats-label">盘点次数</div>
            <div class="stats-value">{{ stats.checkCount }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 台账列表 -->
    <el-card class="table-card">
      <TableComponent
        :data="ledgerList"
        :loading="loading"
        :show-selection="false"
        :page="pagination.page"
        :limit="pagination.page_size"
        :total="pagination.total"
        @update:page="handlePageChange"
        @update:limit="handleSizeChange"
      >
        <template #columns>
          <el-table-column prop="operation_no" label="操作单号" min-width="150">
            <template #default="{ row }">
              <el-button type="primary" link @click="handleDetail(row)">
                {{ row.operation_no }}
              </el-button>
            </template>
          </el-table-column>
          <el-table-column prop="operation_type" label="操作类型" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="getOperationTypeColor(row.operation_type)">
                {{ getOperationTypeText(row.operation_type) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="goods_name" label="物品名称" min-width="150" />
          <el-table-column prop="goods_code" label="物品编码" width="120" />
          <el-table-column prop="category_name" label="分类" width="100" />
          <el-table-column prop="quantity" label="数量" width="80" align="center" />
          <el-table-column prop="stock_before" label="操作前库存" width="100" align="center" />
          <el-table-column prop="stock_after" label="操作后库存" width="100" align="center" />
          <el-table-column prop="operator_name" label="操作人" width="100" />
          <el-table-column prop="operation_time" label="操作时间" width="180">
            <template #default="{ row }">
              {{ formatDate(row.operation_time) }}
            </template>
          </el-table-column>
        </template>
      </TableComponent>
    </el-card>
    
    <!-- 台账详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="台账详情"
      width="700px"
    >
      <el-descriptions :column="2" border>
        <el-descriptions-item label="操作单号">{{ currentDetail.operation_no }}</el-descriptions-item>
        <el-descriptions-item label="操作类型">
          <el-tag :type="getOperationTypeColor(currentDetail.operation_type)">
            {{ getOperationTypeText(currentDetail.operation_type) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="物品名称">{{ currentDetail.goods_name }}</el-descriptions-item>
        <el-descriptions-item label="物品编码">{{ currentDetail.goods_code }}</el-descriptions-item>
        <el-descriptions-item label="分类">{{ currentDetail.category_name }}</el-descriptions-item>
        <el-descriptions-item label="数量">{{ currentDetail.quantity }}</el-descriptions-item>
        <el-descriptions-item label="操作前库存">{{ currentDetail.stock_before }}</el-descriptions-item>
        <el-descriptions-item label="操作后库存">{{ currentDetail.stock_after }}</el-descriptions-item>
        <el-descriptions-item label="操作人">{{ currentDetail.operator_name }}</el-descriptions-item>
        <el-descriptions-item label="操作时间">{{ currentDetail.operation_time }}</el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">{{ currentDetail.remark || '-' }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import TableComponent from '@/components/common/TableComponent.vue'
import { getStockLedger } from '@/api/stock'

/**
 * 加载状态
 */
const loading = ref(false)

/**
 * 台账列表
 */
const ledgerList = ref([])

/**
 * 分页数据
 */
const pagination = reactive({
  page: 1,
  page_size: 20,
  total: 0
})

/**
 * 搜索关键词
 */
const searchKeyword = ref('')

/**
 * 操作类型筛选
 */
const operationTypeFilter = ref('')

/**
 * 日期范围
 */
const dateRange = ref([])

/**
 * 对话框显示状态
 */
const detailDialogVisible = ref(false)

/**
 * 当前详情
 */
const currentDetail = ref({})

/**
 * 统计数据
 */
const stats = reactive({
  inCount: 0,
  outCount: 0,
  checkCount: 0
})

/**
 * 获取操作类型颜色
 * 
 * @param {string} type - 操作类型
 * @returns {string} 颜色类型
 */
const getOperationTypeColor = (type) => {
  const colorMap = {
    'in': 'success',
    'out': 'warning',
    'check': 'info'
  }
  return colorMap[type] || 'info'
}

/**
 * 获取操作类型文本
 * 
 * @param {string} type - 操作类型
 * @returns {string} 文本
 */
const getOperationTypeText = (type) => {
  const textMap = {
    'in': '入库',
    'out': '出库',
    'check': '盘点'
  }
  return textMap[type] || '未知'
}

/**
 * 加载台账列表
 */
const loadLedgerList = async () => {
  try {
    loading.value = true
    const params = {
      page: pagination.page,
      page_size: pagination.page_size
    }
    
    if (searchKeyword.value) {
      params.search = searchKeyword.value
    }
    if (operationTypeFilter.value) {
      params.operation_type = operationTypeFilter.value
    }
    if (dateRange.value && dateRange.value.length === 2) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }
    
    // 响应拦截器已自动处理，直接返回 data
    const response = await getStockLedger(params)
    ledgerList.value = response.items
    pagination.total = response.total
    
    // 更新统计数据
    updateStats()
  } catch (error) {
    ElMessage.error('加载台账列表失败：' + error.message)
  } finally {
    loading.value = false
  }
}

/**
 * 更新统计数据
 */
const updateStats = () => {
  stats.inCount = ledgerList.value.filter(item => item.operation_type === 'in').length
  stats.outCount = ledgerList.value.filter(item => item.operation_type === 'out').length
  stats.checkCount = ledgerList.value.filter(item => item.operation_type === 'check').length
}

/**
 * 处理搜索
 */
const handleSearch = () => {
  pagination.page = 1
  loadLedgerList()
}

/**
 * 处理重置
 */
const handleReset = () => {
  searchKeyword.value = ''
  operationTypeFilter.value = ''
  dateRange.value = []
  pagination.page = 1
  loadLedgerList()
}

/**
 * 处理页码变化
 * 
 * @param {number} page - 页码
 */
const handlePageChange = (page) => {
  pagination.page = page
  loadLedgerList()
}

/**
 * 处理每页数量变化
 * 
 * @param {number} size - 每页数量
 */
const handleSizeChange = (size) => {
  pagination.page_size = size
  pagination.page = 1
  loadLedgerList()
}

/**
 * 格式化日期时间（转换为本地时间）
 *
 * @param {String} dateTime - 日期时间字符串（UTC）
 * @returns {String} 格式化后的日期时间（本地时间 UTC+8）
 */
const formatDate = (dateTime) => {
  if (!dateTime) return '-'
  const date = new Date(dateTime)
  
  // 转换为本地时间（UTC+8小时）
  const localTime = new Date(date.getTime() + 8 * 60 * 60 * 1000)
  
  const year = localTime.getFullYear()
  const month = String(localTime.getMonth() + 1).padStart(2, '0')
  const day = String(localTime.getDate()).padStart(2, '0')
  const hours = String(localTime.getHours()).padStart(2, '0')
  const minutes = String(localTime.getMinutes()).padStart(2, '0')
  const seconds = String(localTime.getSeconds()).padStart(2, '0')
  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
}

/**
 * 处理详情
 *
 * @param {Object} row - 行数据
 */
const handleDetail = (row) => {
  currentDetail.value = row
  detailDialogVisible.value = true
}

/**
 * 组件挂载时加载数据
 */
onMounted(() => {
  loadLedgerList()
})
</script>

<style scoped>
.ledger-container {
  padding: 20px;
}

.toolbar-card {
  margin-bottom: 20px;
}

.stats-row {
  margin-bottom: 20px;
}

.stats-card {
  cursor: pointer;
  transition: all 0.3s;
}

.stats-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.stats-content {
  text-align: center;
  padding: 10px 0;
}

.stats-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 10px;
}

.stats-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.stats-in .stats-value {
  color: #67C23A;
}

.stats-out .stats-value {
  color: #E6A23C;
}

.stats-check .stats-value {
  color: #409EFF;
}

.table-card {
  height: calc(100vh - 420px);
}
</style>