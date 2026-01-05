/**
 * CampusAssetManager/frontend/src/components/common/FormComponent.vue
 * 通用表单组件
 * 
 * 功能说明：
 * - 提供通用的表单功能
 * - 支持多种表单控件类型
 * - 支持表单验证
 * - 支持自定义布局
 * 
 * 作者：CampusAssetManager开发团队
 * 日期：2026-01-05
 */

<template>
  <div class="form-container">
    <el-form
      ref="formRef"
      :model="formData"
      :rules="formRules"
      :label-width="labelWidth"
      :label-position="labelPosition"
      :disabled="disabled"
      :inline="inline"
    >
      <!-- 动态渲染表单项 -->
      <el-form-item
        v-for="item in formItems"
        :key="item.prop"
        :label="item.label"
        :prop="item.prop"
        :required="item.required"
      >
        <!-- 输入框 -->
        <el-input
          v-if="item.type === 'input'"
          v-model="formData[item.prop]"
          :placeholder="item.placeholder"
          :type="item.inputType || 'text'"
          :maxlength="item.maxlength"
          :show-word-limit="item.showWordLimit"
          :disabled="item.disabled"
          :clearable="item.clearable !== false"
          @input="handleInput(item.prop, $event)"
        />
        
        <!-- 文本域 -->
        <el-input
          v-else-if="item.type === 'textarea'"
          v-model="formData[item.prop]"
          type="textarea"
          :placeholder="item.placeholder"
          :rows="item.rows || 4"
          :maxlength="item.maxlength"
          :show-word-limit="item.showWordLimit"
          :disabled="item.disabled"
          :clearable="item.clearable !== false"
          @input="handleInput(item.prop, $event)"
        />
        
        <!-- 数字输入框 -->
        <el-input-number
          v-else-if="item.type === 'number'"
          v-model="formData[item.prop]"
          :min="item.min"
          :max="item.max"
          :step="item.step || 1"
          :precision="item.precision || 0"
          :disabled="item.disabled"
          :controls="item.controls !== false"
          @change="handleChange(item.prop, $event)"
        />
        
        <!-- 选择器 -->
        <el-select
          v-else-if="item.type === 'select'"
          v-model="formData[item.prop]"
          :placeholder="item.placeholder"
          :multiple="item.multiple"
          :clearable="item.clearable !== false"
          :disabled="item.disabled"
          :collapse-tags="item.collapseTags"
          :filterable="item.filterable"
          @change="handleChange(item.prop, $event)"
        >
          <el-option
            v-for="option in item.options"
            :key="option.value"
            :label="option.label"
            :value="option.value"
            :disabled="option.disabled"
          />
        </el-select>
        
        <!-- 日期选择器 -->
        <el-date-picker
          v-else-if="item.type === 'date'"
          v-model="formData[item.prop]"
          type="date"
          :placeholder="item.placeholder"
          :format="item.format || 'YYYY-MM-DD'"
          :value-format="item.valueFormat || 'YYYY-MM-DD'"
          :disabled="item.disabled"
          :clearable="item.clearable !== false"
          @change="handleChange(item.prop, $event)"
        />
        
        <!-- 日期时间选择器 -->
        <el-date-picker
          v-else-if="item.type === 'datetime'"
          v-model="formData[item.prop]"
          type="datetime"
          :placeholder="item.placeholder"
          :format="item.format || 'YYYY-MM-DD HH:mm:ss'"
          :value-format="item.valueFormat || 'YYYY-MM-DD HH:mm:ss'"
          :disabled="item.disabled"
          :clearable="item.clearable !== false"
          @change="handleChange(item.prop, $event)"
        />
        
        <!-- 时间选择器 -->
        <el-time-picker
          v-else-if="item.type === 'time'"
          v-model="formData[item.prop]"
          :placeholder="item.placeholder"
          :format="item.format || 'HH:mm:ss'"
          :value-format="item.valueFormat || 'HH:mm:ss'"
          :disabled="item.disabled"
          :clearable="item.clearable !== false"
          @change="handleChange(item.prop, $event)"
        />
        
        <!-- 级联选择器 -->
        <el-cascader
          v-else-if="item.type === 'cascader'"
          v-model="formData[item.prop]"
          :options="item.options"
          :props="item.props"
          :placeholder="item.placeholder"
          :clearable="item.clearable !== false"
          :disabled="item.disabled"
          :filterable="item.filterable"
          @change="handleChange(item.prop, $event)"
        />
        
        <!-- 单选框 -->
        <el-radio-group
          v-else-if="item.type === 'radio'"
          v-model="formData[item.prop]"
          :disabled="item.disabled"
          @change="handleChange(item.prop, $event)"
        >
          <el-radio
            v-for="option in item.options"
            :key="option.value"
            :label="option.value"
            :disabled="option.disabled"
          >
            {{ option.label }}
          </el-radio>
        </el-radio-group>
        
        <!-- 复选框 -->
        <el-checkbox-group
          v-else-if="item.type === 'checkbox'"
          v-model="formData[item.prop]"
          :disabled="item.disabled"
          @change="handleChange(item.prop, $event)"
        >
          <el-checkbox
            v-for="option in item.options"
            :key="option.value"
            :label="option.value"
            :disabled="option.disabled"
          >
            {{ option.label }}
          </el-checkbox>
        </el-checkbox-group>
        
        <!-- 开关 -->
        <el-switch
          v-else-if="item.type === 'switch'"
          v-model="formData[item.prop]"
          :disabled="item.disabled"
          @change="handleChange(item.prop, $event)"
        />
        
        <!-- 滑块 -->
        <el-slider
          v-else-if="item.type === 'slider'"
          v-model="formData[item.prop]"
          :min="item.min || 0"
          :max="item.max || 100"
          :step="item.step || 1"
          :disabled="item.disabled"
          @change="handleChange(item.prop, $event)"
        />
        
        <!-- 自定义插槽 -->
        <slot
          v-else-if="item.type === 'slot'"
          :name="item.prop"
          :item="item"
          :value="formData[item.prop]"
          :form="formData"
        />
      </el-form-item>
      
      <!-- 表单操作按钮 -->
      <el-form-item v-if="showButtons">
        <el-button
          v-if="showSubmit"
          type="primary"
          :loading="loading"
          @click="handleSubmit"
        >
          {{ submitText }}
        </el-button>
        
        <el-button
          v-if="showReset"
          @click="handleReset"
        >
          {{ resetText }}
        </el-button>
        
        <el-button
          v-if="showCancel"
          @click="handleCancel"
        >
          {{ cancelText }}
        </el-button>
        
        <!-- 自定义按钮插槽 -->
        <slot name="buttons"></slot>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

/**
 * 定义 Props
 */
const props = defineProps({
  /**
   * 表单数据
   */
  modelValue: {
    type: Object,
    default: () => ({})
  },
  /**
   * 表单项配置
   */
  items: {
    type: Array,
    default: () => []
  },
  /**
   * 表单验证规则
   */
  rules: {
    type: Object,
    default: () => ({})
  },
  /**
   * 标签宽度
   */
  labelWidth: {
    type: String,
    default: '100px'
  },
  /**
   * 标签位置
   */
  labelPosition: {
    type: String,
    default: 'right'
  },
  /**
   * 是否禁用
   */
  disabled: {
    type: Boolean,
    default: false
  },
  /**
   * 是否行内表单
   */
  inline: {
    type: Boolean,
    default: false
  },
  /**
   * 是否显示操作按钮
   */
  showButtons: {
    type: Boolean,
    default: true
  },
  /**
   * 是否显示提交按钮
   */
  showSubmit: {
    type: Boolean,
    default: true
  },
  /**
   * 是否显示重置按钮
   */
  showReset: {
    type: Boolean,
    default: true
  },
  /**
   * 是否显示取消按钮
   */
  showCancel: {
    type: Boolean,
    default: false
  },
  /**
   * 提交按钮文本
   */
  submitText: {
    type: String,
    default: '提交'
  },
  /**
   * 重置按钮文本
   */
  resetText: {
    type: String,
    default: '重置'
  },
  /**
   * 取消按钮文本
   */
  cancelText: {
    type: String,
    default: '取消'
  },
  /**
   * 提交按钮加载状态
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
  'update:modelValue',
  'submit',
  'reset',
  'cancel',
  'input',
  'change'
])

/**
 * 表单引用
 */
const formRef = ref(null)

/**
 * 表单数据（响应式）
 */
const formData = computed({
  get: () => props.modelValue,
  set: (val) => {
    emit('update:modelValue', val)
  }
})

/**
 * 表单项配置
 */
const formItems = computed(() => props.items)

/**
 * 表单验证规则
 */
const formRules = computed(() => props.rules)

/**
 * 处理输入事件
 * 
 * @param {string} prop - 字段属性
 * @param {any} value - 输入值
 */
const handleInput = (prop, value) => {
  emit('input', prop, value)
}

/**
 * 处理变化事件
 * 
 * @param {string} prop - 字段属性
 * @param {any} value - 变化值
 */
const handleChange = (prop, value) => {
  emit('change', prop, value)
}

/**
 * 处理提交
 */
const handleSubmit = () => {
  formRef.value?.validate((valid) => {
    if (valid) {
      emit('submit', formData.value)
    } else {
      return false
    }
  })
}

/**
 * 处理重置
 */
const handleReset = () => {
  formRef.value?.resetFields()
  emit('reset')
}

/**
 * 处理取消
 */
const handleCancel = () => {
  emit('cancel')
}

/**
 * 验证表单
 * 
 * @param {Function} callback - 回调函数
 */
const validate = (callback) => {
  return formRef.value?.validate(callback)
}

/**
 * 验证指定字段
 * 
 * @param {string} props - 字段属性
 * @param {Function} callback - 回调函数
 */
const validateField = (props, callback) => {
  return formRef.value?.validateField(props, callback)
}

/**
 * 重置表单
 */
const resetFields = () => {
  formRef.value?.resetFields()
}

/**
 * 清除验证
 */
const clearValidate = () => {
  formRef.value?.clearValidate()
}

/**
 * 暴露方法
 */
defineExpose({
  validate,
  validateField,
  resetFields,
  clearValidate
})
</script>

<style scoped>
/**
 * 表单容器
 */
.form-container {
  width: 100%;
}
</style>