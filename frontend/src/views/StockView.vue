
/**
 * CampusAssetManager/frontend/src/views/StockView.vue
 * 库存管理页面
 * 
 * 功能说明：
 * - 库存列表展示
 * - 入库出库操作
 * - 库存查询
 * - 查看物品详情（包含入库、出库记录）
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
  <div class="stock-container">
    <!-- 工具栏 -->
      <el-card class="toolbar-card">
        <el-form :inline="true" :model="searchForm">
          <el-form-item label="物品名称">
            <el-input
              v-model="searchForm.goods_name"
              placeholder="请输入物品名称"
              clearable
            />
          </el-form-item>
          
          <el-form-item>
            <el-button type="primary" @click="loadStockList">搜索</el-button>
            <el-button @click="handleReset">重置</el-button>
          </el-form-item>
        </el-form>
        
        <el-button type="success" @click="handleStockIn">入库</el-button>
        <el-button type="warning" @click="handleStockOut">出库</el-button>
      </el-card>
      
      <!-- 库存列表 -->
      <el-card class="table-card">
        <TableComponent
          :data="stockList"
          :loading="loading"
          :show-selection="false"
          :page="pagination.page"
          :limit="pagination.limit"
          :total="pagination.total"
          @update:page="handlePageChange"
          @update:limit="handleSizeChange"
        >
          <template #columns>
            <el-table-column prop="goods_id" label="物品ID" width="80" align="center" />
            <el-table-column prop="goods_name" label="物品名称" min-width="150" />
            <el-table-column prop="category_name" label="分类名称" width="120" />
            <el-table-column prop="current_stock" label="当前库存" width="100" align="right">
              <template #default="{ row }">
                <span :class="{ 'low-stock-warning': row.current_stock <= 0 }">
                  {{ row.current_stock || 0 }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="80" align="center">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)" size="small">
                  {{ getStatusText(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="update_time" label="更新时间" width="160" align="center">
              <template #default="{ row }">
                {{ formatDate(row.update_time) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100" align="center" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" link @click="handleDetail(row)">详情</el-button>
              </template>
            </el-table-column>
          </template>
        </TableComponent>
      </el-card>
      
      <!-- 入库对话框 -->
      <el-dialog
        v-model="inDialogVisible"
        title="物品入库"
        width="600px"
        @close="handleInDialogClose"
      >
        <el-form
          ref="inFormRef"
          :model="inFormData"
          :rules="inFormRules"
          label-width="100px"
        >
          <el-form-item label="物品" prop="goods_id">
            <el-select
              v-model="inFormData.goods_id"
              placeholder="请选择物品"
              style="width: 100%"
              @change="handleInGoodsChange"
            >
              <el-option
                v-for="goods in allGoodsList"
                :key="goods.goods_id"
                :label="`${goods.goods_name} (${goods.goods_code})`"
                :value="goods.goods_id"
              />
            </el-select>
          </el-form-item>
          
          <el-form-item label="入库数量" prop="in_quantity">
            <el-input
              v-model.number="inFormData.in_quantity"
              type="number"
              :min="1"
              :step="1"
              placeholder="请输入入库数量"
              @change="calculateInTotalAmount"
            />
          </el-form-item>
          
          <el-form-item label="入库单价" prop="unit_price">
            <el-input
              v-model.number="inFormData.unit_price"
              type="number"
              :min="0"
              :step="0.01"
              placeholder="请输入入库单价"
              @change="calculateInTotalAmount"
            />
          </el-form-item>
          
          <el-form-item label="总金额" prop="total_amount">
            <el-input
              v-model.number="inFormData.total_amount"
              type="number"
              :min="0"
              :step="0.01"
              placeholder="总金额"
              disabled
            />
          </el-form-item>
          
          <el-form-item label="批次号" prop="batch_no">
            <el-input v-model="inFormData.batch_no" placeholder="请输入批次号" />
          </el-form-item>
          
          <el-form-item label="供应商" prop="supplier">
            <el-input v-model="inFormData.supplier" placeholder="请输入供应商" />
          </el-form-item>
          
          <el-form-item label="备注" prop="remark">
            <el-input
              v-model="inFormData.remark"
              type="textarea"
              :rows="3"
              placeholder="请输入备注"
            />
          </el-form-item>
        </el-form>
        
        <template #footer>
          <el-button @click="inDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleInSubmit" :loading="inSubmitting">确定</el-button>
        </template>
      </el-dialog>
      
      <!-- 出库对话框 -->
      <el-dialog
        v-model="outDialogVisible"
        title="物品出库"
        width="600px"
        @close="handleOutDialogClose"
      >
        <el-form
          ref="outFormRef"
          :model="outFormData"
          :rules="outFormRules"
          label-width="100px"
        >
          <el-form-item label="物品" prop="goods_id">
            <el-select
              v-model="outFormData.goods_id"
              placeholder="请选择物品"
              style="width: 100%"
              @change="handleOutGoodsChange"
            >
              <el-option
                v-for="item in stockList"
                :key="item.goods_id"
                :label="`${item.goods_name} - 库存: ${item.current_stock || 0}`"
                :value="item.goods_id"
                :disabled="item.current_stock <= 0"
              />
            </el-select>
          </el-form-item>
          
          <el-form-item label="当前库存">
            <el-input v-model="outCurrentStock" disabled />
          </el-form-item>
          
          <el-form-item label="出库数量" prop="out_quantity">
            <el-input
              v-model.number="outFormData.out_quantity"
              type="number"
              :min="1"
              :max="outCurrentStock"
              :step="1"
              placeholder="请输入出库数量"
              @change="calculateOutTotalAmount"
            />
          </el-form-item>
          
          <el-form-item label="出库单价" prop="unit_price">
            <el-input
              v-model.number="outFormData.unit_price"
              type="number"
              :min="0"
              :step="0.01"
              placeholder="请输入出库单价"
              @change="calculateOutTotalAmount"
            />
          </el-form-item>
          
          <el-form-item label="总金额" prop="total_amount">
            <el-input
              v-model.number="outFormData.total_amount"
              type="number"
              :min="0"
              :step="0.01"
              placeholder="总金额"
              disabled
            />
          </el-form-item>
          
          <el-form-item label="接收人" prop="receiver">
            <el-input v-model="outFormData.receiver" placeholder="请输入接收人" />
          </el-form-item>
          
          <el-form-item label="接收部门" prop="department">
            <el-input v-model="outFormData.department" placeholder="请输入接收部门" />
          </el-form-item>
          
          <el-form-item label="用途说明" prop="purpose">
            <el-input v-model="outFormData.purpose" placeholder="请输入用途说明" />
          </el-form-item>
          
          <el-form-item label="备注" prop="remark">
            <el-input
              v-model="outFormData.remark"
              type="textarea"
              :rows="3"
              placeholder="请输入备注"
            />
          </el-form-item>
        </el-form>
        
        <template #footer>
          <el-button @click="outDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleOutSubmit" :loading="outSubmitting">确定</el-button>
        </template>
      </el-dialog>
      
      <!-- 库存详情对话框 -->
      <StockDetailDialog
        v-model="detailVisible"
        :goods="selectedGoods"
      />
    </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import TableComponent from '@/components/common/TableComponent.vue'
import StockDetailDialog from '@/components/common/StockDetailDialog.vue'
import { getStockList, getGoodsList } from '@/api/goods'
import { createStockIn, createStockOut } from '@/api/stock'

// 用户存储
const userStore = useUserStore()

// 是否可以创建入库（仅管理员）
const canCreate = computed(() => {
  const userRole = userStore.user?.role
  return userRole === 'admin' || userRole === 'super_admin'
})

/**
 * 加载状态
 */
const loading = ref(false)

/**
 * 库存列表
 */
const stockList = ref([])

/**
 * 所有物品列表（用于入库选择）
 */
const allGoodsList = ref([])

/**
 * 搜索表单
 */
const searchForm = reactive({
  goods_name: ''
})

/**
 * 分页数据
 */
const pagination = reactive({
  page: 1,
  limit: 20,
  total: 0
})

/**
 * 入库对话框
 */
const inDialogVisible = ref(false)
const inSubmitting = ref(false)
const inFormRef = ref(null)
const inFormData = reactive({
  goods_id: null,
  in_quantity: 1,
  unit_price: 0,
  total_amount: 0,
  batch_no: '',
  supplier: '',
  remark: ''
})

const inFormRules = {
  goods_id: [{ required: true, message: '请选择物品', trigger: 'change' }],
  in_quantity: [{ required: true, message: '请输入入库数量', trigger: 'blur' }],
  unit_price: [{ required: true, message: '请输入入库单价', trigger: 'blur' }],
  total_amount: [{ required: true, message: '请输入总金额', trigger: 'blur' }]
}

/**
 * 出库对话框
 */
const outDialogVisible = ref(false)
const outSubmitting = ref(false)
const outFormRef = ref(null)
const outFormData = reactive({
  goods_id: null,
  out_quantity: 1,
  unit_price: 0,
  total_amount: 0,
  receiver: '',
  department: '',
  purpose: '',
  remark: ''
})

const outFormRules = {
  goods_id: [{ required: true, message: '请选择物品', trigger: 'change' }],
  out_quantity: [{ required: true, message: '请输入出库数量', trigger: 'blur' }],
  unit_price: [{ required: true, message: '请输入出库单价', trigger: 'blur' }],
  total_amount: [{ required: true, message: '请输入总金额', trigger: 'blur' }]
}

const outCurrentStock = ref(0)

/**
 * 库存详情对话框
 */
const detailVisible = ref(false)
const selectedGoods = ref({})

/**
 * 加载库存列表
 */
const loadStockList = async () => {
  try {
    loading.value = true
    const response = await getStockList({
      page: pagination.page,
      page_size: pagination.limit,
      goods_name: searchForm.goods_name || undefined
    })
    stockList.value = response.items
    pagination.total = response.total
  } catch (error) {
    ElMessage.error('加载库存列表失败')
  } finally {
    loading.value = false
  }
}

/**
 * 加载所有物品列表（用于入库选择）
 */
const loadAllGoodsList = async () => {
  try {
    const response = await getGoodsList({
      page: 1,
      page_size: 1000,
      status: 1  // 仅加载正常状态的物品
    })
    allGoodsList.value = response.items
  } catch (error) {
    ElMessage.error('加载物品列表失败')
  }
}

/**
 * 处理页码变化
 * 
 * @param {number} page - 页码
 */
const handlePageChange = (page) => {
  pagination.page = page
  loadStockList()
}

/**
 * 处理每页数量变化
 * 
 * @param {number} limit - 每页数量
 */
const handleSizeChange = (limit) => {
  pagination.limit = limit
  pagination.page = 1
  loadStockList()
}

/**
 * 处理重置
 */
const handleReset = () => {
  searchForm.goods_name = ''
  pagination.page = 1
  loadStockList()
}

/**
 * 处理入库
 */
const handleStockIn = () => {
  if (!canCreate.value) {
    ElMessage.warning('权限不足，仅管理员可创建入库记录')
    return
  }
  
  // 重置表单
  Object.assign(inFormData, {
    goods_id: null,
    in_quantity: 1,
    unit_price: 0,
    total_amount: 0,
    batch_no: '',
    supplier: '',
    remark: ''
  })
  
  inDialogVisible.value = true
}

/**
 * 处理物品变更（入库）
 */
const handleInGoodsChange = (goodsId) => {
  const goods = allGoodsList.value.find(goods => goods.goods_id === goodsId)
  if (goods) {
    inFormData.unit_price = goods.purchase_price || 0
    calculateInTotalAmount()
  }
}

/**
 * 计算入库总金额
 */
const calculateInTotalAmount = () => {
  inFormData.total_amount = inFormData.in_quantity * inFormData.unit_price
}

/**
 * 处理入库表单提交
 */
const handleInSubmit = async () => {
  try {
    await inFormRef.value.validate()
    inSubmitting.value = true
    
    await createStockIn(inFormData)
    
    ElMessage.success('入库成功')
    inDialogVisible.value = false
    loadStockList()
  } catch (error) {
    if (error.response?.data?.detail) {
      ElMessage.error(error.response.data.detail)
    } else if (error !== false) {
      ElMessage.error('入库失败')
    }
  } finally {
    inSubmitting.value = false
  }
}

/**
 * 处理入库对话框关闭
 */
const handleInDialogClose = () => {
  inFormRef.value?.resetFields()
}

/**
 * 处理出库
 */
const handleStockOut = () => {
  if (stockList.value.length === 0) {
    ElMessage.warning('暂无可用物品')
    return
  }
  
  // 重置表单
  outFormData.goods_id = null
  outFormData.out_quantity = 1
  outFormData.unit_price = 0
  outFormData.total_amount = 0
  outFormData.receiver = ''
  outFormData.department = ''
  outFormData.purpose = ''
  outFormData.remark = ''
  
  outCurrentStock.value = 0
  
  // 使用 nextTick 确保 DOM 更新后再显示对话框
  nextTick(() => {
    outDialogVisible.value = true
  })
}

/**
 * 处理物品变更（出库）
 */
const handleOutGoodsChange = (goodsId) => {
  const goods = stockList.value.find(item => item.goods_id === goodsId)
  if (goods) {
    outCurrentStock.value = goods.current_stock || 0
    outFormData.unit_price = goods.purchase_price || 0
    calculateOutTotalAmount()
  }
}

/**
 * 计算出库总金额
 */
const calculateOutTotalAmount = () => {
  outFormData.total_amount = outFormData.out_quantity * outFormData.unit_price
}

/**
 * 处理出库表单提交
 */
const handleOutSubmit = async () => {
  try {
    await outFormRef.value.validate()
    outSubmitting.value = true
    
    await createStockOut(outFormData)
    
    ElMessage.success('出库成功')
    outDialogVisible.value = false
    loadStockList()
  } catch (error) {
    if (error.response?.data?.detail) {
      ElMessage.error(error.response.data.detail)
    } else if (error !== false) {
      ElMessage.error('出库失败')
    }
  } finally {
    outSubmitting.value = false
  }
}

/**
 * 处理出库对话框关闭
 */
const handleOutDialogClose = () => {
  outFormRef.value?.resetFields()
}

/**
 * 处理详情
 *
 * @param {Object} row - 行数据
 */
const handleDetail = (row) => {
  selectedGoods.value = row
  detailVisible.value = true
}

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
 * 组件挂载时加载数据
 */
onMounted(() => {
  loadStockList()
  loadAllGoodsList()
})
</script>

<style scoped>
.stock-container {
  padding: 20px;
}

.toolbar-card {
  margin-bottom: 20px;
}

.table-card {
  height: calc(100vh - 250px);
}
.low-stock-warning {
  color: #f56c6c;
  font-weight: bold;
}
</style>
