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
  <div class="page-container">
    <div class="glass-toolbar">
      <div class="toolbar-left">
        <h2 class="page-title">库存台账</h2>
      </div>
      
      <div class="toolbar-center">
        <!-- 筛选组件内联显示 -->
        <el-input
          v-model="searchKeyword"
          placeholder="搜索单号/物品..."
          :prefix-icon="Search"
          clearable
          class="search-input-inline"
          @clear="handleSearch"
          @keyup.enter="handleSearch"
        />
        
        <el-select
          v-model="operationTypeFilter"
          placeholder="操作类型"
          clearable
          class="filter-select-inline"
          @change="handleSearch"
        >
          <el-option label="入库" value="in" />
          <el-option label="出库" value="out" />
          <el-option label="盘点" value="check" />
        </el-select>
        
        <el-date-picker
          v-model="dateRange"
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
        <el-button @click="handleReset">重置</el-button>
      </div>
    </div>
    
    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon stat-total">
          <el-icon><Document /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-label">总记录数</div>
          <div class="stat-value num-font">{{ pagination.total }}</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon stat-in">
          <el-icon><Plus /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-label">入库次数</div>
          <div class="stat-value num-font">{{ stats.inCount }}</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon stat-out">
          <el-icon><Minus /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-label">出库次数</div>
          <div class="stat-value num-font">{{ stats.outCount }}</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon stat-check">
          <el-icon><Search /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-label">盘点次数</div>
          <div class="stat-value num-font">{{ stats.checkCount }}</div>
        </div>
      </div>
    </div>
    
    <!-- 台账列表 -->
    <div class="content-card">
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
              <span class="code-text">{{ row.operation_no }}</span>
            </template>
          </el-table-column>
          
          <el-table-column prop="operation_type" label="操作类型" width="100" align="center">
            <template #default="{ row }">
              <div class="status-pill" :class="getOperationTypeClass(row.operation_type)">
                <span class="dot"></span>
                <span>{{ getOperationTypeText(row.operation_type) }}</span>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column prop="goods_name" label="物品名称" min-width="150">
            <template #default="{ row }">
              <span class="text-main fw-600">{{ row.goods_name }}</span>
            </template>
          </el-table-column>
          
          <el-table-column prop="goods_code" label="物品编码" width="120">
            <template #default="{ row }">
              <span class="code-text">{{ row.goods_code }}</span>
            </template>
          </el-table-column>
          
          <el-table-column prop="category_name" label="分类" width="100" />
          
          <el-table-column prop="quantity" label="数量" width="90" align="right">
            <template #default="{ row }">
              <span class="num-font">{{ row.quantity || 0 }}</span>
            </template>
          </el-table-column>
          
          <el-table-column prop="stock_before" label="操作前库存" width="100" align="right">
            <template #default="{ row }">
              <span class="num-font secondary-num">{{ row.stock_before || 0 }}</span>
            </template>
          </el-table-column>
          
          <el-table-column prop="stock_after" label="操作后库存" width="100" align="right">
            <template #default="{ row }">
              <span class="num-font">{{ row.stock_after || 0 }}</span>
            </template>
          </el-table-column>
          
          <el-table-column prop="operator_name" label="操作人" width="100" />
          
          <el-table-column prop="operation_time" label="操作时间" width="160" align="center">
            <template #default="{ row }">
              {{ formatDate(row.operation_time) }}
            </template>
          </el-table-column>
        </template>
      </TableComponent>
    </div>
    
    <!-- 台账详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="台账详情"
      width="700px"
      class="custom-dialog"
    >
      <el-descriptions :column="2" border>
        <el-descriptions-item label="操作单号">{{ currentDetail.operation_no }}</el-descriptions-item>
        <el-descriptions-item label="操作类型">
          <div class="status-pill" :class="getOperationTypeClass(currentDetail.operation_type)">
            <span class="dot"></span>
            <span>{{ getOperationTypeText(currentDetail.operation_type) }}</span>
          </div>
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
import { Search, Plus, Minus, Document } from '@element-plus/icons-vue'
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
 * 获取操作类型样式类
 *
 * @param {string} type - 操作类型
 * @returns {string} 样式类名
 */
const getOperationTypeClass = (type) => {
  const classMap = {
    'in': 's-active',
    'out': 's-warning',
    'check': 's-info'
  }
  return classMap[type] || ''
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
.page-container {
  max-width: 1500px;
  margin: 0 auto;
  animation: fadeIn 0.4s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* 1. 悬浮工具栏 */
.glass-toolbar {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(241, 245, 249, 0.8);
  padding: 12px 20px;
  border-radius: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  box-shadow: 0 4px 20px -5px rgba(0, 0, 0, 0.05);
  position: sticky;
  top: 0;
  z-index: 10;
  flex-wrap: wrap;
  gap: 12px;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 0;
  min-width: auto;
}
.page-title {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
  white-space: nowrap;
}

.toolbar-center {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
  min-width: 0;
}

.search-input-inline {
  width: 220px;
  flex-shrink: 0;
  max-width: 220px;
}
.filter-select-inline {
  width: 100px;
  flex-shrink: 0;
  max-width: 100px;
}
.date-picker-inline {
  width: 220px;
  flex-shrink: 0;
  max-width: 220px;
}

.toolbar-right {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-shrink: 0;
}

/* 2. 统计卡片 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
  border: 1px solid rgba(241, 245, 249, 0.8);
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px -5px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  flex-shrink: 0;
}

.stat-total { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
.stat-in { background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; }
.stat-out { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); color: white; }
.stat-check { background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%); color: white; }

.stat-content {
  flex: 1;
}

.stat-label {
  font-size: 13px;
  color: #64748b;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #1e293b;
}

/* 3. 内容卡片 */
.content-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
  min-height: 500px;
}

/* 4. 字体与细节优化 */
.num-font {
  font-family: 'Oswald', sans-serif !important;
  font-weight: 500;
  letter-spacing: -0.2px;
}

.secondary-num { color: #94a3b8; font-size: 13px; }
.code-text { color: #64748b; font-size: 13px; font-family: 'Consolas', monospace; }
.fw-600 { font-weight: 600; }
.text-main { color: #1e293b; }

/* 5. 状态标签设计 */
.status-pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
}
.dot { width: 6px; height: 6px; border-radius: 50%; }

.s-active { background: #f0fdf4; color: #16a34a; }
.s-active .dot { background: #10b981; box-shadow: 0 0 6px #10b981; }

.s-danger { background: #fef2f2; color: #dc2626; }
.s-danger .dot { background: #ef4444; }

.s-warning { background: #fffbeb; color: #d97706; }
.s-warning .dot { background: #f59e0b; }

.s-info { background: #eff6ff; color: #2563eb; }
.s-info .dot { background: #3b82f6; }

/* 6. 按钮样式调整 */
.edit-btn {
  color: #3b82f6 !important;
  font-weight: 500;
}
.edit-btn:hover {
  color: #2563eb !important;
}

/* 7. 对话框样式 */
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* 响应式适配 */
@media (max-width: 1400px) {
  .search-input-inline {
    width: 180px;
    max-width: 180px;
  }
  .date-picker-inline {
    width: 200px;
    max-width: 200px;
  }
}

@media (max-width: 1200px) {
  .glass-toolbar {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }
  .toolbar-left {
    width: 100%;
    justify-content: flex-start;
  }
  .toolbar-center {
    width: 100%;
    flex-wrap: wrap;
  }
  .search-input-inline,
  .filter-select-inline,
  .date-picker-inline {
    width: 180px;
    max-width: none;
  }
  .toolbar-right {
    width: 100%;
    justify-content: flex-start;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .glass-toolbar {
    padding: 12px 16px;
  }
  .page-title {
    font-size: 16px;
  }
  .toolbar-center {
    flex-direction: column;
    align-items: stretch;
  }
  .search-input-inline,
  .filter-select-inline,
  .date-picker-inline {
    width: 100%;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>