/**
 * CampusAssetManager/frontend/src/components/common/StockDetailDialog.vue
 * 库存详情对话框组件
 * 
 * 功能说明：
 * - 显示物品基本信息
 * - 显示物品的入库记录（支持分页、搜索）
 * - 显示物品的出库记录（支持分页、搜索）
 * 
 * 设计原则：
 * - 声明式：使用Vue Composition API
 * - 组件化：使用Element Plus组件
 * - 响应式：使用ref和reactive管理状态
 * 
 * 作者：CampusAssetManager开发团队
 * 日期：2026-01-08
 */

<template>
  <el-dialog
    v-model="visible"
    title="库存详情"
    width="900px"
    :before-close="handleClose"
  >
    <el-tabs v-model="activeTab" type="border-card">
      <!-- Tab1: 基本信息 -->
      <el-tab-pane label="基本信息" name="basic">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="物品ID">{{ goods.goods_id }}</el-descriptions-item>
          <el-descriptions-item label="物品名称">{{ goods.goods_name }}</el-descriptions-item>
          <el-descriptions-item label="物品编码">{{ goods.goods_code }}</el-descriptions-item>
          <el-descriptions-item label="分类">{{ goods.category_name }}</el-descriptions-item>
          <el-descriptions-item label="规格">{{ goods.specification || '-' }}</el-descriptions-item>
          <el-descriptions-item label="单位">{{ goods.unit }}</el-descriptions-item>
          <el-descriptions-item label="采购价">¥{{ goods.purchase_price?.toFixed(2) }}</el-descriptions-item>
          <el-descriptions-item label="零售价">
            {{ goods.retail_price ? '¥' + goods.retail_price.toFixed(2) : '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(goods.status)">
              {{ getStatusText(goods.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="当前库存">{{ goods.current_stock || 0 }}</el-descriptions-item>
          <el-descriptions-item label="描述" :span="2">{{ goods.description || '-' }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatDate(goods.create_time) }}</el-descriptions-item>
          <el-descriptions-item label="更新时间">{{ formatDate(goods.update_time) }}</el-descriptions-item>
        </el-descriptions>
      </el-tab-pane>
      
      <!-- Tab2: 入库记录 -->
      <el-tab-pane label="入库记录" name="stock-in">
        <el-form :inline="true" :model="inSearchForm">
          <el-form-item label="搜索">
            <el-input
              v-model="inSearchForm.search"
              placeholder="入库单号"
              clearable
              style="width: 200px"
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="loadStockInList">搜索</el-button>
            <el-button @click="handleInReset">重置</el-button>
          </el-form-item>
        </el-form>
        
        <el-table :data="stockInList" :loading="inLoading" style="width: 100%" max-height="400">
          <el-table-column prop="in_id" label="ID" width="80" align="center" />
          <el-table-column prop="in_no" label="入库单号" width="160" />
          <el-table-column prop="goods_name" label="物品名称" width="120" />
          <el-table-column prop="goods_code" label="物品编码" width="120" />
          <el-table-column prop="category_name" label="分类名称" width="120" />
          <el-table-column prop="in_quantity" label="入库数量" width="100" align="right" />
          <el-table-column prop="unit_price" label="单价" width="100" align="right">
            <template #default="{ row }">
              ¥{{ row.unit_price?.toFixed(2) }}
            </template>
          </el-table-column>
          <el-table-column prop="total_amount" label="总金额" width="120" align="right">
            <template #default="{ row }">
              ¥{{ row.total_amount?.toFixed(2) }}
            </template>
          </el-table-column>
          <el-table-column prop="batch_no" label="批次号" width="120" />
          <el-table-column prop="supplier" label="供应商" width="150" />
          <el-table-column prop="in_time" label="入库时间" width="160" align="center">
            <template #default="{ row }">
              {{ formatDate(row.in_time) }}
            </template>
          </el-table-column>
        </el-table>
        
        <el-pagination
          v-model:current-page="inPagination.page"
          v-model:page-size="inPagination.page_size"
          :total="inPagination.total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          @current-change="loadStockInList"
          @size-change="loadStockInList"
          style="margin-top: 20px; justify-content: flex-end"
        />
      </el-tab-pane>
      
      <!-- Tab3: 出库记录 -->
      <el-tab-pane label="出库记录" name="stock-out">
        <el-form :inline="true" :model="outSearchForm">
          <el-form-item label="搜索">
            <el-input
              v-model="outSearchForm.search"
              placeholder="出库单号"
              clearable
              style="width: 200px"
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="loadStockOutList">搜索</el-button>
            <el-button @click="handleOutReset">重置</el-button>
          </el-form-item>
        </el-form>
        
        <el-table :data="stockOutList" :loading="outLoading" style="width: 100%" max-height="400">
          <el-table-column prop="out_id" label="ID" width="80" align="center" />
          <el-table-column prop="out_no" label="出库单号" width="160" />
          <el-table-column prop="goods_name" label="物品名称" width="120" />
          <el-table-column prop="goods_code" label="物品编码" width="120" />
          <el-table-column prop="category_name" label="分类名称" width="120" />
          <el-table-column prop="out_quantity" label="出库数量" width="100" align="right" />
          <el-table-column prop="unit_price" label="单价" width="100" align="right">
            <template #default="{ row }">
              ¥{{ row.unit_price?.toFixed(2) }}
            </template>
          </el-table-column>
          <el-table-column prop="total_amount" label="总金额" width="120" align="right">
            <template #default="{ row }">
              ¥{{ row.total_amount?.toFixed(2) }}
            </template>
          </el-table-column>
          <el-table-column prop="receiver" label="接收人" width="100" />
          <el-table-column prop="department" label="接收部门" width="120" />
          <el-table-column prop="purpose" label="用途" width="150" />
          <el-table-column prop="out_time" label="出库时间" width="160" align="center">
            <template #default="{ row }">
              {{ formatDate(row.out_time) }}
            </template>
          </el-table-column>
        </el-table>
        
        <el-pagination
          v-model:current-page="outPagination.page"
          v-model:page-size="outPagination.page_size"
          :total="outPagination.total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          @current-change="loadStockOutList"
          @size-change="loadStockOutList"
          style="margin-top: 20px; justify-content: flex-end"
        />
      </el-tab-pane>
    </el-tabs>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { getStockInList, getStockOutList } from '@/api/stock'

/**
 * Props定义
 */
const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  goods: {
    type: Object,
    required: true
  }
})

/**
 * Emits定义
 */
const emit = defineEmits(['update:modelValue'])

/**
 * 对话框可见性
 */
const visible = ref(props.modelValue)

/**
 * 当前激活的Tab
 */
const activeTab = ref('basic')

/**
 * ==================== 入库记录相关 ====================
 */

/**
 * 入库记录加载状态
 */
const inLoading = ref(false)

/**
 * 入库记录列表
 */
const stockInList = ref([])

/**
 * 入库记录搜索表单
 */
const inSearchForm = reactive({
  search: ''
})

/**
 * 入库记录分页数据
 */
const inPagination = reactive({
  page: 1,
  page_size: 10,
  total: 0
})

/**
 * 加载入库记录列表
 */
const loadStockInList = async () => {
  try {
    inLoading.value = true
    
    // 检查goods_id是否存在
    if (!props.goods || !props.goods.goods_id) {
      ElMessage.error('物品信息不完整')
      return
    }
    
    // 确保goods_id是数字类型
    const goodsId = parseInt(props.goods.goods_id, 10)
    
    // 构建查询参数
    const queryParams = {
      page: inPagination.page,
      page_size: inPagination.page_size,
      goods_id: goodsId,
      search: inSearchForm.search || undefined
    }
    
    const response = await getStockInList(queryParams)
    stockInList.value = response.items
    inPagination.total = response.total
  } catch (error) {
    console.error('加载入库记录失败:', error)
    ElMessage.error('加载入库记录失败')
  } finally {
    inLoading.value = false
  }
}

/**
 * 处理入库记录搜索重置
 */
const handleInReset = () => {
  inSearchForm.search = ''
  inPagination.page = 1
  loadStockInList()
}

/**
 * ==================== 出库记录相关 ====================
 */

/**
 * 出库记录加载状态
 */
const outLoading = ref(false)

/**
 * 出库记录列表
 */
const stockOutList = ref([])

/**
 * 出库记录搜索表单
 */
const outSearchForm = reactive({
  search: ''
})

/**
 * 出库记录分页数据
 */
const outPagination = reactive({
  page: 1,
  page_size: 10,
  total: 0
})

/**
 * 加载出库记录列表
 */
const loadStockOutList = async () => {
  try {
    outLoading.value = true
    
    // 检查goods_id是否存在
    if (!props.goods || !props.goods.goods_id) {
      ElMessage.error('物品信息不完整')
      return
    }
    
    // 确保goods_id是数字类型
    const goodsId = parseInt(props.goods.goods_id, 10)
    
    const response = await getStockOutList({
      page: outPagination.page,
      page_size: outPagination.page_size,
      goods_id: goodsId,
      search: outSearchForm.search || undefined
    })
    stockOutList.value = response.items
    outPagination.total = response.total
  } catch (error) {
    console.error('加载出库记录失败:', error)
    ElMessage.error('加载出库记录失败')
  } finally {
    outLoading.value = false
  }
}

/**
 * 处理出库记录搜索重置
 */
const handleOutReset = () => {
  outSearchForm.search = ''
  outPagination.page = 1
  loadStockOutList()
}

/**
 * ==================== 工具函数 ====================
 */

/**
 * 格式化日期时间（转换为本地时间）
 *
 * @param {string} dateTime - 日期时间字符串（UTC）
 * @returns {string} 格式化后的日期时间（本地时间UTC+8）
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
 * 获取状态类型
 * 
 * @param {number} status - 状态值
 * @returns {string} 状态类型
 */
const getStatusType = (status) => {
  const statusMap = {
    1: 'success',
    2: 'danger',
    3: 'warning'
  }
  return statusMap[status] || 'info'
}

/**
 * 获取状态文本
 * 
 * @param {number} status - 状态值
 * @returns {string} 状态文本
 */
const getStatusText = (status) => {
  const statusMap = {
    1: '正常',
    2: '报废',
    3: '维修中'
  }
  return statusMap[status] || '未知'
}

/**
 * 处理对话框关闭
 */
const handleClose = () => {
  visible.value = false
}

/**
 * 监听modelValue变化
 */
watch(() => props.modelValue, (newVal) => {
  visible.value = newVal
  if (newVal) {
    // 对话框打开时，重置Tab到基本信息
    activeTab.value = 'basic'
    // 加载入库和出库记录
    loadStockInList()
    loadStockOutList()
  }
})

/**
 * 监听goods变化
 */
watch(() => props.goods, (newVal) => {
  if (newVal && visible.value) {
    // 当goods变化且对话框打开时，重新加载记录
    loadStockInList()
    loadStockOutList()
  }
}, { deep: true })

/**
 * 监听visible变化
 */
watch(visible, (newVal) => {
  emit('update:modelValue', newVal)
})
</script>

<style scoped>
.el-pagination {
  display: flex;
}
</style>