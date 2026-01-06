/**
 * CampusAssetManager/frontend/src/views/CategoryView.vue
 * 物品分类管理页面
 * 
 * 功能说明：
 * - 物品分类列表展示
 * - 分类增删改查（CRUD）
 * - 分类层级显示
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
  <div class="category-container">
    <!-- 工具栏 -->
    <el-card class="toolbar-card">
      <el-form :inline="true">
        <el-form-item v-if="canManage">
          <el-button type="primary" @click="handleAdd">新增分类</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <!-- 分类列表 -->
    <el-card class="table-card">
      <TableComponent
        :data="categoryList"
        :loading="loading"
        :show-selection="false"
        :pagination="false"
      >
        <template #columns>
          <el-table-column prop="category_id" label="ID" width="80" align="center" />
          <el-table-column prop="category_code" label="分类编码" width="150" />
          <el-table-column prop="category_name" label="分类名称" min-width="150" />
          <el-table-column prop="level" label="层级" width="80" align="center">
            <template #default="{ row }">
              {{ row.level }}
            </template>
          </el-table-column>
          <el-table-column prop="parent_id" label="父分类ID" width="120" align="center">
            <template #default="{ row }">
              {{ row.parent_id || '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
          <el-table-column prop="sort_order" label="排序" width="80" align="center" />
          <el-table-column prop="is_active" label="状态" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="row.is_active === 1 ? 'success' : 'danger'">
                {{ row.is_active === 1 ? '启用' : '禁用' }}
              </el-tag>
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
        label-width="120px"
      >
        <el-form-item label="分类编码" prop="category_code">
          <el-input v-model="formData.category_code" placeholder="请输入分类编码" />
        </el-form-item>
        
        <el-form-item label="分类名称" prop="category_name">
          <el-input v-model="formData.category_name" placeholder="请输入分类名称" />
        </el-form-item>
        
        <el-form-item label="父分类" prop="parent_id">
          <el-select
            v-model="formData.parent_id"
            placeholder="请选择父分类（不选则创建顶级分类）"
            clearable
            allow-create
            filterable
            style="width: 100%"
          >
            <el-option label="无（顶级分类）" :value="null" />
            <el-option
              v-for="category in parentCategories"
              :key="category.category_id"
              :label="category.category_name"
              :value="category.category_id"
              :disabled="category.category_id === formData.category_id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="分类描述" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="3"
            placeholder="请输入分类描述"
          />
        </el-form-item>
        
        <el-form-item label="排序号" prop="sort_order">
          <el-input-number
            v-model="formData.sort_order"
            :min="0"
            :max="999"
            style="width: 100%"
          />
        </el-form-item>
        
        <el-form-item label="是否启用" prop="is_active">
          <el-switch
            v-model="formData.is_active"
            :active-value="1"
            :inactive-value="0"
            active-text="启用"
            inactive-text="禁用"
          />
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
  getGoodsCategories,
  getCategoryDetail,
  createCategory,
  updateCategory,
  deleteCategory
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
 * 分类列表
 */
const categoryList = ref([])

/**
 * 父分类列表（用于下拉选择）
 */
const parentCategories = computed(() => {
  return categoryList.value.filter(cat => cat.parent_id === null)
})

/**
 * 对话框可见性
 */
const dialogVisible = ref(false)

/**
 * 对话框标题
 */
const dialogTitle = computed(() => {
  return formData.category_id ? '编辑分类' : '新增分类'
})

/**
 * 表单数据
 */
const formData = reactive({
  category_id: null,
  category_name: '',
  category_code: '',
  parent_id: null,
  description: '',
  sort_order: 0,
  is_active: 1
})

/**
 * 表单校验规则
 */
const formRules = {
  category_name: [
    { required: true, message: '请输入分类名称', trigger: 'blur' },
    { min: 1, max: 50, message: '分类名称长度在 1 到 50 个字符', trigger: 'blur' }
  ],
  category_code: [
    { required: true, message: '请输入分类编码', trigger: 'blur' },
    { min: 1, max: 20, message: '分类编码长度在 1 到 20 个字符', trigger: 'blur' }
  ]
}

/**
 * 表单引用
 */
const formRef = ref(null)

/**
 * 加载分类列表
 */
const loadCategoryList = async () => {
  try {
    loading.value = true
    const response = await getGoodsCategories()
    categoryList.value = response.items || response
  } catch (error) {
    ElMessage.error('加载分类列表失败')
  } finally {
    loading.value = false
  }
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
    const response = await getCategoryDetail(row.category_id)
    
    // 填充表单数据
    Object.assign(formData, {
      category_id: response.category_id,
      category_name: response.category_name,
      category_code: response.category_code,
      parent_id: response.parent_id,
      description: response.description || '',
      sort_order: response.sort_order,
      is_active: response.is_active
    })
    
    dialogVisible.value = true
  } catch (error) {
    ElMessage.error('获取分类详情失败')
  }
}

/**
 * 处理删除
 * 
 * @param {Object} row - 行数据
 */
const handleDelete = (row) => {
  ElMessageBox.confirm(
    `确定要删除分类"${row.category_name}"吗？删除后将无法恢复。`,
    '删除确认',
    {
      type: 'warning',
      confirmButtonText: '确定',
      cancelButtonText: '取消'
    }
  ).then(async () => {
    try {
      await deleteCategory(row.category_id)
      ElMessage.success('删除成功')
      loadCategoryList()
    } catch (error) {
      ElMessage.error('删除失败：' + (error.message || '未知错误'))
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
        category_name: formData.category_name,
        category_code: formData.category_code,
        parent_id: formData.parent_id,
        description: formData.description,
        sort_order: formData.sort_order,
        is_active: formData.is_active
      }
      
      if (formData.category_id) {
        // 编辑
        await updateCategory(formData.category_id, data)
        ElMessage.success('更新成功')
      } else {
        // 新增
        await createCategory(data)
        ElMessage.success('创建成功')
      }
      
      dialogVisible.value = false
      loadCategoryList()
    } catch (error) {
      ElMessage.error(formData.category_id ? '更新失败' : '创建失败')
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
    category_id: null,
    category_name: '',
    category_code: '',
    parent_id: null,
    description: '',
    sort_order: 0,
    is_active: 1
  })
}

/**
 * 组件挂载时加载数据
 */
onMounted(() => {
  loadCategoryList()
})
</script>

<style scoped>
.category-container {
  padding: 20px;
}

.toolbar-card {
  margin-bottom: 20px;
}

.table-card {
  margin-bottom: 20px;
}
</style>