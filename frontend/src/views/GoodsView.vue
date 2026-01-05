/**
 * CampusAssetManager/frontend/src/views/GoodsView.vue
 * 物品管理页面
 * 
 * 功能说明：
 * - 物品列表展示
 * - 物品搜索和筛选
 * - 物品增删改查
 * 
 * 作者：CampusAssetManager开发团队
 * 日期：2026-01-05
 */

<template>
  <LayoutComponent>
    <div class="goods-container">
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
          
          <el-form-item>
            <el-button type="primary" @click="loadGoodsList">搜索</el-button>
            <el-button @click="handleReset">重置</el-button>
          </el-form-item>
        </el-form>
        
        <el-button type="primary" @click="handleAdd">新增物品</el-button>
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
            <el-table-column prop="category_name" label="分类" width="120" />
            <el-table-column prop="specification" label="规格" width="150" />
            <el-table-column prop="unit_price" label="单价" width="100" align="right">
              <template #default="{ row }">
                ¥{{ row.unit_price.toFixed(2) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="180" align="center">
              <template #default="{ row }">
                <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
                <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
              </template>
            </el-table-column>
          </template>
        </TableComponent>
      </el-card>
    </div>
  </LayoutComponent>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import LayoutComponent from '@/components/common/LayoutComponent.vue'
import TableComponent from '@/components/common/TableComponent.vue'
import { getGoodsList, getGoodsCategories, deleteGoods } from '@/api'

/**
 * 加载状态
 */
const loading = ref(false)

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
  goods_name: '',
  category_id: null
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
 * 加载物品列表
 */
const loadGoodsList = async () => {
  try {
    loading.value = true
    const response = await getGoodsList({
      page: pagination.page,
      page_size: pagination.limit,
      ...searchForm
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
    categories.value = response
  } catch (error) {
    console.error('加载分类列表失败:', error)
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
  searchForm.goods_name = ''
  searchForm.category_id = null
  loadGoodsList()
}

/**
 * 处理新增
 */
const handleAdd = () => {
  ElMessage.info('新增物品功能待实现')
}

/**
 * 处理编辑
 * 
 * @param {Object} row - 行数据
 */
const handleEdit = (row) => {
  ElMessage.info(`编辑物品：${row.goods_name}`)
}

/**
 * 处理删除
 * 
 * @param {Object} row - 行数据
 */
const handleDelete = (row) => {
  ElMessageBox.confirm(
    `确定要删除物品"${row.goods_name}"吗？`,
    '删除确认',
    {
      type: 'warning'
    }
  ).then(async () => {
    try {
      await deleteGoods(row.goods_id)
      ElMessage.success('删除成功')
      loadGoodsList()
    } catch (error) {
      ElMessage.error('删除失败')
    }
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
  height: calc(100vh - 250px);
}
</style>