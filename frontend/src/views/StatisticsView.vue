/**
 * CampusAssetManager/frontend/src/views/StatisticsView.vue
 * 统计报表页面
 * 
 * 功能说明：
 * - 数据概览卡片（物品总数、库存总数、今日入库、今日出库、预警数量）
 * - 库存趋势图表（折线图，支持时间范围选择）
 * - 物品排行榜图表（柱状图，支持入库/出库切换）
 * - 分类统计图表（饼图，支持库存/入库切换）
 * - 图表交互功能（点击显示详细信息）
 * 
 * 作者：CampusAssetManager开发团队
 * 日期：2026-01-09
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
              <div class="stat-label">库存总数</div>
              <div class="stat-value">{{ summary.total_stock }}</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-item">
              <div class="stat-label">今日入库</div>
              <div class="stat-value">{{ summary.today_stock_in }}</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-item">
              <div class="stat-label">今日出库</div>
              <div class="stat-value">{{ summary.today_stock_out }}</div>
            </div>
          </el-card>
        </el-col>
      </el-row>
      
      <!-- 图表区域 -->
      <el-row :gutter="20" style="margin-top: 20px;">
        <!-- 库存趋势图 -->
        <el-col :span="24">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>库存趋势</span>
                <div class="chart-controls">
                  <el-radio-group v-model="trendTimeRange" size="small">
                    <el-radio-button value="7">近7天</el-radio-button>
                    <el-radio-button value="30">近30天</el-radio-button>
                    <el-radio-button value="custom">自定义</el-radio-button>
                  </el-radio-group>
                  <el-date-picker
                    v-if="trendTimeRange === 'custom'"
                    v-model="trendDateRange"
                    type="daterange"
                    range-separator="至"
                    start-placeholder="开始日期"
                    end-placeholder="结束日期"
                    size="small"
                    style="margin-left: 10px;"
                  />
                  <el-select
                    v-model="selectedGoodsId"
                    placeholder="选择物品"
                    clearable
                    size="small"
                    style="margin-left: 10px; width: 150px;"
                    @change="handleGoodsChange"
                  >
                    <el-option :value="0" label="全部物品" />
                    <el-option
                      v-for="item in goodsList"
                      :key="item.goods_id"
                      :label="item.goods_name"
                      :value="item.goods_id"
                    />
                  </el-select>
                </div>
              </div>
            </template>
            <div ref="trendChartRef" class="chart"></div>
          </el-card>
        </el-col>
      </el-row>
      
      <el-row :gutter="20" style="margin-top: 20px;">
        <!-- 物品排行榜 -->
        <el-col :span="12">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>物品排行榜</span>
                <el-radio-group v-model="rankingType" size="small">
                  <el-radio-button value="in">入库Top10</el-radio-button>
                  <el-radio-button value="out">出库Top10</el-radio-button>
                </el-radio-group>
              </div>
            </template>
            <div ref="rankingChartRef" class="chart"></div>
          </el-card>
        </el-col>
        
        <!-- 分类统计图 -->
        <el-col :span="12">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>分类统计</span>
                <el-radio-group v-model="categoryStatsType" size="small">
                  <el-radio-button value="stock">库存数量</el-radio-button>
                  <el-radio-button value="in">入库数量</el-radio-button>
                </el-radio-group>
              </div>
            </template>
            <div ref="categoryChartRef" class="chart"></div>
          </el-card>
        </el-col>
      </el-row>
      
      <!-- 预警信息卡片 -->
      <el-card style="margin-top: 20px;">
        <template #header>
          <div class="card-header">
            <span>库存预警</span>
            <el-tag type="warning" v-if="summary.warning_count > 0">
              预警数量：{{ summary.warning_count }}
            </el-tag>
            <el-tag type="success" v-else>无预警物品</el-tag>
          </div>
        </template>
        <el-table :data="alertList" style="width: 100%" v-loading="loadingAlert">
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
      
      <!-- 物品详情对话框 -->
      <el-dialog
        v-model="showGoodsDetail"
        :title="`物品详情 - ${currentGoodsDetail.goods_name || ''}`"
        width="600px"
      >
        <el-descriptions :column="1" border>
          <el-descriptions-item label="物品ID">{{ currentGoodsDetail.goods_id }}</el-descriptions-item>
          <el-descriptions-item label="物品名称">{{ currentGoodsDetail.goods_name }}</el-descriptions-item>
          <el-descriptions-item label="物品编码">{{ currentGoodsDetail.goods_code }}</el-descriptions-item>
          <el-descriptions-item label="数量">{{ currentGoodsDetail.total_quantity }}</el-descriptions-item>
        </el-descriptions>
        <template #footer>
          <el-button @click="showGoodsDetail = false">关闭</el-button>
        </template>
      </el-dialog>
      
      <!-- 分类详情对话框 -->
      <el-dialog
        v-model="showCategoryDetail"
        :title="`分类详情 - ${currentCategoryDetail.category_name || ''}`"
        width="600px"
      >
        <el-descriptions :column="1" border>
          <el-descriptions-item label="分类ID">{{ currentCategoryDetail.category_id }}</el-descriptions-item>
          <el-descriptions-item label="分类名称">{{ currentCategoryDetail.category_name }}</el-descriptions-item>
          <el-descriptions-item label="分类编码">{{ currentCategoryDetail.category_code }}</el-descriptions-item>
          <el-descriptions-item label="库存数量">{{ currentCategoryDetail.stock_quantity }}</el-descriptions-item>
          <el-descriptions-item label="入库数量">{{ currentCategoryDetail.in_quantity }}</el-descriptions-item>
        </el-descriptions>
        <template #footer>
          <el-button @click="showCategoryDetail = false">关闭</el-button>
        </template>
      </el-dialog>
    </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import { getDataOverview, getStockTrend, getGoodsRanking, getCategoryStats } from '@/api/statistics'
import { getGoodsList } from '@/api/goods'

/**
 * 图表DOM引用
 */
const trendChartRef = ref(null)
const rankingChartRef = ref(null)
const categoryChartRef = ref(null)

/**
 * 图表实例
 */
let trendChart = null
let rankingChart = null
let categoryChart = null

/**
 * 加载状态
 */
const loadingAlert = ref(false)

/**
 * 统计概览数据
 */
const summary = reactive({
  total_goods: 0,
  total_stock: 0,
  today_stock_in: 0,
  today_stock_out: 0,
  warning_count: 0
})

/**
 * 预警列表
 */
const alertList = ref([])

/**
 * 物品列表
 */
const goodsList = ref([])

/**
 * 趋势图配置
 */
/**
 * 趋势图配置
 */
const trendTimeRange = ref('7')
const trendDateRange = ref([])
const selectedGoodsId = ref(0)

/**
 * 处理物品选择变化
 */
const handleGoodsChange = (value) => {
  console.log('=== handleGoodsChange 被调用 ===')
  console.log('新选择的value:', value)
  console.log('新选择的value类型:', typeof value)
  console.log('更新前的 selectedGoodsId.value:', selectedGoodsId.value)
  selectedGoodsId.value = value || 0
  console.log('更新后的 selectedGoodsId.value:', selectedGoodsId.value)
  console.log('更新后的 selectedGoodsId.value类型:', typeof selectedGoodsId.value)
}

/**
 * 排行榜配置
 */
const rankingType = ref('in')
const rankingData = ref([])

/**
 * 分类统计配置
 */
const categoryStatsType = ref('stock')
const categoryData = ref([])

/**
 * 对话框状态
 */
const showGoodsDetail = ref(false)
const currentGoodsDetail = reactive({
  goods_id: null,
  goods_name: '',
  goods_code: '',
  total_quantity: 0
})

const showCategoryDetail = ref(false)
const currentCategoryDetail = reactive({
  category_id: null,
  category_name: '',
  category_code: '',
  stock_quantity: 0,
  in_quantity: 0
})

/**
 * 加载统计概览
 */
const loadSummary = async () => {
  try {
    const response = await getDataOverview()
    Object.assign(summary, response)
  } catch (error) {
    ElMessage.error('加载统计概览失败')
  }
}

/**
 * 加载库存趋势
 */
const loadStockTrend = async () => {
  try {
    let startDate, endDate
    
    // 如果是自定义时间范围，但未选择日期，则不执行请求
    if (trendTimeRange.value === 'custom') {
      if (!trendDateRange.value || trendDateRange.value.length !== 2) {
        // 未选择日期范围，静默返回不执行请求
        return
      }
      startDate = formatDate(trendDateRange.value[0])
      endDate = formatDate(trendDateRange.value[1])
    } else {
      const days = parseInt(trendTimeRange.value)
      const now = new Date()
      endDate = formatDate(now)
      startDate = formatDate(new Date(now.getTime() - days * 24 * 60 * 60 * 1000))
    }
    
    const params = {
      start_date: startDate,
      end_date: endDate
    }
    
    if (selectedGoodsId.value && selectedGoodsId.value !== 0) {
      params.goods_id = selectedGoodsId.value
    }
    
    const response = await getStockTrend(params)
    renderTrendChart(response)
  } catch (error) {
    ElMessage.error('加载库存趋势失败')
  }
}

/**
 * 渲染趋势图表
 */
const renderTrendChart = (data) => {
  nextTick(() => {
    // 如果图表实例不存在，则创建新实例
    if (!trendChart) {
      trendChart = echarts.init(trendChartRef.value)
    }
    
    const dates = data.trend_data?.map(item => item.date) || []
    const stocks = data.trend_data?.map(item => item.stock_quantity) || []
    
    const option = {
      tooltip: {
        trigger: 'axis',
        formatter: function(params) {
          const date = params[0].name
          const quantity = params[0].value
          return `${date}<br />库存数量: ${quantity}`
        }
      },
      title: {
        text: data.goods_name || '整体库存趋势',
        left: 'center'
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        boundaryGap: false,
        data: data.trend_data?.map(item => item.date) || []
      },
      yAxis: {
        type: 'value',
        name: '数量'
      },
      series: [
        {
          name: '库存数量',
          type: 'line',
          data: data.trend_data?.map(item => item.stock_quantity) || [],
          smooth: true,
          areaStyle: {
            color: {
              type: 'linear',
              x: 0,
              y: 0,
              x2: 0,
              y2: 1,
              colorStops: [
                {
                  offset: 0,
                  color: 'rgba(64, 158, 255, 0.3)'
                },
                {
                  offset: 1,
                  color: 'rgba(64, 158, 255, 0.05)'
                }
              ]
            }
          },
          itemStyle: {
            color: '#409EFF'
          }
        }
      ]
    }
    
    try {
      // 使用 notMerge: true 强制不合并配置，完全替换
      trendChart.setOption(option, {
        notMerge: true,
        lazyUpdate: false
      })
      
      // 立即执行resize确保图表正确渲染
      trendChart.resize()
      
      // 使用 requestAnimationFrame 确保在下一帧渲染
      requestAnimationFrame(() => {
        if (trendChart && !trendChart.isDisposed()) {
          trendChart.resize()
        }
      })
      
    } catch (error) {
      console.error('setOption调用失败:', error)
    }
  })
}

/**
 * 加载物品排行榜
 */
const loadGoodsRanking = async () => {
  try {
    const response = await getGoodsRanking({
      ranking_type: rankingType.value,
      top_n: 10
    })
    
    rankingData.value = response.ranking_list
    renderRankingChart(response)
  } catch (error) {
    ElMessage.error('加载物品排行榜失败')
  }
}

/**
 * 渲染排行榜图表
 */
const renderRankingChart = (data) => {
  nextTick(() => {
    if (!rankingChart) {
      rankingChart = echarts.init(rankingChartRef.value)
    }
    
    const chartData = data.ranking_list.map(item => [
      item.goods_name,
      item.total_quantity
    ])
    
    const option = {
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow'
        },
        formatter: function(params) {
          const item = data.ranking_list[params[0].dataIndex]
          return `
            ${item.goods_name}<br />
            编码: ${item.goods_code}<br />
            排名: ${item.rank}<br />
            ${rankingType.value === 'in' ? '入库' : '出库'}数量: ${item.total_quantity}
          `
        }
      },
      title: {
        text: rankingType.value === 'in' ? '入库Top10' : '出库Top10',
        left: 'center'
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'value',
        name: '数量'
      },
      yAxis: {
        type: 'category',
        data: data.ranking_list.map(item => item.goods_name).reverse()
      },
      series: [
        {
          name: rankingType.value === 'in' ? '入库数量' : '出库数量',
          type: 'bar',
          data: data.ranking_list.map(item => item.total_quantity),
          itemStyle: {
            color: function(params) {
              const colors = ['#91cc75', '#fac858', '#ee6666', '#73c0de', '#3ba272', '#fc8452', '#9a60b4', '#ea7ccc', '#5470c6', '#eeb98b']
              return colors[params.dataIndex % colors.length]
            }
          }
        }
      ]
    }
    
    rankingChart.setOption(option, true)
  })
}

/**
 * 加载分类统计
 */
const loadCategoryStats = async () => {
  try {
    const response = await getCategoryStats({
      stats_type: categoryStatsType.value
    })
    
    categoryData.value = response.category_stats || []
    renderCategoryChart(response)
  } catch (error) {
    ElMessage.error('加载分类统计失败')
  }
}

/**
 * 渲染分类统计图表
 */
const renderCategoryChart = (data) => {
  nextTick(() => {
    if (!categoryChart) {
      categoryChart = echarts.init(categoryChartRef.value)
    }
    
    const chartData = data.category_stats.map(item => {
      const value = categoryStatsType.value === 'stock' ? item.stock_quantity : item.in_quantity
      return {
        value: value,
        name: item.category_name,
        categoryData: item
      }
    })
    
    const option = {
      tooltip: {
        trigger: 'item',
        formatter: function(params) {
          const item = params.data.categoryData
          return `
            ${item.category_name}<br />
            编码: ${item.category_code}<br />
            库存数量: ${item.stock_quantity}<br />
            入库数量: ${item.in_quantity}
          `
        }
      },
      title: {
        text: categoryStatsType.value === 'stock' ? '库存数量分布' : '入库数量分布',
        left: 'center'
      },
      legend: {
        orient: 'vertical',
        left: 'left'
      },
      series: [
        {
          name: categoryStatsType.value === 'stock' ? '库存数量' : '入库数量',
          type: 'pie',
          radius: ['40%', '70%'],
          data: chartData,
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          },
          label: {
            formatter: '{b}: {c} ({d}%)'
          }
        }
      ]
    }
    
    try {
      categoryChart.setOption(option, true)
      setTimeout(() => {
        categoryChart.resize()
      }, 100)
    } catch (error) {
      console.error('图表设置失败:', error)
    }
  })
}

/**
 * 加载物品列表（用于筛选）
 */
const loadGoodsList = async () => {
  try {
    const response = await getGoodsList({ page: 1, page_size: 1000 })
    goodsList.value = response.items || []
  } catch (error) {
    ElMessage.error('加载物品列表失败')
  }
}

/**
 * 格式化日期
 */
const formatDate = (date) => {
  const d = new Date(date)
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

/**
 * 组件卸载时销毁图表
 */
onUnmounted(() => {
  if (trendChart) {
    trendChart.dispose()
  }
  if (rankingChart) {
    rankingChart.dispose()
  }
  if (categoryChart) {
    categoryChart.dispose()
  }
})

/**
 * 组件挂载时加载数据
 */
onMounted(() => {
  loadSummary()
  loadStockTrend()
  loadGoodsRanking()
  loadCategoryStats()
  loadGoodsList()
  
  window.addEventListener('resize', () => {
    trendChart?.resize()
    rankingChart?.resize()
    categoryChart?.resize()
  })
})

/**
 * 监听趋势图时间范围变化
 */
watch(trendTimeRange, () => {
  loadStockTrend()
})

/**
 * 监听趋势图自定义日期变化
 */
watch(trendDateRange, () => {
  loadStockTrend()
})

/**
 * 监听选中物品变化
 */
watch(selectedGoodsId, () => {
  loadStockTrend()
})

/**
 * 监听排行棒类型变化
 */
watch(rankingType, () => {
  loadGoodsRanking()
})

/**
 * 监听分类统计类型变化
 */
watch(categoryStatsType, () => {
  loadCategoryStats()
})
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
  font-size: 28px;
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

.chart-controls {
  display: flex;
  align-items: center;
}

/**
 * 图表容器
 */
.chart {
  width: 100%;
  height: 350px;
}
</style>
