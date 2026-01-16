/**
 * CampusAssetManager/frontend/src/views/DatabaseView.vue
 * 数据库管理页面
 * 
 * 功能说明：
 * - 数据库备份
 * - 备份文件管理（查看列表、下载、删除）
 * - 数据库恢复
 *
 * 作者：CampusAssetManager开发团队
 * 日期：2026-01-14
 */

<template>
  <div class="database-container">
    <!-- 数据库备份卡片 -->
    <el-card style="margin-bottom: 20px;">
      <template #header>
        <div class="card-header">
          <span>数据备份</span>
        </div>
      </template>
      
      <el-alert
        title="备份说明"
        type="info"
        :closable="false"
        style="margin-bottom: 20px;"
      >
        <template #default>
          <div>• 备份文件将保存为：campus_asset_backup_YYYYMMDD_HHMMSS.db</div>
          <div>• 备份文件存储在服务器端</div>
          <div>• 建议定期备份数据库以保证数据安全</div>
        </template>
      </el-alert>
      
      <el-button type="primary" @click="handleCreateBackup" :loading="createLoading" size="large">
        <el-icon><Download /></el-icon>
        创建备份
      </el-button>
    </el-card>
    
    <!-- 备份文件列表卡片 -->
    <el-card style="margin-bottom: 20px;">
      <template #header>
        <div class="card-header">
          <span>备份文件列表</span>
          <el-button type="primary" size="small" @click="handleLoadBackups" :loading="listLoading">
            <el-icon><Refresh /></el-icon>
            刷新列表
          </el-button>
        </div>
      </template>
      
      <el-table
        :data="backupList"
        stripe
        style="width: 100%"
        v-loading="listLoading"
      >
        <el-table-column prop="filename" label="文件名" min-width="250" fixed>
          <template #default="{ row }">
            <el-icon><Document /></el-icon>
            {{ row.filename }}
          </template>
        </el-table-column>
        
        <el-table-column prop="create_time" label="创建时间" width="180">
          <template #default="{ row }">
            {{ row.create_time }}
          </template>
        </el-table-column>
        
        <el-table-column prop="size_human" label="文件大小" width="120">
          <template #default="{ row }">
            {{ row.size_human }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              @click="handleDownloadBackup(row.filename)"
            >
              <el-icon><Download /></el-icon>
              下载
            </el-button>
            <el-button
              type="warning"
              size="small"
              @click="handleRestoreClick(row)"
            >
              <el-icon><Upload /></el-icon>
              恢复
            </el-button>
            <el-button
              type="danger"
              size="small"
              @click="handleDeleteBackup(row)"
            >
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <el-empty v-if="backupList.length === 0" description="暂无备份文件" />
    </el-card>
    
    <!-- 恢复确认对话框 -->
    <el-dialog
      v-model="restoreDialogVisible"
      title="数据恢复"
      width="400px"
      :close-on-click-modal="false"
    >
      <el-alert
        title="重要提示"
        type="warning"
        :closable="false"
        style="margin-bottom: 20px;"
      >
        <template #default>
          <div>数据恢复操作将用备份文件替换当前数据库</div>
          <div>• 恢复前会自动创建当前数据库的备份</div>
          <div>• 恢复操作不可逆，请谨慎操作</div>
          <div>• 建议先下载当前备份文件后再进行恢复</div>
        </template>
      </el-alert>
      
      <el-form :model="restoreForm" label-width="100px">
        <el-form-item label="备份文件">
          <el-input v-model="restoreForm.filename" disabled />
        </el-form-item>
        <el-form-item label="管理员密码">
          <el-input
            v-model="restoreForm.password"
            type="password"
            placeholder="请输入管理员密码"
            show-password
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="restoreDialogVisible = false">取消</el-button>
          <el-button type="warning" @click="handleConfirmRestore" :loading="restoreLoading">确认恢复</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { createBackup, getBackupList, downloadBackup, deleteBackup, restoreDatabase } from '@/api'
import { useUserStore } from '@/stores'

/**
 * 路由实例
 */
const router = useRouter()

/**
 * 用户Store
 */
const userStore = useUserStore()

/**
 * 备份列表
 */
const backupList = ref([])

/**
 * 创建备份加载状态
 */
const createLoading = ref(false)

/**
 * 列表加载状态
 */
const listLoading = ref(false)

/**
 * 恢复对话框可见性
 */
const restoreDialogVisible = ref(false)

/**
 * 恢复加载状态
 */
const restoreLoading = ref(false)

/**
 * 恢复表单
 */
const restoreForm = reactive({
  filename: '',
  password: ''
})

/**
 * 加载备份列表
 */
const handleLoadBackups = async () => {
  try {
    listLoading.value = true
    const response = await getBackupList()
    backupList.value = response.backups
  } catch (error) {
    console.error('加载备份列表失败:', error)
    ElMessage.error('加载备份列表失败')
  } finally {
    listLoading.value = false
  }
}

/**
 * 处理创建备份
 */
const handleCreateBackup = async () => {
  try {
    createLoading.value = true
    await createBackup()
    ElMessage.success('备份创建成功')
    // 刷新备份列表
    await handleLoadBackups()
  } catch (error) {
    console.error('创建备份失败:', error)
    ElMessage.error('创建备份失败')
  } finally {
    createLoading.value = false
  }
}

/**
 * 处理下载备份
 */
const handleDownloadBackup = async (filename) => {
  try {
    const response = await downloadBackup(filename)
    
    // 创建Blob URL并触发下载
    const url = window.URL.createObjectURL(new Blob([response]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', filename)
    document.body.appendChild(link)
    link.click()
    
    // 清理
    link.remove()
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('文件下载成功')
  } catch (error) {
    console.error('下载备份失败:', error)
    ElMessage.error('下载备份失败')
  }
}

/**
 * 处理删除备份
 */
const handleDeleteBackup = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除备份文件 "${row.filename}" 吗？此操作不可逆。`,
      '删除确认',
      {
        type: 'warning',
        confirmButtonText: '确认删除',
        cancelButtonText: '取消'
      }
    )
    
    await deleteBackup(row.filename)
    ElMessage.success('删除成功')
    // 刷新备份列表
    await handleLoadBackups()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除备份失败:', error)
      ElMessage.error('删除备份失败')
    }
  }
}

/**
 * 处理恢复按钮点击
 */
const handleRestoreClick = (row) => {
  restoreForm.filename = row.filename
  restoreForm.password = ''
  restoreDialogVisible.value = true
}

/**
 * 处理确认恢复
 */
const handleConfirmRestore = async () => {
  if (!restoreForm.password) {
    ElMessage.warning('请输入管理员密码')
    return
  }
  
  try {
    restoreLoading.value = true
    
    await restoreDatabase({
      filename: restoreForm.filename,
      password: restoreForm.password
    })
    
    // 清除登录状态
    await userStore.logout()
    
    ElMessage.success('数据恢复成功，请重新登录')
    restoreDialogVisible.value = false
    
    // 跳转到登录页
    router.push('/login')
  } catch (error) {
    console.error('数据恢复失败:', error)
    const errorMessage = error.response?.data?.detail || error.message || '数据恢复失败'
    
    if (errorMessage.includes('密码')) {
      ElMessage.error('密码错误，恢复操作被拒绝')
    } else {
      ElMessage.error('数据恢复失败')
    }
  } finally {
    restoreLoading.value = false
  }
}

/**
 * 组件挂载时加载备份列表
 * 使用nextTick确保组件完全渲染后再加载数据
 */
onMounted(() => {
  nextTick(() => {
    handleLoadBackups()
  })
})
</script>

<style scoped>
.database-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header span {
  font-size: 16px;
  font-weight: bold;
}

.el-icon {
  margin-right: 5px;
}
</style>