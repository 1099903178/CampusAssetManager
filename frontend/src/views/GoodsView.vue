/**
 * CampusAssetManager/frontend/src/views/GoodsView.vue
 * 物品管理页面
 * 
 * 功能说明：
 * - 物品列表展示（支持分页、搜索）
 * - 物品搜索和筛选
 * - 物品增删改查（CRUD）
 * 
 * 设计原则：
 * - 声明式：使用Vue Composition API
 * - 组件化：使用Element Plus组件
 * - 响应式：使用ref和reactive管理状态
 * 
 * 作者：CampusAssetManager开发团队
 * 日期：2026-01-06
 */

<template>
  <div class="goods-container">
    <!-- 工具栏 -->
    <el-card class="toolbar-card">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="搜索关键词">
          <el-input
            v-model="searchForm.search"
            placeholder="物品名称/编码"
            clearable
            style="width: 200px"
          />
        </el-form-item>
        
        <el-form-item label="分类">
          <el-select
            v-model="searchForm.category_id"
            placeholder="请选择分类"
            clearable
            style="width: 200px"
          >
            <el-option
              v-for="category in categories"
              :key="category.category_id"
              :label="category.category_name"
              :value="category.category_id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="状态">
          <el-select
            v-model="searchForm.status"
            placeholder="请选择状态"
            clearable
            style="width: 150px"
          >
            <el-option label="正常" :value="1" />
            <el-option label="报废" :value="2" />
            <el-option label="维修中" :value="3" />
          </el-select>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="loadGoodsList">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
      
      <el-button v-if="canManage" type="primary" @click="handleAdd">新增物品</el-button>
    </el-card>
    
    <!-- 物品列表 -->
    <el-card class="table-card">
      <TableComponent
        :data="goodsList"
        :loading="loading"
        :show-selection="false"
        :page="pagination.page"
        :limit="pagination.limit"
        :total="pagination.total"
        @update:page="handlePageChange"
        @update:limit="handleSizeChange"
      >
        <template #columns>
          <el-table-column prop="goods_id" label="ID" width="80" align="center" />
          <el-table-column prop="goods_name" label="物品名称" min-width="150" />
          <el-table-column prop="goods_code" label="物品编码" width="120" />
          <el-table-column prop="category_name" label="分类" width="120" />
          <el-table-column prop="specification" label="规格" width="150" />
          <el-table-column prop="unit" label="单位" width="80" align="center" />
          <el-table-column prop="purchase_price" label="采购价" width="100" align="right">
            <template #default="{ row }">
              ¥{{ row.purchase_price.toFixed(2) }}
            </template>
          </el-table-column>
          <el-table-column prop="retail_price" label="零售价" width="100" align="right">
            <template #default="{ row }">
              {{ row.retail_price ? `¥${row.retail_price.toFixed(2)}` : '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="100" align="center">
            <template #default="{ row }">
              <el-tag v-if="row.status === 1" type="success">正常</el-tag>
              <el-tag v-else-if="row.status === 2" type="danger">报废</el-tag>
              <el-tag v-else type="warning">维修中</el-tag>
            </template>
          </el-table-column>
          <el-table-column v-if="canManage" label="操作" width="200" align="center" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
              <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
            </template>
          </el-table-column>
        </template>
      </TableComponent>
    </el-card>
    
    <!-- 新增/编辑对话框 -->
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
        <el-form-item label="物品名称" prop="goods_name">
          <el-input v-model="formData.goods_name" placeholder="请输入物品名称" />
        </el-form-item>
        
        <el-form-item label="物品编码" prop="goods_code">
          <el-input v-model="formData.goods_code" placeholder="请输入物品编码" />
        </el-form-item>
        
        <el-form-item label="分类" prop="category_id">
          <el-select
            v-model="formData.category_id"
            placeholder="请选择分类"
            style="width: 100%"
          >
            <el-option
              v-for="category in categories"
              :key="category.category_id"
              :label="category.category_name"
              :value="category.category_id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="规格型号" prop="specification">
          <el-input v-model="formData.specification" placeholder="请输入规格型号" />
        </el-form-item>
        
        <el-form-item label="计量单位" prop="unit">
          <el-input v-model="formData.unit" placeholder="如：个、台、箱等" />
        </el-form-item>
        
        <el-form-item label="采购单价" prop="purchase_price">
          <el-input-number
            v-model="formData.purchase_price"
            :precision="2"
            :min="0"
            :step="0.01"
            style="width: 100%"
          />
        </el-form-item>
        
        <el-form-item label="零售单价" prop="retail_price">
          <el-input-number
            v-model="formData.retail_price"
            :precision="2"
            :min="0"
            :step="0.01"
            style="width: 100%"
          />
        </el-form-item>
        
        <el-form-item label="物品描述" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="3"
            placeholder="请输入物品描述"
          />
        </el-form-item>
        
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="formData.status">
            <el-radio :label="1">正常</el-radio>
            <el-radio :label="2">报废</el-radio>
            <el-radio :label="3">维修中</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave" :loading="submitLoading">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import TableComponent from '@/components/common/TableComponent.vue'
import {
  getGoodsList,
  getGoodsDetail,
  createGoods,
  updateGoods,
  deleteGoods,
  getGoodsCategories
} from '@/api'
import { useUserStore } from '@/stores/user'

/**
 * 用户状态管理
 */
const userStore = useUserStore()

/**
 * 是否有管理权限（只有admin和super_admin可以管理）
 */
const canManage = computed(() => {
  return userStore.hasPermission('admin')
})

/**
 * 加载状态
 */
const loading = ref(false)

/**
 * 提交状态
 */
const submitLoading = ref(false)

/**
 * 物品列表
 */
const goodsList = ref([])

/**
 * 分类列表
 */
const categories = ref([])

/**
 * 搜索表单
 */
const searchForm = reactive({
  search: '',
  category_id: null,
  status: null
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
 * 对话框可见性
 */
const dialogVisible = ref(false)

/**
 * 对话框标题
 */
const dialogTitle = computed(() => {
  return formData.goods_id ? '编辑物品' : '新增物品'
})

/**
 * 表单数据
 */
const formData = reactive({
  goods_id: null,
  goods_name: '',
  goods_code: '',
  category_id: null,
  specification: '',
  unit: '',
  purchase_price: 0,
  retail_price: null,
  description: '',
  status: 1
})

/**
 * 表单校验规则
 */
const formRules = {
  goods_name: [
    { required: true, message: '请输入物品名称', trigger: 'blur' }
  ],
  goods_code: [
    { required: true, message: '请输入物品编码', trigger: 'blur' }
  ],
  category_id: [
    { required: true, message: '请选择分类', trigger: 'change' }
  ],
  unit: [
    { required: true, message: '请输入计量单位', trigger: 'blur' }
  ],
  purchase_price: [
    { required: true, message: '请输入采购单价', trigger: 'blur' }
  ]
}

/**
 * 表单引用
 */
const formRef = ref(null)

/**
 * 加载物品列表
 */
const loadGoodsList = async () => {
  try {
    loading.value = true
    const response = await getGoodsList({
      page: pagination.page,
      page_size: pagination.limit,
      search: searchForm.search || undefined,
      category_id: searchForm.category_id || undefined,
      status: searchForm.status || undefined
    })
    goodsList.value = response.items
    pagination.total = response.total
  } catch (error) {
    ElMessage.error('加载物品列表失败')
  } finally {
    loading.value = false
  }
}

/**
 * 加载分类列表
 */
const loadCategories = async () => {
  try {
    const response = await getGoodsCategories()
    categories.value = response.items || response
  } catch (error) {
    ElMessage.error('加载分类列表失败')
  }
}

/**
 * 处理页码变化
 * 
 * @param {number} page - 页码
 */
const handlePageChange = (page) => {
  pagination.page = page
  loadGoodsList()
}

/**
 * 处理每页数量变化
 * 
 * @param {number} limit - 每页数量
 */
const handleSizeChange = (limit) => {
  pagination.limit = limit
  pagination.page = 1
  loadGoodsList()
}

/**
 * 处理重置
 */
const handleReset = () => {
  searchForm.search = ''
  searchForm.category_id = null
  searchForm.status = null
  pagination.page = 1
  loadGoodsList()
}

/**
 * 处理新增
 */
const handleAdd = () => {
  dialogVisible.value = true
}

/**
 * 处理编辑
 * 
 * @param {Object} row - 行数据
 */
const handleEdit = async (row) => {
  try {
    const response = await getGoodsDetail(row.goods_id)
    
    // 填充表单数据
    Object.assign(formData, {
      goods_id: response.goods_id,
      goods_name: response.goods_name,
      goods_code: response.goods_code,
      category_id: response.category_id,
      specification: response.specification || '',
      unit: response.unit,
      purchase_price: response.purchase_price,
      retail_price: response.retail_price,
      description: response.description || '',
      status: response.status
    })
    
    dialogVisible.value = true
  } catch (error) {
    ElMessage.error('获取物品详情失败')
  }
}

/**
 * 处理删除
 * 
 * @param {Object} row - 行数据
 */
const handleDelete = (row) => {
  ElMessageBox.confirm(
    `确定要删除物品"${row.goods_name}"吗？删除后该物品状态将变为报废。`,
    '删除确认',
    {
      type: 'warning',
      confirmButtonText: '确定',
      cancelButtonText: '取消'
    }
  ).then(async () => {
    try {
      await deleteGoods(row.goods_id)
      ElMessage.success('删除成功')
      loadGoodsList()
    } catch (error) {
      ElMessage.error('删除失败')
    }
  }).catch(() => {
    // 取消删除
  })
}

/**
 * 处理保存
 */
const handleSave = async () => {
  // 表单验证
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    try {
      submitLoading.value = true
      
      const data = {
        goods_name: formData.goods_name,
        goods_code: formData.goods_code,
        category_id: formData.category_id,
        specification: formData.specification,
        unit: formData.unit,
        purchase_price: formData.purchase_price,
        retail_price: formData.retail_price,
        description: formData.description,
        status: formData.status
      }
      
      if (formData.goods_id) {
        // 编辑
        await updateGoods(formData.goods_id, data)
        ElMessage.success('更新成功')
      } else {
        // 新增
        await createGoods(data)
        ElMessage.success('创建成功')
      }
      
      dialogVisible.value = false
      loadGoodsList()
    } catch (error) {
      ElMessage.error(formData.goods_id ? '更新失败' : '创建失败')
    } finally {
      submitLoading.value = false
    }
  })
}

/**
 * 处理对话框关闭
 */
const handleDialogClose = () => {
  formRef.value?.resetFields()
  Object.assign(formData, {
    goods_id: null,
    goods_name: '',
    goods_code: '',
    category_id: null,
    specification: '',
    unit: '',
    purchase_price: 0,
    retail_price: null,
    description: '',
    status: 1
  })
}

/**
 * 组件挂载时加载数据
 */
onMounted(() => {
  loadGoodsList()
  loadCategories()
})
</script>

<style scoped>
.goods-container {
  padding: 20px;
}

.toolbar-card {
  margin-bottom: 20px;
}

.table-card {
  margin-bottom: 20px;
}
</style>