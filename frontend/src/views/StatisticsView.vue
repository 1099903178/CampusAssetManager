/**
 * CampusAssetManager/frontend/src/views/StatisticsView.vue
 * 统计报表页面
 * 
 * 功能说明：
 * - 库存统计图表
 * - 出入库趋势图
 * - 分类统计图
 * - 报表导出功能
 * 
 * 作者：CampusAssetManager开发团队
 * 日期：2026-01-05
 */

<template>
    <div class="statistics-container">
      <!-- 统计卡片 -->
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-item">
              <div class="stat-label">物品总数</div>
              <div class="stat-value">{{ summary.total_goods }}</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-item">
              <div class="stat-label">库存总额</div>
              <div class="stat-value">¥{{ summary.total_value }}</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-item">
              <div class="stat-label">本月入库</div>
              <div class="stat-value">{{ summary.monthly_in }}</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-item">
              <div class="stat-label">本月出库</div>
              <div class="stat-value">{{ summary.monthly_out }}</div>
            </div>
          </el-card>
        </el-col>
      </el-row>
      
      <!-- 图表区域 -->
      <el-row :gutter="20" style="margin-top: 20px;">
        <!-- 分类统计图 -->
        <el-col :span="12">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>物品分类统计</span>
              </div>
            </template>
            <div ref="categoryChartRef" class="chart"></div>
          </el-card>
        </el-col>
        
        <!-- 出入库趋势图 -->
        <el-col :span="12">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>出入库趋势</span>
                <el-date-picker
                  v-model="dateRange"
                  type="daterange"
                  range-separator="至"
                  start-placeholder="开始日期"
                  end-placeholder="结束日期"
                  size="small"
                  @change="handleDateChange"
                />
              </div>
            </template>
            <div ref="trendChartRef" class="chart"></div>
          </el-card>
        </el-col>
      </el-row>
      
      <!-- 库存预警 -->
      <el-card style="margin-top: 20px;">
        <template #header>
          <div class="card-header">
            <span>库存预警</span>
            <el-button type="primary" size="small" @click="handleExport">导出报表</el-button>
          </div>
        </template>
        <el-table :data="alertList" style="width: 100%">
          <el-table-column prop="goods_name" label="物品名称" />
          <el-table-column prop="current_stock" label="当前库存" align="right" />
          <el-table-column prop="min_stock" label="最小库存" align="right" />
          <el-table-column label="状态" align="center">
            <template #default="{ row }">
              <el-tag type="danger" v-if="row.current_stock === 0">缺货</el-tag>
              <el-tag type="warning" v-else-if="row.current_stock < row.min_stock">库存不足</el-tag>
              <el-tag type="info" v-else>正常</el-tag>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import { getStockOverview, getCategoryStatistics, getStockAlert } from '@/api'

/**
 * 分类图表引用
 */
const categoryChartRef = ref(null)

/**
 * 趋势图表引用
 */
const trendChartRef = ref(null)

/**
 * 分类图表实例
 */
let categoryChart = null

/**
 * 趋势图表实例
 */
let trendChart = null

/**
 * 日期范围
 */
const dateRange = ref([])

/**
 * 汇总数据
 */
const summary = reactive({
  total_goods: 0,
  total_value: '0.00',
  monthly_in: 0,
  monthly_out: 0
})

/**
 * 预警列表
 */
const alertList = ref([])

/**
 * 加载库存概览
 */
const loadStockOverview = async () => {
  try {
    const response = await getStockOverview()
    Object.assign(summary, response)
  } catch (error) {
    ElMessage.error('加载库存概览失败')
  }
}

/**
 * 加载分类统计
 */
const loadCategoryStatistics = async () => {
  try {
    const response = await getCategoryStatistics()
    
    await nextTick()
    
    /**
     * 初始化分类图表
     */
    if (!categoryChart) {
      categoryChart = echarts.init(categoryChartRef.value)
    }
    
    /**
     * 配置图表
     */
    const option = {
      tooltip: {
        trigger: 'item'
      },
      legend: {
        orient: 'vertical',
        left: 'left'
      },
      series: [
        {
          name: '物品分类',
          type: 'pie',
          radius: '50%',
          data: response.map(item => ({
            value: item.count,
            name: item.category_name
          })),
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          }
        }
      ]
    }
    
    categoryChart.setOption(option)
  } catch (error) {
    ElMessage.error('加载分类统计失败')
  }
}

/**
 * 加载库存预警
 */
const loadStockAlert = async () => {
  try {
    const response = await getStockAlert()
    alertList.value = response
  } catch (error) {
    ElMessage.error('加载库存预警失败')
  }
}

/**
 * 处理日期变化
 */
const handleDateChange = (dates) => {
  ElMessage.info('日期选择功能待实现')
}

/**
 * 处理导出
 */
const handleExport = () => {
  ElMessage.info('导出报表功能待实现')
}

/**
 * 组件卸载时销毁图表
 */
onUnmounted(() => {
  if (categoryChart) {
    categoryChart.dispose()
  }
  if (trendChart) {
    trendChart.dispose()
  }
})

/**
 * 组件挂载时加载数据
 */
onMounted(() => {
  loadStockOverview()
  loadCategoryStatistics()
  loadStockAlert()
  
  /**
   * 窗口大小变化时重绘图表
   */
  window.addEventListener('resize', () => {
    categoryChart?.resize()
    trendChart?.resize()
  })
})
</script>

<script>
import { onUnmounted } from 'vue'
export default {
  name: 'StatisticsView'
}
</script>

<style scoped>
.statistics-container {
  padding: 20px;
}

/**
 * 统计卡片
 */
.stat-card {
  margin-bottom: 20px;
  cursor: pointer;
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.stat-item {
  text-align: center;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 10px;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

/**
 * 卡片头部
 */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 16px;
  font-weight: 600;
}

/**
 * 图表容器
 */
.chart {
  width: 100%;
  height: 300px;
}
</style>