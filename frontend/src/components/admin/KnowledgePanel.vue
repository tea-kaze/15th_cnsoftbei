<template>
  <div class="knowledge-panel">
    <!-- 上传区域 -->
    <el-card shadow="hover" class="upload-card">
      <template #header>
        <span><el-icon><Upload /></el-icon> 上传知识文档</span>
      </template>
      <el-upload
        ref="uploadRef"
        :action="uploadUrl"
        :accept="'.txt,.pdf,.docx'"
        :limit="10"
        :on-success="onUploadSuccess"
        :on-error="onUploadError"
        :before-upload="beforeUpload"
        drag
        name="file"
      >
        <el-icon class="upload-icon"><UploadFilled /></el-icon>
        <div class="upload-text">将文件拖到此处，或<em>点击上传</em></div>
        <template #tip>
          <div class="upload-tip">支持 .txt / .pdf / .docx 格式的知识文档</div>
        </template>
      </el-upload>
    </el-card>

    <!-- 文档列表 -->
    <el-card shadow="hover" class="list-card">
      <template #header>
        <span>
          <el-icon><FolderOpened /></el-icon>
          知识库文档列表（共 {{ documents.length }} 个）
        </span>
        <el-button text type="primary" @click="loadDocuments" style="float:right">
          <el-icon><Refresh /></el-icon> 刷新
        </el-button>
      </template>

      <el-table :data="documents" stripe v-loading="loading" empty-text="暂无文档">
        <el-table-column prop="name" label="文件名" min-width="300" show-overflow-tooltip />
        <el-table-column prop="chunks" label="知识块数" width="120" align="center" />
        <el-table-column label="操作" width="140" align="center">
          <template #default="{ row }">
            <el-popconfirm
              title="确定删除该文档及其知识块吗？"
              confirm-button-text="删除"
              cancel-button-text="取消"
              @confirm="deleteDocument(row.name)"
            >
              <template #reference>
                <el-button type="danger" size="small" text>
                  <el-icon><Delete /></el-icon> 删除
                </el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Upload, UploadFilled, FolderOpened, Refresh, Delete } from '@element-plus/icons-vue'
import api from '../../api/chat'

const uploadUrl = '/api/knowledge/upload'
const documents = ref([])
const loading = ref(false)
const uploadRef = ref(null)

async function loadDocuments() {
  loading.value = true
  try {
    const { data } = await api.get('/knowledge/list')
    documents.value = data.documents || []
  } catch (e) {
    ElMessage.error('加载文档列表失败')
  } finally {
    loading.value = false
  }
}

function beforeUpload(file) {
  const valid = ['.txt', '.pdf', '.docx']
  const ext = '.' + file.name.split('.').pop().toLowerCase()
  if (!valid.includes(ext)) {
    ElMessage.error('仅支持 .txt / .pdf / .docx 格式')
    return false
  }
  return true
}

function onUploadSuccess(resp) {
  ElMessage.success(`上传成功：${resp.filename}（${resp.chunks} 个知识块）`)
  loadDocuments()
}

function onUploadError(err) {
  ElMessage.error('上传失败：' + (err.message || '未知错误'))
}

async function deleteDocument(filename) {
  try {
    await api.delete(`/knowledge/${encodeURIComponent(filename)}`)
    ElMessage.success(`已删除：${filename}`)
    loadDocuments()
  } catch (e) {
    ElMessage.error('删除失败')
  }
}

onMounted(loadDocuments)
</script>

<style scoped>
.upload-card { margin-bottom: 20px; }

.upload-icon {
  font-size: 48px;
  color: #c0c4cc;
  margin-bottom: 8px;
}

.upload-text {
  font-size: 14px;
  color: #606266;
}

.upload-text em {
  color: #409EFF;
  font-style: normal;
}

.upload-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 8px;
}
</style>
