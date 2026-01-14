/**
 * CampusAssetManager/frontend/src/views/SettingsView.vue
 * 系统设置页面
 * 
 * 功能说明：
 * - 系统配置管理
 * - 系统重置功能
 *
 * 作者：CampusAssetManager开发团队
 * 日期：2026-01-13
 */

<template>
    <div class="settings-container">
      <!-- 系统配置卡片列表 -->
      <el-card v-for="group in configGroups" :key="group.category" style="margin-bottom: 20px;">
        <template #header>
          <div class="card-header">
            <span>{{ group.category_name }}</span>
          </div>
        </template>
        
        <el-form :model="configForm" label-width="150px">
          <el-form-item
            v-for="config in group.configs"
            :key="config.config_id"
            :label="config.config_name"
          >
            <!-- 字符串类型 -->
            <el-input
              v-if="config.config_type === 'string'"
              v-model="configForm[config.config_key]"
              :placeholder="'请输入' + config.config_name"
            />
            
            <!-- 数字类型 -->
            <el-input-number
              v-else-if="config.config_type === 'number'"
              v-model="configForm[config.config_key]"
              :min="0"
            />
            
            <!-- 布尔类型 -->
            <el-switch
              v-else-if="config.config_type === 'boolean'"
              v-model="configForm[config.config_key]"
            />
            
            <!-- JSON类型 -->
            <el-input
              v-else-if="config.config_type === 'json'"
              v-model="configForm[config.config_key]"
              type="textarea"
              :placeholder="'请输入' + config.config_name + '（JSON格式）'"
            />
          </el-form-item>
        </el-form>
      </el-card>
      
      <div style="text-align: right; margin-top: 20px; display: flex; gap: 10px; justify-content: flex-end;">
        <el-button type="primary" @click="handleSaveConfig" :loading="loading">保存配置</el-button>
        <el-button type="danger" @click="handleResetClick" :loading="resetLoading">系统重置</el-button>
      </div>
    </div>
    
    <!-- 系统重置确认对话框 -->
    <el-dialog
      v-model="resetDialogVisible"
      title="系统重置"
      width="400px"
      :close-on-click-modal="false"
    >
      <el-alert
        title="危险操作警告"
        type="error"
        :closable="false"
        style="margin-bottom: 20px;"
      >
        <template #default>
          <div>系统重置将清空所有数据，包括：</div>
          <div>• 物品分类和物品信息</div>
          <div>• 库存数据</div>
          <div>• 出入库记录</div>
          <div>• 盘点记录</div>
          <div>• 操作日志</div>
          <div>• 系统配置（将恢复默认配置）</div>
          <div style="margin-top: 10px; font-weight: bold;">此操作不可逆，请谨慎操作！</div>
        </template>
      </el-alert>
      
      <el-form :model="resetForm" label-width="100px">
        <el-form-item label="管理员密码">
          <el-input
            v-model="resetForm.password"
            type="password"
            placeholder="请输入管理员密码"
            show-password
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="resetDialogVisible = false">取消</el-button>
          <el-button type="danger" @click="handleConfirmReset" :loading="resetLoading">确认重置</el-button>
        </span>
      </template>
    </el-dialog>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getConfigs, updateConfig, resetSystem } from '@/api'

/**
 * 路由实例
 */
const router = useRouter()

/**
 * 配置分组列表
 */
const configGroups = ref([])

/**
 * 配置表单（按config_key组织）
 */
const configForm = reactive({})

/**
 * 加载状态
 */
const loading = ref(false)

/**
 * 重置对话框可见性
 */
const resetDialogVisible = ref(false)

/**
 * 重置加载状态
 */
const resetLoading = ref(false)

/**
 * 重置表单
 */
const resetForm = reactive({
  password: ''
})

/**
 * 加载系统配置
 */
const loadConfig = async () => {
  try {
    const response = await getConfigs()
    // 过滤掉库存配置模块（category为'stock'）
    configGroups.value = response.configs.filter(group => group.category !== 'stock')
    
    // 将配置值绑定到configForm
    Object.keys(configForm).forEach(key => delete configForm[key])
    
    configGroups.value.forEach(group => {
      group.configs.forEach(config => {
        // 根据类型转换值
        if (config.config_type === 'number') {
          configForm[config.config_key] = Number(config.config_value)
        } else if (config.config_type === 'boolean') {
          configForm[config.config_key] = config.config_value === 'true'
        } else {
          configForm[config.config_key] = config.config_value
        }
      })
    })
  } catch (error) {
    console.error('加载系统配置失败:', error)
    ElMessage.error('加载系统配置失败')
  }
}

/**
 * 处理保存配置
 */
const handleSaveConfig = async () => {
  try {
    loading.value = true
    
    // 构建批量更新请求数据
    const configs = []
    
    configGroups.value.forEach(group => {
      group.configs.forEach(config => {
        const newValue = String(configForm[config.config_key])
        
        configs.push({
          config_key: config.config_key,
          config_value: newValue
        })
      })
    })
    
    await updateConfig({ configs })
    ElMessage.success('配置保存成功')
  } catch (error) {
    console.error('保存配置失败:', error)
    ElMessage.error('配置保存失败')
  } finally {
    loading.value = false
  }
}

/**
 * 处理重置按钮点击
 */
const handleResetClick = () => {
  resetForm.password = ''
  resetDialogVisible.value = true
}

/**
 * 处理确认重置
 */
const handleConfirmReset = async () => {
  if (!resetForm.password) {
    ElMessage.warning('请输入管理员密码')
    return
  }
  
  try {
    resetLoading.value = true
    
    await resetSystem({
      password: resetForm.password
    })
    
    ElMessage.success('系统重置成功')
    resetDialogVisible.value = false
    
    // 跳转到首页
    router.push('/home')
  } catch (error) {
    console.error('系统重置失败:', error)
    const errorMessage = error.response?.data?.detail || error.message || '系统重置失败'
    
    if (errorMessage.includes('密码')) {
      ElMessage.error('密码错误，重置操作被拒绝')
    } else {
      ElMessage.error(errorMessage)
    }
  } finally {
    resetLoading.value = false
  }
}

/**
 * 组件挂载时加载数据
 */
onMounted(() => {
  loadConfig()
})
</script>

<!-- 强制 Vite 重新编译 -->
<style scoped>
.settings-container {
  padding: 20px;
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
 * 对话框底部按钮
 */
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>