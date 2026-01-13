/**
 * CampusAssetManager/frontend/src/views/CheckView.vue
 * 盘点管理页面
 * 
 * 功能说明：
 * - 盘点记录列表展示
 * - 创建盘点单
 * - 提交盘点结果
 * - 查看盘点详情
 * 
 * 作者：CampusAssetManager开发团队
 * 日期：2026-01-13
 */

<template>
  <div class="check-container">
    <!-- 工具栏 -->
    <el-card class="toolbar-card">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索盘点单号、物品名称"
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
            v-model="checkResultFilter"
            placeholder="盘点结果"
            clearable
            @change="handleSearch"
          >
            <el-option label="正常" value="normal" />
            <el-option label="盘盈" value="over" />
            <el-option label="盘亏" value="short" />
          </el-select>
        </el-col>
        <el-col :span="4">
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
        <el-col :span="10" style="text-align: right;">
          <el-button type="primary" @click="handleCreateCheck">创建盘点单</el-button>
        </el-col>
      </el-row>
    </el-card>
    
    <!-- 盘点记录列表 -->
    <el-card class="table-card">
      <TableComponent
        :data="checkList"
        :loading="loading"
        :show-selection="false"
        :page="pagination.page"
        :limit="pagination.page_size"
        :total="pagination.total"
        @update:page="handlePageChange"
        @update:limit="handleSizeChange"
      >
        <template #columns>
          <el-table-column prop="check_no" label="盘点单号" min-width="150" />
          <el-table-column prop="goods_name" label="物品名称" min-width="150" />
          <el-table-column prop="book_stock" label="账面库存" width="100" align="center" />
          <el-table-column prop="actual_stock" label="实际库存" width="100" align="center" />
          <el-table-column prop="diff_quantity" label="差异" width="100" align="center">
            <template #default="{ row }">
              <span :class="getDiffClass(row.diff_quantity)">
                {{ row.diff_quantity > 0 ? '+' + row.diff_quantity : row.diff_quantity }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="check_result" label="盘点结果" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="getCheckResultType(row.check_result)">
                {{ getCheckResultText(row.check_result) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="checker_name" label="盘点人" width="100" />
          <el-table-column prop="check_time" label="盘点时间" width="180">
            <template #default="{ row }">
              {{ formatDate(row.check_time) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="150" align="center">
            <template #default="{ row }">
              <el-button type="primary" link @click="handleDetail(row)">详情</el-button>
            </template>
          </el-table-column>
        </template>
      </TableComponent>
    </el-card>
    
    <!-- 创建盘点对话框 -->
    <el-dialog
      v-model="dialogVisible"
      title="创建盘点单"
      width="600px"
      @close="resetForm"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="选择物品" prop="goods_id">
          <el-select
            v-model="form.goods_id"
            placeholder="请选择物品"
            filterable
            @change="handleGoodsChange"
          >
            <el-option
              v-for="item in goodsList"
              :key="item.goods_id"
              :label="`${item.goods_code} - ${item.goods_name}`"
              :value="item.goods_id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="账面库存" prop="book_stock">
          <el-input v-model="form.book_stock" disabled />
        </el-form-item>
        <el-form-item label="实际库存" prop="actual_stock">
          <el-input-number v-model="form.actual_stock" :min="0" style="width: 100%;" />
        </el-form-item>
        <el-form-item label="差异" prop="diff_quantity">
          <el-input v-model="form.diff_quantity" disabled>
            <template #append>自动计算</template>
          </el-input>
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input
            v-model="form.remark"
            type="textarea"
            :rows="3"
            placeholder="请输入备注说明"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm">提交</el-button>
      </template>
    </el-dialog>
    
    <!-- 盘点详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="盘点详情"
      width="700px"
    >
      <el-descriptions :column="2" border>
        <el-descriptions-item label="盘点单号">{{ currentDetail.check_no }}</el-descriptions-item>
        <el-descriptions-item label="盘点时间">{{ currentDetail.check_time }}</el-descriptions-item>
        <el-descriptions-item label="物品名称">{{ currentDetail.goods_name }}</el-descriptions-item>
        <el-descriptions-item label="物品编码">{{ currentDetail.goods_code }}</el-descriptions-item>
        <el-descriptions-item label="账面库存">{{ currentDetail.book_stock }}</el-descriptions-item>
        <el-descriptions-item label="实际库存">{{ currentDetail.actual_stock }}</el-descriptions-item>
        <el-descriptions-item label="差异">
          <span :class="getDiffClass(currentDetail.diff_quantity)">
            {{ currentDetail.diff_quantity > 0 ? '+' + currentDetail.diff_quantity : currentDetail.diff_quantity }}
          </span>
        </el-descriptions-item>
        <el-descriptions-item label="盘点结果">
          <el-tag :type="getCheckResultType(currentDetail.check_result)">
            {{ getCheckResultText(currentDetail.check_result) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="盘点人">{{ currentDetail.checker_name }}</el-descriptions-item>
        <el-descriptions-item label="备注">{{ currentDetail.remark || '-' }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import TableComponent from '@/components/common/TableComponent.vue'
import {
  getStockCheckList,
  createStockCheck,
  getStockCheckDetail,
  getStockListEnhanced
} from '@/api/stock'

/**
 * 加载状态
 */
const loading = ref(false)

/**
 * 盘点记录列表
 */
const checkList = ref([])

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
 * 盘点结果筛选
 */
const checkResultFilter = ref('')

/**
 * 日期范围
 */
const dateRange = ref([])

/**
 * 对话框显示状态
 */
const dialogVisible = ref(false)
const detailDialogVisible = ref(false)

/**
 * 表单数据
 */
const form = reactive({
  goods_id: null,
  book_stock: 0,
  actual_stock: 0,
  diff_quantity: 0,
  remark: ''
})

/**
 * 表单引用
 */
const formRef = ref(null)

/**
 * 物品列表
 */
const goodsList = ref([])

/**
 * 当前详情
 */
const currentDetail = ref({})

/**
 * 表单验证规则
 */
const rules = {
  goods_id: [
    { required: true, message: '请选择物品', trigger: 'change' }
  ],
  actual_stock: [
    { required: true, message: '请输入实际库存', trigger: 'blur' }
  ]
}

/**
 * 获取差异样式类
 * 
 * @param {number} diff - 差异数量
 * @returns {string} 样式类名
 */
const getDiffClass = (diff) => {
  if (diff > 0) {
    return 'diff-positive'
  } else if (diff < 0) {
    return 'diff-negative'
  }
  return 'diff-normal'
}

/**
 * 获取盘点结果类型
 * 
 * @param {string} result - 盘点结果
 * @returns {string} 类型
 */
const getCheckResultType = (result) => {
  const typeMap = {
    'normal': 'success',
    'over': 'warning',
    'short': 'danger'
  }
  return typeMap[result] || 'info'
}

/**
 * 获取盘点结果文本
 * 
 * @param {string} result - 盘点结果
 * @returns {string} 文本
 */
const getCheckResultText = (result) => {
  const textMap = {
    'normal': '正常',
    'over': '盘盈',
    'short': '盘亏'
  }
  return textMap[result] || '未知'
}

/**
 * 加载盘点记录列表
 */
const loadCheckList = async () => {
  try {
    loading.value = true
    const params = {
      page: pagination.page,
      page_size: pagination.page_size
    }
    
    if (searchKeyword.value) {
      params.search = searchKeyword.value
    }
    if (checkResultFilter.value) {
      params.check_result = checkResultFilter.value
    }
    if (dateRange.value && dateRange.value.length === 2) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }
    
    // 响应拦截器已自动处理，直接返回 data
    const response = await getStockCheckList(params)
    checkList.value = response.items
    pagination.total = response.total
  } catch (error) {
    ElMessage.error('加载盘点记录列表失败：' + error.message)
  } finally {
    loading.value = false
  }
}

/**
 * 加载物品列表
 */
const loadGoodsList = async () => {
  try {
    // 响应拦截器已自动处理，直接返回 data
    // 使用 getStockListEnhanced 获取包含库存信息的物品列表
    // 分批加载所有物品，避免一次加载过多数据导致 500 错误
    const allItems = []
    let page = 1
    const pageSize = 100  // 每次加载 100 条
    
    while (true) {
      const response = await getStockListEnhanced({ page, page_size: pageSize })
      allItems.push(...response.items)
      
      // 如果返回的数据量少于 pageSize，说明已加载完毕
      if (response.items.length < pageSize) {
        break
      }
      
      page++
    }
    
    // 将库存列表转换为盘点表单需要的格式
    goodsList.value = allItems.map(item => ({
      goods_id: item.goods_id,
      goods_name: item.goods_name,
      goods_code: item.goods_code,
      current_stock: item.current_stock
    }))
  } catch (error) {
    ElMessage.error('加载物品列表失败：' + error.message)
  }
}

/**
 * 处理搜索
 */
const handleSearch = () => {
  pagination.page = 1
  loadCheckList()
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
 * @param {number} size - 每页数量
 */
const handleSizeChange = (size) => {
  pagination.page_size = size
  pagination.page = 1
  loadCheckList()
}

/**
 * 处理创建盘点单
 */
const handleCreateCheck = () => {
  dialogVisible.value = true
  if (goodsList.value.length === 0) {
    loadGoodsList()
  }
}

/**
 * 处理物品变化
 */
const handleGoodsChange = (goodsId) => {
  const goods = goodsList.value.find(item => item.goods_id === goodsId)
  if (goods) {
    form.book_stock = goods.current_stock || 0
  }
  calculateDiff()
}

/**
 * 计算差异
 */
const calculateDiff = () => {
  form.diff_quantity = form.actual_stock - form.book_stock
}

/**
 * 监听实际库存变化
 */
watch(() => form.actual_stock, () => {
  calculateDiff()
})

/**
 * 提交表单
 */
const submitForm = async () => {
  try {
    await formRef.value.validate()
    
    const submitData = {
      goods_id: form.goods_id,
      actual_stock: form.actual_stock,
      remark: form.remark
    }
    
    // 响应拦截器已自动处理错误提示，这里不需要检查 code
    await createStockCheck(submitData)
    ElMessage.success('盘点成功')
    dialogVisible.value = false
    loadCheckList()
  } catch (error) {
    if (error !== 'cancel') {
      // 错误已被拦截器处理并显示，这里仅记录或做其他处理
      console.error('提交盘点失败：', error)
    }
  }
}

/**
 * 重置表单
 */
const resetForm = () => {
  form.goods_id = null
  form.book_stock = 0
  form.actual_stock = 0
  form.diff_quantity = 0
  form.remark = ''
  formRef.value?.resetFields()
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
const handleDetail = async (row) => {
  try {
    // 响应拦截器已自动处理，直接返回 data
    const response = await getStockCheckDetail(row.check_id)
    currentDetail.value = response
    detailDialogVisible.value = true
  } catch (error) {
    ElMessage.error('获取盘点详情失败：' + error.message)
  }
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

.diff-positive {
  color: #E6A23C;
  font-weight: bold;
}

.diff-negative {
  color: #F56C6C;
  font-weight: bold;
}

.diff-normal {
  color: #67C23A;
}
</style>