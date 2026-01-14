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
  <div class="statistics-view">
    <div class="summary-section">
      <div class="summary-item">
        <div class="label">物品总数</div>
        <div class="value">{{ summary.total_goods }}</div>
      </div>
      <div class="summary-item">
        <div class="label">正常物品</div>
        <div class="value text-success">{{ summary.total_goods_normal }}</div>
      </div>
      <div class="summary-item">
        <div class="label">库存总量</div>
        <div class="value">{{ summary.total_stock }}</div>
      </div>
      <div class="summary-item">
        <div class="label">今日入库</div>
        <div class="value text-success">+{{ summary.today_stock_in }}</div>
      </div>
      <div class="summary-item">
        <div class="label">今日出库</div>
        <div class="value text-warning">-{{ summary.today_stock_out }}</div>
      </div>
    </div>
    
    <div class="chart-panel full-width">
      <div class="panel-header">
        <div class="title-box">
          <h4>库存趋势分析</h4>
        </div>
        <div class="filter-box">
          <el-radio-group v-model="trendTimeRange" size="default">
            <el-radio-button value="7">近7天</el-radio-button>
            <el-radio-button value="30">近30天</el-radio-button>
            <el-radio-button value="custom">自定义</el-radio-button>
          </el-radio-group>
          <el-date-picker
            v-if="trendTimeRange === 'custom'"
            v-model="trendDateRange"
            type="daterange"
            range-separator="-"
            start-placeholder="开始"
            end-placeholder="结束"
            size="default"
            class="custom-date-picker"
          />
          <el-select
            v-model="selectedGoodsId"
            placeholder="选择物品"
            clearable
            size="default"
            class="custom-select"
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
      <div ref="trendChartRef" class="chart-container main-chart"></div>
    </div>
    
    <el-row :gutter="24" style="margin-top: 24px;">
      <el-col :span="12">
        <div class="chart-panel">
          <div class="panel-header">
            <div class="title-box">
              <h4>物品流转排名</h4>
            </div>
            <el-radio-group v-model="rankingType" size="small">
              <el-radio-button value="in">入库榜</el-radio-button>
              <el-radio-button value="out">出库榜</el-radio-button>
            </el-radio-group>
          </div>
          <div ref="rankingChartRef" class="chart-container sub-chart"></div>
        </div>
      </el-col>
      
      <el-col :span="12">
        <div class="chart-panel">
          <div class="panel-header">
            <div class="title-box">
              <h4>分类占比</h4>
            </div>
            <el-radio-group v-model="categoryStatsType" size="small">
              <el-radio-button value="stock">库存</el-radio-button>
              <el-radio-button value="in">入库</el-radio-button>
            </el-radio-group>
          </div>
          <div ref="categoryChartRef" class="chart-container sub-chart"></div>
        </div>
      </el-col>
    </el-row>
    
    <div class="chart-panel full-width" style="margin-top: 24px;" v-if="summary.warning_count > 0">
      <div class="panel-header warning-header">
        <div class="title-box">
          <h4 style="color: #ff4d4f;">库存预警</h4>
          <span class="badge">{{ summary.warning_count }}</span>
        </div>
      </div>
      <div ref="alertChartRef" class="chart-container sub-chart" v-loading="loadingAlert" style="height: 300px;"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import { getDataOverview, getStockTrend, getGoodsRanking, getCategoryStats, getStockAlert } from '@/api/statistics'
import { getGoodsList } from '@/api/goods'

const trendChartRef = ref(null)
const rankingChartRef = ref(null)
const categoryChartRef = ref(null)
const alertChartRef = ref(null)

let trendChart = null
let rankingChart = null
let categoryChart = null
let alertChart = null

const loadingAlert = ref(false)
const summary = reactive({
  total_goods: 0,
  total_stock: 0,
  today_stock_in: 0,
  today_stock_out: 0,
  warning_count: 0
})
const alertList = ref([])
const goodsList = ref([])

const trendTimeRange = ref('7')
const trendDateRange = ref([])
const selectedGoodsId = ref(0)
const handleGoodsChange = (value) => { selectedGoodsId.value = value || 0 }

const rankingType = ref('in')
const rankingData = ref([])
const categoryStatsType = ref('stock')
const categoryData = ref([])

const loadSummary = async () => {
  try {
    const response = await getDataOverview()
    Object.assign(summary, response)
  } catch (error) { ElMessage.error('加载概览失败') }
}

const loadAlertList = async () => {
  if (summary.warning_count === 0) return
  
  try {
    loadingAlert.value = true
    const response = await getStockAlert()
    alertList.value = response.alert_list || []
    renderAlertChart({ alert_list: response.alert_list, total_count: response.total_count })
  } catch (error) {
    ElMessage.error('加载预警列表失败')
  } finally {
    loadingAlert.value = false
  }
}

const renderAlertChart = (data) => {
  nextTick(() => {
    if (!alertChart) alertChart = echarts.init(alertChartRef.value)
    
    const alertItems = data.alert_list || []
    
    const option = {
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'shadow' },
        formatter: (params) => {
          const item = alertItems[params[0].dataIndex]
          const percentage = ((1 - item.current_stock / item.min_stock) * 100).toFixed(0)
          return `
            <div style="padding: 8px;">
              <div style="font-weight: bold; margin-bottom: 4px;">${item.goods_name}</div>
              <div>当前库存: ${item.current_stock} ${item.unit || ''}</div>
              <div>安全库存: ${item.min_stock} ${item.unit || ''}</div>
              <div style="color: #ff4d4f;">缺口: ${percentage}%</div>
            </div>
          `
        }
      },
      grid: { top: 5, right: 10, bottom: 20, left: 100, containLabel: true },
      xAxis: {
        type: 'value',
        name: '数量',
        nameTextStyle: { color: '#909399', fontSize: 12 },
        axisLine: { show: false },
        axisTick: { show: false },
        axisLabel: { fontSize: 12, color: '#909399' },
        splitLine: { lineStyle: { type: 'dashed', color: '#f0f0f0' } }
      },
      yAxis: {
        type: 'category',
        data: alertItems.map(item => item.goods_name),
        axisLine: { show: false },
        axisTick: { show: false },
        axisLabel: { fontSize: 13, color: '#333' }
      },
      series: [{
        type: 'bar',
        name: '当前库存',
        data: alertItems.map(item => item.current_stock),
        barWidth: 12,
        itemStyle: { color: '#ff4d4f', borderRadius: [0, 3, 3, 0] },
        label: { show: true, position: 'right', color: '#ff4d4f', formatter: '{c}', fontSize: 11 }
      }, {
        type: 'bar',
        name: '安全库存',
        data: alertItems.map(item => item.min_stock),
        barWidth: 12,
        itemStyle: { color: '#faad14d', borderRadius: [0, 3, 3, 0], opacity: 0.3 },
        label: { show: true, position: 'right', color: '#faad14d', formatter: '{c}', fontSize: 11 }
      }]
    }
    
    alertChart.setOption(option, { notMerge: true })
  })
}

const loadStockTrend = async () => {
  try {
    let startDate, endDate
    if (trendTimeRange.value === 'custom') {
      if (!trendDateRange.value || trendDateRange.value.length !== 2) return
      startDate = formatDate(trendDateRange.value[0])
      endDate = formatDate(trendDateRange.value[1])
    } else {
      const days = parseInt(trendTimeRange.value)
      const now = new Date()
      endDate = formatDate(now)
      startDate = formatDate(new Date(now.getTime() - days * 24 * 60 * 60 * 1000))
    }
    
    const params = { start_date: startDate, end_date: endDate }
    if (selectedGoodsId.value && selectedGoodsId.value !== 0) params.goods_id = selectedGoodsId.value
    
    const response = await getStockTrend(params)
    renderTrendChart(response)
  } catch (error) { ElMessage.error('加载趋势失败') }
}

const renderTrendChart = (data) => {
  nextTick(() => {
    if (!trendChart) trendChart = echarts.init(trendChartRef.value)
    
    const option = {
      tooltip: { trigger: 'axis' },
      grid: { top: 30, right: 20, bottom: 20, left: 50, containLabel: true },
      xAxis: {
        type: 'category',
        boundaryGap: false,
        data: data.trend_data?.map(item => item.date) || [],
        axisLine: { show: false },
        axisTick: { show: false },
        axisLabel: { color: '#909399' }
      },
      yAxis: {
        type: 'value',
        splitLine: { lineStyle: { type: 'dashed', color: '#f0f0f0' } }
      },
      series: [{
        name: '库存数量',
        type: 'line',
        data: data.trend_data?.map(item => item.stock_quantity) || [],
        smooth: true,
        symbol: 'none',
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(22, 119, 255, 0.2)' },
            { offset: 1, color: 'rgba(22, 119, 255, 0)' }
          ])
        },
        itemStyle: { color: '#1677ff' },
        lineStyle: { width: 3 }
      }]
    }
    trendChart.setOption(option, { notMerge: true })
  })
}

const loadGoodsRanking = async () => {
  try {
    const response = await getGoodsRanking({ ranking_type: rankingType.value, top_n: 10 })
    rankingData.value = response.ranking_list
    renderRankingChart(response)
  } catch (error) {
    ElMessage.error('加载排行失败')
  }
}

const renderRankingChart = (data) => {
  nextTick(() => {
    if (!rankingChart) rankingChart = echarts.init(rankingChartRef.value)
    
    const yAxisData = data.ranking_list.map(item => item.goods_name).reverse()
    const seriesData = data.ranking_list.map(item => item.total_quantity).reverse()
    
    const option = {
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      grid: { top: 10, right: 20, bottom: 20, left: 10, containLabel: true },
      xAxis: { type: 'value', show: false },
      yAxis: {
        type: 'category',
        data: yAxisData,
        axisLine: { show: false },
        axisTick: { show: false }
      },
      series: [{
        type: 'bar',
        data: seriesData,
        barWidth: 16,
        itemStyle: { borderRadius: [0, 8, 8, 0], color: '#4096ff' },
        label: { show: true, position: 'right' }
      }]
    }
    
    rankingChart.setOption(option, { notMerge: true })
  })
}

const loadCategoryStats = async () => {
  try {
    const response = await getCategoryStats({ stats_type: categoryStatsType.value })
    categoryData.value = response.category_stats || []
    renderCategoryChart(response)
  } catch (error) { ElMessage.error('加载分类统计失败') }
}

const renderCategoryChart = (data) => {
  nextTick(() => {
    if (!categoryChart) categoryChart = echarts.init(categoryChartRef.value)
    const chartData = data.category_stats.map(item => ({
      value: categoryStatsType.value === 'stock' ? item.stock_quantity : item.in_quantity,
      name: item.category_name
    }))
    
    const option = {
      tooltip: { trigger: 'item' },
      legend: { orient: 'vertical', left: 'left', type: 'scroll' },
      series: [{
        type: 'pie',
        radius: ['50%', '70%'],
        center: ['60%', '50%'],
        avoidLabelOverlap: false,
        itemStyle: { borderRadius: 10, borderColor: '#fff', borderWidth: 2 },
        label: { show: false },
        emphasis: { label: { show: true, fontSize: 14, fontWeight: 'bold' } },
        data: chartData
      }]
    }
    categoryChart.setOption(option)
  })
}

const loadGoodsList = async () => {
  try {
    const response = await getGoodsList({ page: 1, page_size: 20 })
    goodsList.value = response.items || []
  } catch (error) { ElMessage.error('加载物品列表失败') }
}

const formatDate = (date) => {
  const d = new Date(date)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

onUnmounted(() => {
  if (trendChart) trendChart.dispose()
  if (rankingChart) rankingChart.dispose()
  if (categoryChart) categoryChart.dispose()
  if (alertChart) alertChart.dispose()
})

onMounted(() => {
  loadSummary().then(() => {
    loadAlertList()
  })
  loadStockTrend()
  loadGoodsRanking()
  loadCategoryStats()
  loadGoodsList()
  window.addEventListener('resize', () => {
    trendChart?.resize()
    rankingChart?.resize()
    categoryChart?.resize()
    alertChart?.resize()
  })
})

watch([trendTimeRange, trendDateRange, selectedGoodsId], loadStockTrend)
watch(rankingType, loadGoodsRanking)
watch(categoryStatsType, loadCategoryStats)
watch(() => summary.warning_count, () => loadAlertList())
</script>

<style scoped>
.statistics-view {
  max-width: 1600px;
  margin: 0 auto;
}

/* 顶部概览条 */
.summary-section {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 24px;
  margin-bottom: 24px;
}

.summary-item {
  background: #fff;
  padding: 24px;
  border-radius: 8px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.03);
  border: 1px solid #f0f0f0;
}

.summary-item .label {
  font-size: 14px;
  color: #8c8c8c;
  margin-bottom: 8px;
}

.summary-item .value {
  font-size: 32px;
  font-weight: 600;
  color: #1f1f1f;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto;
}

.text-success { color: #52c41a !important; }
.text-warning { color: #faad14 !important; }

/* 图表容器面板 */
.chart-panel {
  background: #fff;
  border-radius: 8px;
  padding: 24px;
  border: 1px solid #f0f0f0;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.title-box h4 {
  font-size: 16px;
  font-weight: 600;
  color: #1f1f1f;
  position: relative;
  padding-left: 12px;
}

.title-box h4::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 16px;
  background: #1677ff;
  border-radius: 2px;
}

.filter-box {
  display: flex;
  gap: 12px;
}

.custom-date-picker { width: 240px; }
.custom-select { width: 160px; }

.chart-container { width: 100%; }
.main-chart { height: 350px; }
.sub-chart { height: 300px; }

/* 徽标 */
.badge {
  background: #fff1f0;
  color: #ff4d4f;
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 10px;
  border: 1px solid #ffa39e;
  margin-left: 8px;
  vertical-align: middle;
}
</style>