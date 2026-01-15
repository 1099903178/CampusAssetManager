/**
 * CampusAssetManager/frontend/src/views/GoodsView.vue
 * 物品管理页面
 *
 * 功能说明：
 * - 物品列表展示（支持分页、搜索）
 * - 物品搜索和筛选
 * - 物品增删改查（CRUD）
 * - 物品批量导入导出
 *
 * 设计原则：
 * - 声明式：使用Vue Composition API
 * - 组件化：使用Element Plus组件
 * - 响应式：使用ref和reactive管理状态
 *
 * 作者：CampusAssetManager开发团队
 * 日期：2026-01-06
 */

/* Template 区域已应用新设计风格，Script 业务逻辑保持不变 */

<template>
  <div class="page-container">
    <div class="glass-toolbar">
      <div class="toolbar-left">
        <el-input
          v-model="searchForm.search"
          placeholder="搜索物品名称 / 编码..."
          :prefix-icon="Search"
          clearable
          class="search-input"
          @clear="handleSearch"
          @keyup.enter="handleSearch"
        />
        
        <el-select
          v-model="searchForm.category_id"
          placeholder="全部分类"
          clearable
          class="filter-select"
          @change="handleSearch"
        >
          <el-option
            v-for="category in categories"
            :key="category.category_id"
            :label="category.category_name"
            :value="category.category_id"
          />
        </el-select>

        <el-select
          v-model="searchForm.status"
          placeholder="资产状态"
          clearable
          class="filter-select"
          @change="handleSearch"
        >
          <el-option label="正常" :value="1" />
          <el-option label="报废" :value="2" />
          <el-option label="维修中" :value="3" />
        </el-select>
      </div>

      <div class="toolbar-right">
        <el-button @click="handleReset">重置</el-button>
        
        <el-button-group class="action-group" v-if="canManage">
           <el-tooltip content="下载模板" placement="top">
             <el-button :icon="Download" @click="handleDownloadTemplate" />
           </el-tooltip>
           <el-tooltip content="批量导入" placement="top">
             <el-button :icon="Upload" @click="handleImport" />
           </el-tooltip>
           <el-tooltip content="导出列表" placement="top">
             <el-button :icon="Share" @click="handleExport" />
           </el-tooltip>
        </el-button-group>
        
        <el-button
          v-if="canManage"
          type="primary"
          :icon="Plus"
          class="create-btn"
          @click="handleAdd"
        >
          新建资产
        </el-button>
      </div>
    </div>

    <div class="content-card">
      <TableComponent
        :key="tableKey"
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
          <el-table-column prop="goods_id" label="ID" width="50" align="center" fixed="left">
            <template #default="{ row }">
              <span class="num-font secondary-num">{{ row.goods_id }}</span>
            </template>
          </el-table-column>

          <el-table-column prop="goods_name" label="物品名称" min-width="150">
            <template #default="{ row }">
              <span class="text-main fw-600">{{ row.goods_name }}</span>
            </template>
          </el-table-column>

          <el-table-column prop="goods_code" label="物品编码" width="110">
            <template #default="{ row }">
              <span class="num-font code-text">{{ row.goods_code }}</span>
            </template>
          </el-table-column>

          <el-table-column prop="category_name" label="分类" width="120" />

          <el-table-column prop="specification" label="规格" width="150" show-overflow-tooltip />

          <el-table-column prop="unit" label="单位" width="80" align="center" />

          <el-table-column prop="purchase_price" label="采购价" width="110" align="right">
            <template #default="{ row }">
              <span class="num-font price-text">
                {{ row.purchase_price ? row.purchase_price.toFixed(2) : '0.00' }}
              </span>
            </template>
          </el-table-column>

          <el-table-column prop="retail_price" label="零售价" width="110" align="right">
            <template #default="{ row }">
              <span class="num-font price-text" v-if="row.retail_price">
                {{ row.retail_price.toFixed(2) }}
              </span>
              <span v-else class="secondary-num">-</span>
            </template>
          </el-table-column>

          <el-table-column prop="status" label="状态" width="110" align="center">
            <template #default="{ row }">
              <div class="status-pill" :class="getStatusClass(row.status)">
                <span class="dot"></span>
                <span>{{ getStatusLabel(row.status) }}</span>
              </div>
            </template>
          </el-table-column>

          <el-table-column v-if="canManage" label="操作" width="160" align="center" fixed="right">
            <template #default="{ row }">
              <el-button link class="edit-btn" @click="handleEdit(row)">编辑</el-button>
              <el-divider direction="vertical" />
              <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
            </template>
          </el-table-column>
        </template>
      </TableComponent>
    </div>
    
    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      class="custom-dialog"
      @close="handleDialogClose"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
        class="modern-form"
      >
        <el-form-item label="物品名称" prop="goods_name">
          <el-input v-model="formData.goods_name" placeholder="请输入物品全称" />
        </el-form-item>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="物品编码" prop="goods_code">
              <el-input v-model="formData.goods_code" placeholder="留空则自动生成" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="所属分类" prop="category_id">
              <el-select v-model="formData.category_id" placeholder="请选择" style="width: 100%">
                <el-option
                  v-for="c in categories"
                  :key="c.category_id"
                  :label="c.category_name"
                  :value="c.category_id"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="规格型号" prop="specification">
              <el-input v-model="formData.specification" placeholder="如：16G/512G" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="计量单位" prop="unit">
              <el-input v-model="formData.unit" placeholder="如：个、台、箱" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="采购单价" prop="purchase_price">
              <el-input-number
                v-model="formData.purchase_price"
                :precision="2"
                :step="0.01"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="零售单价" prop="retail_price">
              <el-input-number
                v-model="formData.retail_price"
                :precision="2"
                :min="0"
                :step="0.01"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="物品描述" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            rows="3"
          />
        </el-form-item>

        <el-form-item label="资产状态" prop="status">
          <el-radio-group v-model="formData.status">
            <el-radio-button :value="1">正常</el-radio-button>
            <el-radio-button :value="2">报废</el-radio-button>
            <el-radio-button :value="3">维修中</el-radio-button>
          </el-radio-group>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSave" :loading="submitLoading">保存信息</el-button>
        </div>
      </template>
    </el-dialog>
    
    <!-- 导入对话框 -->
    <el-dialog
      v-model="importDialogVisible"
      title="批量导入物品"
      width="500px"
      class="custom-dialog"
      @close="handleImportDialogClose"
    >
      <el-upload
        ref="uploadRef"
        drag
        accept=".xlsx,.xls"
        :auto-upload="false"
        :on-change="handleFileChange"
        :file-list="fileList"
        :limit="1"
      >
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">
          将文件拖到此处，或<em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            只能上传 xlsx/xls 文件，且不超过 10MB
          </div>
        </template>
      </el-upload>
      
      <template #footer>
        <el-button @click="importDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleConfirmImport" :loading="importLoading">确认导入</el-button>
      </template>
    </el-dialog>
    
    <!-- 导入结果对话框 -->
    <el-dialog
      v-model="importResultDialogVisible"
      title="导入结果"
      width="600px"
      class="custom-dialog"
    >
      <el-result
        :icon="importResult.success_count > 0 ? 'success' : 'error'"
        :title="`导入完成：成功 ${importResult.success_count} 条，失败 ${importResult.failed_count} 条`"
        :sub-title="importResult.failed_count > 0 ? '请查看下方错误详情' : ''"
      />
      
      <div v-if="importResult.errors.length > 0" class="error-list">
        <el-descriptions title="错误详情" :column="1" border>
          <el-descriptions-item
            v-for="(error, index) in importResult.errors"
            :key="index"
            :label="`第${error.row}行`"
          >
            <el-tag type="danger">{{ error.goods_code }}</el-tag>
            <span class="error-message">{{ error.error_message }}</span>
          </el-descriptions-item>
        </el-descriptions>
      </div>
      
      <template #footer>
        <el-button @click="importResultDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Plus, Download, Upload, Share, UploadFilled } from '@element-plus/icons-vue'
import TableComponent from '@/components/common/TableComponent.vue'
import {
  getGoodsList,
  getGoodsDetail,
  createGoods,
  updateGoods,
  deleteGoods,
  getGoodsCategories,
  downloadImportTemplate,
  importGoods,
  exportGoods
} from '@/api'
import { useUserStore } from '@/stores/user'

/**
 * 表格组件引用
 */
const tableRef = ref(null)

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
 * 表格组件的 key（用于强制重新渲染）
 */
const tableKey = ref(0)

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
 * 上传组件引用
 */
const uploadRef = ref(null)

/**
 * 导入对话框可见性
 */
const importDialogVisible = ref(false)

/**
 * 导入结果对话框可见性
 */
const importResultDialogVisible = ref(false)

/**
 * 导入加载状态
 */
const importLoading = ref(false)

/**
 * 文件列表
 */
const fileList = ref([])

/**
 * 当前上传的文件
 */
const currentFile = ref(null)

/**
 * 导入结果
 */
const importResult = reactive({
  total_count: 0,
  success_count: 0,
  failed_count: 0,
  errors: []
})

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
    
    goodsList.value = response.items || []
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
 * 获取资产状态标签文本
 *
 * 根据状态码返回对应的中文标签
 *
 * @param {number} status - 状态码
 *   - 1: 正常
 *   - 2: 报废
 *   - 3: 维修中
 * @returns {string} 状态文本
 */
const getStatusLabel = (status) => {
  const statusMap = {
    1: '正常',
    2: '报废',
    3: '维修中'
  }
  return statusMap[status] || '未知'
}

/**
 * 获取资产状态样式类
 *
 * 根据状态码返回对应的 CSS 类名，用于设置颜色样式
 *
 * @param {number} status - 状态码
 * @returns {string} CSS 类名
 *   - 1: 's-active'（绿色）
 *   - 2: 's-danger'（红色）
 *   - 3: 's-warning'（橙色）
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
 * 处理搜索
 */
const handleSearch = () => {
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
    `确定要删除物品"${row.goods_name}"吗？删除后该物品将被永久删除，无法恢复。`,
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
 * 从 Content-Disposition 响应头中提取文件名
 *
 * @param {string} contentDisposition - Content-Disposition 响应头
 * @returns {string} 文件名
 */
const getFilenameFromContentDisposition = (contentDisposition) => {
  if (!contentDisposition) return 'download.xlsx'
  
  // 尝试匹配 filename*=UTF-8''encoded_filename
  const utf8Match = contentDisposition.match(/filename\*=UTF-8''(.+)/i)
  if (utf8Match) {
    // URL 解码
    try {
      return decodeURIComponent(utf8Match[1])
    } catch (e) {
      console.error('文件名解码失败:', e)
    }
  }
  
  // 尝试匹配 filename="filename"
  const quoteMatch = contentDisposition.match(/filename="(.+)"/i)
  if (quoteMatch) {
    return quoteMatch[1]
  }
  
  // 尝试匹配 filename=filename
  const simpleMatch = contentDisposition.match(/filename=(.+)/i)
  if (simpleMatch) {
    return simpleMatch[1]
  }
  
  return 'download.xlsx'
}

/**
 * 下载导入模板
 */
const handleDownloadTemplate = async () => {
  try {
    const response = await downloadImportTemplate()
    
    // 从响应头提取文件名
    const contentDisposition = response.headers?.['content-disposition']
    const filename = getFilenameFromContentDisposition(contentDisposition)
    
    // 创建下载链接
    const url = window.URL.createObjectURL(response.data)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    ElMessage.success('模板下载成功')
  } catch (error) {
    ElMessage.error('模板下载失败')
  }
}

/**
 * 处理导入按钮点击
 */
const handleImport = () => {
  importDialogVisible.value = true
}

/**
 * 处理文件选择
 */
const handleFileChange = (file) => {
  const isExcel = file.name.endsWith('.xlsx') || file.name.endsWith('.xls')
  const isLt10M = file.size / 1024 / 1024 < 10
  
  if (!isExcel) {
    ElMessage.error('只能上传 Excel 文件！')
    fileList.value = []
    return false
  }
  
  if (!isLt10M) {
    ElMessage.error('上传文件大小不能超过 10MB！')
    fileList.value = []
    return false
  }
  
  currentFile.value = file
  return true
}

/**
 * 处理导入对话框关闭
 */
const handleImportDialogClose = () => {
  fileList.value = []
  currentFile.value = null
  uploadRef.value?.clearFiles()
}

/**
 * 确认导入
 */
const handleConfirmImport = async () => {
  if (!currentFile.value) {
    ElMessage.warning('请选择要导入的文件')
    return
  }
  
  try {
    importLoading.value = true
    const formData = new FormData()
    formData.append('file', currentFile.value.raw)
    
    const response = await importGoods(currentFile.value.raw)
    
    // 显示导入结果
    Object.assign(importResult, {
      total_count: response.total_count,
      success_count: response.success_count,
      failed_count: response.failed_count,
      errors: response.errors || []
    })
    
    importDialogVisible.value = false
    importResultDialogVisible.value = true
    
    // 刷新列表
    if (response.success_count > 0) {
      loadGoodsList()
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '导入失败')
  } finally {
    importLoading.value = false
  }
}

/**
 * 处理导出
 */
const handleExport = async () => {
  try {
    ElMessage.info('正在导出，请稍候...')
    
    const response = await exportGoods({
      search: searchForm.search || undefined,
      category_id: searchForm.category_id || undefined,
      status: searchForm.status || undefined
    })
    
    // 从响应头提取文件名
    const contentDisposition = response.headers?.['content-disposition']
    const filename = getFilenameFromContentDisposition(contentDisposition)
    
    // 创建下载链接
    const url = window.URL.createObjectURL(response.data)
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', filename)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('导出成功')
  } catch (error) {
    ElMessage.error('导出失败')
  }
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
.code-text { color: #64748b; font-size: 14px; background: #f8fafc; padding: 2px 6px; border-radius: 4px; }
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

/* 按钮样式调整 */
.action-group .el-button {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
}
.action-group .el-button:hover {
  color: #2563eb;
  background: white;
}

.edit-btn {
  color: #3b82f6 !important;
  font-weight: 500;
}
.edit-btn:hover {
  color: #2563eb !important;
}

.create-btn {
  padding: 10px 24px;
  border-radius: 10px;
  box-shadow: 0 4px 10px -2px rgba(37, 99, 235, 0.3);
}

/* 响应式适配 */
@media (max-width: 992px) {
  .glass-toolbar { flex-direction: column; gap: 16px; align-items: stretch; }
  .toolbar-left { flex-direction: column; }
  .toolbar-right { width: 100%; justify-content: flex-start; }
  .search-input, .filter-select { width: 100%; }
}
</style>