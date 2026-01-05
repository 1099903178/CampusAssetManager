/**
 * CampusAssetManager/frontend/src/components/common/TableComponent.vue
 * 通用表格组件
 * 
 * 功能说明：
 * - 提供通用的表格展示功能
 * - 支持分页、排序、筛选
 * - 支持多选、行高亮
 * - 支持自定义列
 * 
 * 作者：CampusAssetManager开发团队
 * 日期：2026-01-05
 */

<template>
  <div class="table-container">
    <!-- 工具栏 -->
    <div class="table-toolbar" v-if="showToolbar">
      <slot name="toolbar"></slot>
    </div>
    
    <!-- 表格 -->
    <el-table
      ref="tableRef"
      :data="tableData"
      :stripe="stripe"
      :border="border"
      :height="height"
      :max-height="maxHeight"
      :highlight-current-row="highlightCurrentRow"
      :show-overflow-tooltip="showOverflowTooltip"
      :row-key="rowKey"
      @selection-change="handleSelectionChange"
      @sort-change="handleSortChange"
      @filter-change="handleFilterChange"
      v-loading="loading"
    >
      <!-- 序号列 -->
      <el-table-column
        v-if="showIndex"
        type="index"
        label="序号"
        width="60"
        align="center"
        :index="indexMethod"
      />
      
      <!-- 选择列 -->
      <el-table-column
        v-if="showSelection"
        type="selection"
        width="55"
        align="center"
      />
      
      <!-- 自定义列 -->
      <slot name="columns"></slot>
    </el-table>
    
    <!-- 分页 -->
    <div class="table-pagination" v-if="showPagination">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="pageSizes"
        :total="total"
        :layout="paginationLayout"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

/**
 * 定义 Props
 */
const props = defineProps({
  /**
   * 表格数据
   */
  data: {
    type: Array,
    default: () => []
  },
  /**
   * 是否显示斑马纹
   */
  stripe: {
    type: Boolean,
    default: true
  },
  /**
   * 是否显示边框
   */
  border: {
    type: Boolean,
    default: true
  },
  /**
   * 表格高度
   */
  height: {
    type: [String, Number],
    default: null
  },
  /**
   * 最大高度
   */
  maxHeight: {
    type: [String, Number],
    default: null
  },
  /**
   * 是否高亮当前行
   */
  highlightCurrentRow: {
    type: Boolean,
    default: true
  },
  /**
   * 是否显示工具栏
   */
  showToolbar: {
    type: Boolean,
    default: false
  },
  /**
   * 是否显示序号
   */
  showIndex: {
    type: Boolean,
    default: true
  },
  /**
   * 是否显示选择框
   */
  showSelection: {
    type: Boolean,
    default: false
  },
  /**
   * 是否显示溢出提示
   */
  showOverflowTooltip: {
    type: Boolean,
    default: true
  },
  /**
   * 行数据的 Key（用于 row-key 属性）
   */
  rowKey: {
    type: String,
    default: 'id'
  },
  /**
   * 是否显示分页
   */
  showPagination: {
    type: Boolean,
    default: true
  },
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
   */
  paginationLayout: {
    type: String,
    default: 'total, sizes, prev, pager, next, jumper'
  },
  /**
   * 是否加载中
   */
  loading: {
    type: Boolean,
    default: false
  }
})

/**
 * 定义 Emits
 */
const emit = defineEmits([
  'selection-change',
  'sort-change',
  'filter-change',
  'size-change',
  'current-change',
  'update:page',
  'update:limit'
])

/**
 * 表格引用
 */
const tableRef = ref(null)

/**
 * 表格数据（响应式）
 */
const tableData = computed(() => props.data)

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
 * 计算序号
 * 
 * @param {number} index - 索引
 * @returns {number} 序号
 */
const indexMethod = (index) => {
  return (props.page - 1) * props.limit + index + 1
}

/**
 * 处理选择变化
 * 
 * @param {Array} selection - 选中的行
 */
const handleSelectionChange = (selection) => {
  emit('selection-change', selection)
}

/**
 * 处理排序变化
 * 
 * @param {Object} column - 列对象
 * @param {string} prop - 排序属性
 * @param {string} order - 排序方式
 */
const handleSortChange = ({ column, prop, order }) => {
  emit('sort-change', { column, prop, order })
}

/**
 * 处理筛选变化
 * 
 * @param {Object} filters - 筛选条件
 */
const handleFilterChange = (filters) => {
  emit('filter-change', filters)
}

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

/**
 * 清除选择
 */
const clearSelection = () => {
  tableRef.value?.clearSelection()
}

/**
 * 切换某一行选中状态
 * 
 * @param {Object} row - 行数据
 * @param {boolean} selected - 是否选中
 */
const toggleRowSelection = (row, selected) => {
  tableRef.value?.toggleRowSelection(row, selected)
}

/**
 * 切换所有行选中状态
 * 
 * @param {boolean} selected - 是否选中
 */
const toggleAllSelection = (selected) => {
  tableRef.value?.toggleAllSelection()
}

/**
 * 暴露方法
 */
defineExpose({
  clearSelection,
  toggleRowSelection,
  toggleAllSelection
})
</script>

<style scoped>
/**
 * 表格容器
 */
.table-container {
  display: flex;
  flex-direction: column;
  height: 100%;
}

/**
 * 工具栏
 */
.table-toolbar {
  margin-bottom: 16px;
}

/**
 * 分页容器
 */
.table-pagination {
  display: flex;
  justify-content: flex-end;
  padding: 16px 0;
  background-color: #fff;
}
</style>