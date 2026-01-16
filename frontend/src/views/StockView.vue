
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
  <div class="page-container">
    <div class="glass-toolbar">
      <div class="toolbar-left">
        <el-input
          v-model="searchForm.goods_name"
          placeholder="搜索物品名称、编码..."
          :prefix-icon="Search"
          clearable
          class="search-input"
          @clear="handleSearch"
          @keyup.enter="handleSearch"
        />
        
        <el-select
          v-model="searchForm.stock_status"
          placeholder="库存状态"
          clearable
          class="filter-select"
          @change="handleSearch"
        >
          <el-option label="低库存" value="low" />
          <el-option label="库存过高" value="over" />
          <el-option label="正常" value="normal" />
        </el-select>
      </div>
      
      <div class="toolbar-right">
        <el-button @click="handleShowLowStock" v-if="canAdjustStock">
          <el-icon><Warning /></el-icon>
          低库存
        </el-button>
        <el-button @click="handleReset">重置</el-button>
        <el-button type="primary" @click="handleBatchThreshold" v-if="canAdjustStock">
          <el-icon><Setting /></el-icon>
          批量阈值
        </el-button>
        <el-button type="success" @click="handleStockIn" v-if="canCreate">
          <el-icon><Plus /></el-icon>
          入库
        </el-button>
        <el-button type="warning" @click="handleStockOut">
          <el-icon><Minüs /></el-icon>
          出库
        </el-button>
        <el-button type="danger" @click="handleStockAdjust" v-if="canAdjustStock">
          <el-icon><Setting /></el-icon>
          调整
        </el-button>
      </div>
    </div>
    
    <div class="content-card">
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
            <el-table-column prop="goods_id" label="物品ID" width="70" align="center" fixed="left">
              <template #default="{ row }">
                <span class="num-font secondary-num">{{ row.goods_id }}</span>
              </template>
            </el-table-column>

            <el-table-column prop="goods_name" label="物品名称" min-width="150">
              <template #default="{ row }">
                <span class="text-main fw-600">{{ row.goods_name }}</span>
              </template>
            </el-table-column>

            <el-table-column prop="category_name" label="分类名称" width="120" />

            <el-table-column prop="current_stock" label="当前库存" width="110" align="right">
              <template #default="{ row }">
                <span class="num-font" :class="getStockClass(row)">
                  {{ row.current_stock || 0 }}
                </span>
              </template>
            </el-table-column>

            <el-table-column prop="min_stock" label="最小库存" width="90" align="center" />

            <el-table-column prop="max_stock" label="最大库存" width="90" align="center" />

            <el-table-column prop="stock_status" label="库存状态" width="110" align="center">
              <template #default="{ row }">
                <div class="status-pill" :class="getStockStatusClass(row)">
                  <span class="dot"></span>
                  <span>{{ getStockStatusLabel(row) }}</span>
                </div>
              </template>
            </el-table-column>

            <el-table-column prop="status" label="物品状态" width="110" align="center">
              <template #default="{ row }">
                <div class="status-pill" :class="getStatusClass(row.status)">
                  <span class="dot"></span>
                  <span>{{ getStatusText(row.status) }}</span>
                </div>
              </template>
            </el-table-column>

            <el-table-column prop="update_time" label="更新时间" width="160" align="center">
              <template #default="{ row }">
                {{ formatDate(row.update_time) }}
              </template>
            </el-table-column>

            <el-table-column label="操作" width="160" align="center" fixed="right">
              <template #default="{ row }">
                <el-button link class="edit-btn" @click="handleDetail(row)">详情</el-button>
                <el-divider direction="vertical" />
                <el-button type="danger" link @click="handleThreshold(row)" v-if="canAdjustStock">设置阈值</el-button>
              </template>
            </el-table-column>
          </template>
        </TableComponent>
      </div>
      
      <!-- 入库对话框 -->
      <el-dialog
        v-model="inDialogVisible"
        title="物品入库"
        width="600px"
        class="custom-dialog"
        @close="handleInDialogClose"
      >
        <el-form
          ref="inFormRef"
          :model="inFormData"
          :rules="inFormRules"
          label-width="100px"
          class="modern-form"
        >
          <el-form-item label="物品" prop="goods_id">
            <el-select
              v-model="inFormData.goods_id"
              placeholder="请选择物品"
              style="width: 100%"
              @change="handleInGoodsChange"
            >
              <el-option
                v-for="item in stockList"
                :key="item.goods_id"
                :label="`${item.goods_name} (${item.goods_code}) - 库存: ${item.current_stock || 0}`"
                :value="item.goods_id"
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
            <div class="dialog-footer">
              <el-button @click="inDialogVisible = false">取消</el-button>
              <el-button type="primary" @click="handleInSubmit" :loading="inSubmitting">确定</el-button>
            </div>
          </template>
        </el-dialog>
        
        <!-- 出库对话框 -->
        <el-dialog
          v-model="outDialogVisible"
          title="物品出库"
          width="600px"
          class="custom-dialog"
          @close="handleOutDialogClose"
        >
          <el-form
            ref="outFormRef"
            :model="outFormData"
            :rules="outFormRules"
            label-width="100px"
            class="modern-form"
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
            <div class="dialog-footer">
              <el-button @click="outDialogVisible = false">取消</el-button>
              <el-button type="primary" @click="handleOutSubmit" :loading="outSubmitting">确定</el-button>
            </div>
          </template>
        </el-dialog>
        
        <!-- 库存调整对话框 -->
        <el-dialog
          v-model="adjustDialogVisible"
          title="库存调整"
          width="600px"
          class="custom-dialog"
          @close="handleAdjustDialogClose"
        >
        <el-alert
          title="警告"
          type="warning"
          :closable="false"
          style="margin-bottom: 20px;"
        >
          此操作将直接修改库存数量，请谨慎操作！此功能仅限超级管理员使用。
        </el-alert>
        <el-form
          ref="adjustFormRef"
          :model="adjustFormData"
          :rules="adjustFormRules"
          label-width="100px"
        >
          <el-form-item label="物品" prop="goods_id">
            <el-select
              v-model="adjustFormData.goods_id"
              placeholder="请选择物品"
              style="width: 100%"
              @change="handleAdjustGoodsChange"
            >
              <el-option
                v-for="item in stockList"
                :key="item.goods_id"
                :label="`${item.goods_name} - 当前库存: ${item.current_stock || 0}`"
                :value="item.goods_id"
              />
            </el-select>
          </el-form-item>
          
          <el-form-item label="当前库存">
            <el-input v-model="adjustCurrentStock" disabled />
          </el-form-item>
          
          <el-form-item label="调整数量" prop="adjust_quantity">
            <el-input-number
              v-model="adjustFormData.adjust_quantity"
              :step="1"
              placeholder="正数为增加，负数为减少"
              style="width: 100%"
            />
            <div style="font-size: 12px; color: #909399; margin-top: 5px;">
              正数为增加库存，负数为减少库存
            </div>
          </el-form-item>
          
          <el-form-item label="调整后库存">
            <el-input v-model="adjustAfterStock" disabled>
              <template #append>自动计算</template>
            </el-input>
          </el-form-item>
          
          <el-form-item label="调整原因" prop="adjust_reason">
            <el-input
              v-model="adjustFormData.adjust_reason"
              type="textarea"
              :rows="3"
              placeholder="请详细说明调整原因，此项为必填项"
            />
          </el-form-item>
        </el-form>
          
          <template #footer>
            <div class="dialog-footer">
              <el-button @click="adjustDialogVisible = false">取消</el-button>
              <el-button type="danger" @click="handleAdjustSubmit" :loading="adjustSubmitting">确定调整</el-button>
            </div>
          </template>
        </el-dialog>
      
      <!-- 单个物品阈值设置对话框 -->
      <el-dialog
        v-model="thresholdDialogVisible"
        title="设置库存阈值"
        width="500px"
        class="custom-dialog"
        @close="handleThresholdDialogClose"
      >
        <el-form
          ref="thresholdFormRef"
          :model="thresholdFormData"
          :rules="thresholdFormRules"
          label-width="100px"
          class="modern-form"
        >
        <el-form-item label="物品名称">
          <el-input v-model="thresholdFormData.goods_name" disabled />
        </el-form-item>
        
        <el-form-item label="当前库存">
          <el-input v-model="thresholdFormData.current_stock" disabled />
        </el-form-item>
        
        <el-form-item label="最小库存" prop="min_stock">
          <el-input-number
            v-model="thresholdFormData.min_stock"
            :min="0"
            :step="1"
            style="width: 100%"
          />
          <div style="font-size: 12px; color: #909399; margin-top: 5px;">
            低于此值时显示低库存预警
          </div>
        </el-form-item>
        
        <el-form-item label="最大库存" prop="max_stock">
          <el-input-number
            v-model="thresholdFormData.max_stock"
            :min="0"
            :step="1"
            placeholder="可选，不设置则不预警"
            style="width: 100%"
          />
          <div style="font-size: 12px; color: #909399; margin-top: 5px;">
            高于此值时显示库存过高预警
          </div>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="thresholdDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleThresholdSubmit" :loading="thresholdSubmitting">确定</el-button>
        </div>
      </template>
    </el-dialog>
    
    <!-- 批量阈值设置对话框 -->
    <el-dialog
      v-model="batchThresholdDialogVisible"
      title="批量设置库存阈值"
      width="500px"
      class="custom-dialog"
      @close="handleBatchThresholdDialogClose"
    >
      <el-alert
        title="提示"
        type="info"
        :closable="false"
        style="margin-bottom: 20px;"
      >
        将为所有物品设置统一的库存阈值。如需为特定物品设置不同阈值，请在列表中单独设置。
      </el-alert>
      <el-form
        ref="batchThresholdFormRef"
        :model="batchThresholdFormData"
        :rules="batchThresholdFormRules"
        label-width="120px"
      >
        <el-form-item label="最小库存" prop="min_stock">
          <el-input-number
            v-model="batchThresholdFormData.min_stock"
            :min="0"
            :step="1"
            style="width: 100%"
          />
          <div style="font-size: 12px; color: #909399; margin-top: 5px;">
            低于此值时显示低库存预警
          </div>
        </el-form-item>
        
        <el-form-item label="最大库存" prop="max_stock">
          <el-input-number
            v-model="batchThresholdFormData.max_stock"
            :min="0"
            :step="1"
            placeholder="可选，如留空则不设置最大库存"
            style="width: 100%"
          />
          <div style="font-size: 12px; color: #909399; margin-top: 5px;">
            高于此值时显示库存过高预警
          </div>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="batchThresholdDialogVisible = false">取消</el-button>
          <el-button type="danger" @click="handleBatchThresholdSubmit" :loading="batchThresholdSubmitting">
            批量应用
          </el-button>
        </div>
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
/**
 * 库存管理页面逻辑
 *
 * 导入模块：
 * - Vue Composition API：ref, reactive, computed, onMounted, nextTick, watch
 * - Element Plus 组件和消息提示
 * - Element Plus 图标组件
 * - 表格组件
 * - 库存管理 API
 * - 用户状态管理 Store
 */
import { ref, reactive, computed, onMounted, nextTick, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Warning, Setting, Plus, Minus } from '@element-plus/icons-vue'
import TableComponent from '@/components/common/TableComponent.vue'
import StockDetailDialog from '@/components/common/StockDetailDialog.vue'
import { useUserStore } from '@/stores/user'
import { getStockList, getGoodsList } from '@/api/goods'
import { createStockIn, createStockOut, adjustStock, getStockListEnhanced, updateStockThreshold, batchUpdateStockThresholds } from '@/api/stock'
import { getConfigs } from '@/api'

// 用户存储
const userStore = useUserStore()

/**
 * 系统配置
 */
const defaultMinStock = ref(10)      // 默认最小库存
const defaultMaxStock = ref(1000)    // 默认最大库存

// 是否可以创建入库（仅管理员）
const canCreate = computed(() => {
  const userRole = userStore.user?.role
  return userRole === 'admin' || userRole === 'super_admin'
})

// 是否可以调整库存（仅超级管理员）
const canAdjustStock = computed(() => {
  const userRole = userStore.user?.role
  return userRole === 'super_admin'
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
  goods_name: '',
  stock_status: ''
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
 * 库存调整对话框
 */
const adjustDialogVisible = ref(false)
const adjustSubmitting = ref(false)

/**
 * 阈值配置对话框
 */
const thresholdDialogVisible = ref(false)
const thresholdSubmitting = ref(false)
const thresholdFormRef = ref(null)
const thresholdFormData = reactive({
  goods_id: null,
  goods_name: '',
  current_stock: 0,
  min_stock: 10,
  max_stock: null
})

const thresholdFormRules = {
  min_stock: [{ required: true, message: '请输入最小库存', trigger: 'blur' }]
}

/**
 * 批量阈值配置对话框
 */
const batchThresholdDialogVisible = ref(false)
const batchThresholdSubmitting = ref(false)
const batchThresholdFormRef = ref(null)
const batchThresholdFormData = reactive({
  min_stock: 10,
  max_stock: null
})

const batchThresholdFormRules = {
  min_stock: [{ required: true, message: '请输入最小库存', trigger: 'blur' }]
}
const adjustFormRef = ref(null)
const adjustFormData = reactive({
  goods_id: null,
  adjust_quantity: 0,
  adjust_reason: ''
})

const adjustFormRules = {
  goods_id: [{ required: true, message: '请选择物品', trigger: 'change' }],
  adjust_quantity: [
    { required: true, message: '请输入调整数量', trigger: 'blur' },
    { type: 'number', message: '请输入有效的数字', trigger: 'blur' }
  ],
  adjust_reason: [
    { required: true, message: '请输入调整原因', trigger: 'blur' },
    { min: 5, message: '调整原因至少5个字符', trigger: 'blur' }
  ]
}

const adjustCurrentStock = ref(0)
const adjustAfterStock = ref(0)

/**
 * 加载库存列表
 */
const loadStockList = async () => {
  try {
    loading.value = true
    const params = {
      page: pagination.page,
      page_size: pagination.limit,
      search: searchForm.goods_name || undefined,
      stock_status: searchForm.stock_status || undefined
    }
    
    // 响应拦截器已自动处理，直接返回 data
    const response = await getStockListEnhanced(params)
    stockList.value = response.items
    pagination.total = response.total
  } catch (error) {
    ElMessage.error('加载库存列表失败：' + (error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

/**
 * 加载所有物品列表（用于入库单价读取）
 */
const loadAllGoodsList = async () => {
  try {
    // 响应拦截器已自动处理，直接返回 data
    // 不传递status参数，加载所有状态的物品（包括非正常状态的物品）
    const response = await getGoodsList({
      page: 1,
      page_size: 100  // 加载足够多的物品，确保包含所有状态的物品
    })
    allGoodsList.value = response.items
  } catch (error) {
    ElMessage.error('加载物品列表失败：' + error.message)
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
 * 处理搜索
 */
const handleSearch = () => {
  pagination.page = 1
  loadStockList()
}

/**
 * 处理显示低库存
 */
const handleShowLowStock = () => {
  searchForm.goods_name = ''
  searchForm.stock_status = 'low'
  pagination.page = 1
  loadStockList()
}

/**
 * 处理重置
 */
const handleReset = () => {
  searchForm.goods_name = ''
  searchForm.stock_status = ''
  pagination.page = 1
  loadStockList()
}

/**
 * 获取库存样式类
 *
 * @param {Object} row - 行数据
 * @returns {string} 样式类名
 */
const getStockClass = (row) => {
  if (!row.stock_status) return ''
  const classMap = {
    'low': 'stock-low',
    'over': 'stock-over',
    'normal': ''
  }
  return classMap[row.stock_status] || ''
}

/**
 * 获取库存状态标签文本
 *
 * @param {Object} row - 行数据
 * @returns {string} 状态文本
 */
const getStockStatusLabel = (row) => {
  const labelMap = {
    'low': '低库存',
    'over': '过高',
    'normal': '正常'
  }
  return labelMap[row.stock_status] || '未知'
}

/**
 * 获取库存状态样式类
 *
 * @param {Object} row - 行数据
 * @returns {string} 样式类名
 */
const getStockStatusClass = (row) => {
  const classMap = {
    'low': 's-danger',
    'over': 's-warning',
    'normal': 's-active'
  }
  return classMap[row.stock_status] || ''
}

/**
 * 获取物品状态样式类
 *
 * @param {number} status - 状态码
 * @returns {string} 样式类名
 */
const getStatusClass = (status) => {
  const classMap = {
    1: 's-active',
    2: 's-danger',
    3: 's-warning'
  }
  return classMap[status] || ''
}

/**
 * 获取库存状态类型
 *
 * @param {Object} row - 行数据
 * @returns {string} 标签类型
 */
const getStockStatusType = (row) => {
  const typeMap = {
    'low': 'danger',
    'over': 'warning',
    'normal': 'success'
  }
  return typeMap[row.stock_status] || 'info'
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
    
    // 响应拦截器已自动处理错误提示，这里不需要额外处理
    await createStockIn(inFormData)
    
    ElMessage.success('入库成功')
    inDialogVisible.value = false
    loadStockList()
  } catch (error) {
    // 错误已被拦截器处理并显示，这里仅记录或做其他处理
    if (error !== false) {
      console.error('入库失败：', error)
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
    
    // 响应拦截器已自动处理错误提示，这里不需要额外处理
    await createStockOut(outFormData)
    
    ElMessage.success('出库成功')
    outDialogVisible.value = false
    loadStockList()
  } catch (error) {
    // 错误已被拦截器处理并显示，这里仅记录或做其他处理
    if (error !== false) {
      console.error('出库失败：', error)
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
 * 处理库存调整
 */
const handleStockAdjust = () => {
  if (stockList.value.length === 0) {
    ElMessage.warning('暂无可用物品')
    return
  }
  
  // 重置表单
  adjustFormData.goods_id = null
  adjustFormData.adjust_quantity = 0
  adjustFormData.adjust_reason = ''
  adjustCurrentStock.value = 0
  adjustAfterStock.value = 0
  
  adjustDialogVisible.value = true
}

/**
 * 处理物品变更（库存调整）
 */
const handleAdjustGoodsChange = (goodsId) => {
  const goods = stockList.value.find(item => item.goods_id === goodsId)
  if (goods) {
    adjustCurrentStock.value = goods.current_stock || 0
    calculateAdjustAfterStock()
  }
}

/**
 * 计算调整后库存
 */
const calculateAdjustAfterStock = () => {
  adjustAfterStock.value = adjustCurrentStock.value + adjustFormData.adjust_quantity
}

/**
 * 监听调整数量变化
 */
watch(() => adjustFormData.adjust_quantity, () => {
  calculateAdjustAfterStock()
})

/**
 * 处理库存调整表单提交
 */
const handleAdjustSubmit = async () => {
  try {
    await adjustFormRef.value.validate()
    
    // 验证调整后库存
    if (adjustAfterStock.value < 0) {
      ElMessage.error('调整后库存不能为负数')
      return
    }
    
    adjustSubmitting.value = true
    
    // 响应拦截器已自动处理错误提示，这里不需要额外处理
    await adjustStock(adjustFormData)
    
    ElMessage.success('库存调整成功')
    adjustDialogVisible.value = false
    loadStockList()
  } catch (error) {
    // 错误已被拦截器处理并显示，这里仅记录或做其他处理
    if (error !== 'cancel') {
      console.error('库存调整失败：', error)
    }
  } finally {
    adjustSubmitting.value = false
  }
}

/**
 * 处理库存调整对话框关闭
 */
const handleAdjustDialogClose = () => {
  adjustFormRef.value?.resetFields()
}

/**
 * 处理单个物品阈值设置
 */
const handleThreshold = (row) => {
  thresholdFormData.goods_id = row.goods_id
  thresholdFormData.goods_name = row.goods_name
  thresholdFormData.current_stock = row.current_stock
  thresholdFormData.min_stock = row.min_stock
  thresholdFormData.max_stock = row.max_stock
  thresholdDialogVisible.value = true
}

/**
 * 处理单个物品阈值表单提交
 */
const handleThresholdSubmit = async () => {
  try {
    await thresholdFormRef.value.validate()
    
    thresholdSubmitting.value = true
    
    await updateStockThreshold({
      goods_id: thresholdFormData.goods_id,
      min_stock: thresholdFormData.min_stock,
      max_stock: thresholdFormData.max_stock
    })
    
    ElMessage.success('库存阈值设置成功')
    thresholdDialogVisible.value = false
    loadStockList()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('设置库存阈值失败：', error)
    }
  } finally {
    thresholdSubmitting.value = false
  }
}

/**
 * 处理单个物品阈值对话框关闭
 */
const handleThresholdDialogClose = () => {
  thresholdFormRef.value?.resetFields()
}

/**
 * 加载系统配置
 */
const loadSystemConfig = async () => {
  try {
    const response = await getConfigs()
    if (response && response.items) {
      const configMap = {}
      response.items.forEach(config => {
        configMap[config.config_key] = config.config_value
      })
      
      // 读取库存预警阈值配置
      if (configMap.min_stock_alert) {
        defaultMinStock.value = parseInt(configMap.min_stock_alert, 10)
      }
      if (configMap.max_stock_alert) {
        defaultMaxStock.value = parseInt(configMap.max_stock_alert, 10)
      }
    }
  } catch (error) {
    console.error('加载系统配置失败：', error)
    // 使用默认值
    defaultMinStock.value = 10
    defaultMaxStock.value = 1000
  }
}

/**
 * 处理批量阈值设置
 */
const handleBatchThreshold = () => {
  batchThresholdFormData.min_stock = defaultMinStock.value
  batchThresholdFormData.max_stock = defaultMaxStock.value
  batchThresholdDialogVisible.value = true
}

/**
 * 处理批量阈值表单提交
 */
const handleBatchThresholdSubmit = async () => {
  try {
    await batchThresholdFormRef.value.validate()
    
    batchThresholdSubmitting.value = true
    
    const result = await batchUpdateStockThresholds({
      min_stock: batchThresholdFormData.min_stock,
      max_stock: batchThresholdFormData.max_stock
    })
    
    ElMessage.success(result.message || '批量设置库存阈值成功')
    batchThresholdDialogVisible.value = false
    loadStockList()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('批量设置库存阈值失败：', error)
    }
  } finally {
    batchThresholdSubmitting.value = false
  }
}

/**
 * 处理批量阈值对话框关闭
 */
const handleBatchThresholdDialogClose = () => {
  batchThresholdFormRef.value?.resetFields()
}

/**
 * 组件挂载时加载数据
 */
onMounted(() => {
  loadSystemConfig()  // 加载系统配置
  loadStockList()
  loadAllGoodsList()
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
  padding: 16px 24px;
  border-radius: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  box-shadow: 0 4px 20px -5px rgba(0, 0, 0, 0.05);
  position: sticky;
  top: 0;
  z-index: 10;
}

.toolbar-left { display: flex; gap: 12px; }
.search-input { width: 260px; }
.filter-select { width: 140px; }

.toolbar-right { display: flex; gap: 12px; align-items: center; }

/* 2. 内容卡片 */
.content-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
  min-height: 650px;
}

/* 3. 字体与细节优化 */
.num-font {
  font-family: 'Oswald', sans-serif !important;
  font-weight: 500;
  letter-spacing: -0.2px;
}

.secondary-num { color: #94a3b8; font-size: 13px; }
.price-text { color: #2563eb; font-size: 16px; font-weight: 600; }
.price-text::before { content: '¥'; font-size: 12px; margin-right: 2px; font-family: sans-serif; }

.fw-600 { font-weight: 600; }
.text-main { color: #1e293b; }

/* 4. 状态标签设计 */
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

/* 库存状态样式 */
.stock-low { color: #ef4444; font-weight: 600; }
.stock-over { color: #f59e0b; font-weight: 600; }

/* 5. 按钮样式调整 */
.edit-btn {
  color: #3b82f6 !important;
  font-weight: 500;
}
.edit-btn:hover {
  color: #2563eb !important;
}

/* 6. 对话框样式 */
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* 响应式适配 */
@media (max-width: 992px) {
  .glass-toolbar { flex-direction: column; gap: 16px; align-items: stretch; }
  .toolbar-left { flex-direction: column; }
  .toolbar-right { width: 100%; justify-content: flex-start; }
  .search-input, .filter-select { width: 100%; }
}
</style>
