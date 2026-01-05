/**
 * CampusAssetManager/frontend/src/views/StockView.vue
 * 库存管理页面
 * 
 * 功能说明：
 * - 库存列表展示
 * - 入库出库操作
 * - 库存查询
 * 
 * 作者：CampusAssetManager开发团队
 * 日期：2026-01-05
 */

<template>
  <LayoutComponent>
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
            <el-table-column prop="stock_id" label="ID" width="80" align="center" />
            <el-table-column prop="goods_name" label="物品名称" min-width="150" />
            <el-table-column prop="current_stock" label="当前库存" width="100" align="right" />
            <el-table-column prop="unit" label="单位" width="80" align="center" />
            <el-table-column prop="specification" label="规格" width="150" />
            <el-table-column label="操作" width="180" align="center">
              <template #default="{ row }">
                <el-button type="primary" link @click="handleDetail(row)">详情</el-button>
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
import { ElMessage } from 'element-plus'
import LayoutComponent from '@/components/common/LayoutComponent.vue'
import TableComponent from '@/components/common/TableComponent.vue'
import { getStockList } from '@/api'

/**
 * 加载状态
 */
const loading = ref(false)

/**
 * 库存列表
 */
const stockList = ref([])

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
 * 加载库存列表
 */
const loadStockList = async () => {
  try {
    loading.value = true
    const response = await getStockList({
      page: pagination.page,
      page_size: pagination.limit,
      ...searchForm
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
  loadStockList()
}

/**
 * 处理入库
 */
const handleStockIn = () => {
  ElMessage.info('入库功能待实现')
}

/**
 * 处理出库
 */
const handleStockOut = () => {
  ElMessage.info('出库功能待实现')
}

/**
 * 处理详情
 * 
 * @param {Object} row - 行数据
 */
const handleDetail = (row) => {
  ElMessage.info(`查看库存详情：${row.goods_name}`)
}

/**
 * 组件挂载时加载数据
 */
onMounted(() => {
  loadStockList()
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
</style>