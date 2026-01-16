/**
 * CampusAssetManager/frontend/src/views/StockInView.vue
 * 入库管理页面
 * 
 * 功能说明：
 * - 入库记录列表展示（支持分页、搜索）
 * - 入库搜索和筛选
 * - 创建入库记录
 * - 查看入库详情
 * 
 * 设计原则：
 * - 声明式：使用Vue Composition API
 * - 组件化：使用Element Plus组件
 * - 响应式：使用ref和reactive管理状态
 * 
 * 作者：CampusAssetManager开发团队
 * 日期：2026-01-07
 */

<template>
  <div class="stock-in-container">
    <!-- 工具栏 -->
    <el-card class="toolbar-card">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="搜索关键词">
          <el-input
            v-model="searchForm.search"
            placeholder="入库单号/物品名称"
            clearable
            style="width: 200px"
          />
        </el-form-item>
        
        <el-form-item label="物品">
          <el-select
            v-model="searchForm.goods_id"
            placeholder="请选择物品"
            clearable
            style="width: 200px"
          >
            <el-option
              v-for="goods in goodsList"
              :key="goods.goods_id"
              :label="goods.goods_name"
              :value="goods.goods_id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="开始日期">
          <el-date-picker
            v-model="searchForm.start_date"
            type="date"
            placeholder="选择开始日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            clearable
          />
        </el-form-item>
        
        <el-form-item label="结束日期">
          <el-date-picker
            v-model="searchForm.end_date"
            type="date"
            placeholder="选择结束日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            clearable
          />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="loadStockInList">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
      
      <el-button v-if="canCreate" type="primary" @click="handleAdd">入库</el-button>
    </el-card>
    
    <!-- 入库记录列表 -->
    <el-card class="table-card">
      <TableComponent
        :data="stockInList"
        :loading="loading"
        :show-selection="false"
        :page="pagination.page"
        :limit="pagination.limit"
        :total="pagination.total"
        @update:page="handlePageChange"
        @update:limit="handleSizeChange"
      >
        <template #columns>
          <el-table-column prop="in_id" label="ID" width="80" align="center" />
          <el-table-column prop="in_no" label="入库单号" width="160" />
          <el-table-column prop="goods_name" label="物品名称" min-width="150" />
          <el-table-column prop="goods_code" label="物品编码" width="120" />
          <el-table-column prop="in_quantity" label="入库数量" width="100" align="right" />
          <el-table-column prop="unit_price" label="单价" width="100" align="right">
            <template #default="{ row }">
              ¥{{ row.unit_price.toFixed(2) }}
            </template>
          </el-table-column>
          <el-table-column prop="total_amount" label="总金额" width="120" align="right">
            <template #default="{ row }">
              ¥{{ row.total_amount.toFixed(2) }}
            </template>
          </el-table-column>
          <el-table-column prop="batch_no" label="批次号" width="120" />
          <el-table-column prop="supplier" label="供应商" width="150" />
          <el-table-column prop="in_time" label="入库时间" width="160" align="center">
            <template #default="{ row }">
              {{ formatDate(row.in_time) }}
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
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      @close="handleDialogClose"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="物品" prop="goods_id">
          <el-select
            v-model="formData.goods_id"
            placeholder="请选择物品"
            style="width: 100%"
            @change="handleGoodsChange"
          >
            <el-option
              v-for="goods in goodsList"
              :key="goods.goods_id"
              :label="`${goods.goods_name} (${goods.goods_code})`"
              :value="goods.goods_id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="入库数量" prop="in_quantity">
          <el-input-number
            v-model="formData.in_quantity"
            :min="1"
            :step="1"
            style="width: 100%"
            @change="calculateTotalAmount"
          />
        </el-form-item>
        
        <el-form-item label="入库单价" prop="unit_price">
          <el-input-number
            v-model="formData.unit_price"
            :precision="2"
            :min="0"
            :step="0.01"
            style="width: 100%"
            @change="calculateTotalAmount"
          />
        </el-form-item>
        
        <el-form-item label="总金额" prop="total_amount">
          <el-input-number
            v-model="formData.total_amount"
            :precision="2"
            :min="0"
            :step="0.01"
            style="width: 100%"
            disabled
          />
        </el-form-item>
        
        <el-form-item label="批次号" prop="batch_no">
          <el-input v-model="formData.batch_no" placeholder="请输入批次号" />
        </el-form-item>
        
        <el-form-item label="供应商" prop="supplier">
          <el-input v-model="formData.supplier" placeholder="请输入供应商" />
        </el-form-item>
        
        <el-form-item label="备注" prop="remark">
          <el-input
            v-model="formData.remark"
            type="textarea"
            :rows="3"
            placeholder="请输入备注"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
    
    <!-- 详情对话框 -->
    <el-dialog
      v-model="detailVisible"
      title="入库详情"
      width="700px"
    >
      <el-descriptions :column="2" border>
        <el-descriptions-item label="入库单号">{{ detailData.in_no }}</el-descriptions-item>
        <el-descriptions-item label="入库时间">{{ formatDate(detailData.in_time) }}</el-descriptions-item>
        <el-descriptions-item label="物品名称">{{ detailData.goods_name }}</el-descriptions-item>
        <el-descriptions-item label="物品编码">{{ detailData.goods_code }}</el-descriptions-item>
        <el-descriptions-item label="入库数量">{{ detailData.in_quantity }}</el-descriptions-item>
        <el-descriptions-item label="单价">¥{{ detailData.unit_price?.toFixed(2) }}</el-descriptions-item>
        <el-descriptions-item label="总金额">¥{{ detailData.total_amount?.toFixed(2) }}</el-descriptions-item>
        <el-descriptions-item label="批次号">{{ detailData.batch_no || '-' }}</el-descriptions-item>
        <el-descriptions-item label="供应商" :span="2">{{ detailData.supplier || '-' }}</el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">{{ detailData.remark || '-' }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import TableComponent from '@/components/common/TableComponent.vue'
import { createStockIn, getStockInList } from '@/api/stock'
import { getGoodsList } from '@/api/goods'

// 用户存储
const userStore = useUserStore()

// 是否可以创建入库（仅管理员）
const canCreate = computed(() => {
  const userRole = userStore.user?.role
  return userRole === 'admin' || userRole === 'super_admin'
})

// 加载状态
const loading = ref(false)

// 入库记录列表
const stockInList = ref([])
const goodsList = ref([])

// 搜索表单
const searchForm = reactive({
  search: '',
  goods_id: null,
  start_date: '',
  end_date: ''
})

// 分页信息
const pagination = reactive({
  page: 1,
  limit: 20,
  total: 0
})

// 对话框显示状态
const dialogVisible = ref(false)
const detailVisible = ref(false)

// 对话框标题
const dialogTitle = computed(() => '入库')

// 表单数据
const formData = reactive({
  goods_id: null,
  in_quantity: 1,
  unit_price: 0,
  total_amount: 0,
  batch_no: '',
  supplier: '',
  remark: ''
})

// 表单引用
const formRef = ref(null)

// 提交状态
const submitting = ref(false)

// 详情数据
const detailData = ref({})

// 表单验证规则
const formRules = {
  goods_id: [{ required: true, message: '请选择物品', trigger: 'change' }],
  in_quantity: [{ required: true, message: '请输入入库数量', trigger: 'blur' }],
  unit_price: [{ required: true, message: '请输入入库单价', trigger: 'blur' }]
}

// 格式化日期
const formatDate = (date) => {
  if (!date) return '-'
  return new Date(date).toLocaleString('zh-CN')
}

// 加载入库记录列表
const loadStockInList = async () => {
  try {
    loading.value = true
    const params = {
      page: pagination.page,
      page_size: pagination.limit,
      ...searchForm
    }
    
    const data = await getStockInList(params)
    
    stockInList.value = data.items.map(item => ({
      ...item,
      goods_name: item.goods?.goods_name || '',
      goods_code: item.goods?.goods_code || ''
    }))
    pagination.total = data.total
  } catch (error) {
    console.error('加载入库记录失败:', error)
    ElMessage.error(error.message || '加载入库记录失败')
  } finally {
    loading.value = false
  }
}

// 加载物品列表
const loadGoodsList = async () => {
  try {
    const data = await getGoodsList({ page: 1, page_size: 20 })
    goodsList.value = data.items
  } catch (error) {
    console.error('加载物品列表失败:', error)
    ElMessage.error(error.message || '加载物品列表失败')
  }
}

// 搜索重置
const handleReset = () => {
  searchForm.search = ''
  searchForm.goods_id = null
  searchForm.start_date = ''
  searchForm.end_date = ''
  pagination.page = 1
  loadStockInList()
}

// 页码变化
const handlePageChange = (page) => {
  pagination.page = page
  loadStockInList()
}

// 每页数量变化
const handleSizeChange = (size) => {
  pagination.limit = size
  pagination.page = 1
  loadStockInList()
}

// 处理入库按钮点击
const handleAdd = () => {
  formData.goods_id = null
  formData.in_quantity = 1
  formData.unit_price = 0
  formData.total_amount = 0
  formData.batch_no = ''
  formData.supplier = ''
  formData.remark = ''
  dialogVisible.value = true
}

// 处理物品变化
const handleGoodsChange = (goodsId) => {
  const goods = goodsList.value.find(g => g.goods_id === goodsId)
  if (goods) {
    formData.unit_price = goods.purchase_price
    calculateTotalAmount()
  }
}

// 计算总金额
const calculateTotalAmount = () => {
  formData.total_amount = formData.in_quantity * formData.unit_price
}

// 提交入库
const handleSubmit = async () => {
  try {
    // 验证表单
    await formRef.value.validate()
    
    submitting.value = true
    const data = await createStockIn(formData)
    
    if (data) {
      ElMessage.success('入库成功')
      dialogVisible.value = false
      loadStockInList()
    }
  } catch (error) {
    if (error !== false) {
      ElMessage.error(error.message || '入库失败')
    }
  } finally {
    submitting.value = false
  }
}

// 查看详情
const handleDetail = (row) => {
  detailData.value = {
    ...row,
    goods_name: row.goods?.goods_name || '',
    goods_code: row.goods?.goods_code || ''
  }
  detailVisible.value = true
}

// 对话框关闭处理
const handleDialogClose = () => {
  formRef.value?.resetFields()
}

// 组件挂载时加载数据
onMounted(() => {
  loadStockInList()
  loadGoodsList()
})
</script>

<style scoped>
.stock-in-container {
  padding: 20px;
}

.toolbar-card {
  margin-bottom: 20px;
}

.table-card {
  margin-bottom: 20px;
}
</style>