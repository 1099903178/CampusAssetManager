/**
 * CampusAssetManager/frontend/src/components/common/PaginationComponent.vue
 * 通用分页组件
 * 
 * 功能说明：
 * - 提供通用的分页功能
 * - 支持跳转页码、改变每页数量
 * - 显示总记录数
 * - 支持布局自定义
 * 
 * 作者：CampusAssetManager开发团队
 * 日期：2026-01-05
 */

<template>
  <div class="pagination-container">
    <el-pagination
      v-model:current-page="currentPage"
      v-model:page-size="pageSize"
      :page-sizes="pageSizes"
      :total="total"
      :layout="layout"
      :background="background"
      :hide-on-single-page="hideOnSinglePage"
      @size-change="handleSizeChange"
      @current-change="handleCurrentChange"
    />
  </div>
</template>

<script setup>
import { computed } from 'vue'

/**
 * 定义 Props
 */
const props = defineProps({
  /**
   * 当前页码
   */
  page: {
    type: Number,
    default: 1
  },
  /**
   * 每页数量
   */
  limit: {
    type: Number,
    default: 20
  },
  /**
   * 总记录数
   */
  total: {
    type: Number,
    default: 0
  },
  /**
   * 每页显示数量选择器的选项
   */
  pageSizes: {
    type: Array,
    default: () => [10, 20, 50, 100]
  },
  /**
   * 分页布局
   * 可选值：total, sizes, prev, pager, next, jumper
   */
  layout: {
    type: String,
    default: 'total, sizes, prev, pager, next, jumper'
  },
  /**
   * 是否显示背景色
   */
  background: {
    type: Boolean,
    default: true
  },
  /**
   * 只有一页时是否隐藏
   */
  hideOnSinglePage: {
    type: Boolean,
    default: false
  }
})

/**
 * 定义 Emits
 */
const emit = defineEmits([
  'size-change',
  'current-change',
  'update:page',
  'update:limit'
])

/**
 * 当前页码（双向绑定）
 */
const currentPage = computed({
  get: () => props.page,
  set: (val) => {
    emit('update:page', val)
  }
})

/**
 * 每页数量（双向绑定）
 */
const pageSize = computed({
  get: () => props.limit,
  set: (val) => {
    emit('update:limit', val)
  }
})

/**
 * 处理每页数量变化
 * 
 * @param {number} val - 每页数量
 */
const handleSizeChange = (val) => {
  emit('size-change', val)
}

/**
 * 处理页码变化
 * 
 * @param {number} val - 页码
 */
const handleCurrentChange = (val) => {
  emit('current-change', val)
  emit('update:page', val)
}
</script>

<style scoped>
/**
 * 分页容器
 */
.pagination-container {
  display: flex;
  justify-content: flex-end;
  padding: 16px 0;
}
</style>