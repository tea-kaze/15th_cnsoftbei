<template>
  <div class="config-panel">
    <!-- VTS 连接状态 -->
    <el-card shadow="hover" class="section-card">
      <template #header>
        <span><el-icon><Connection /></el-icon> VTube Studio 连接状态</span>
        <el-tag :type="vtsConnected ? 'success' : 'danger'" style="float:right">
          {{ vtsConnected ? '已连接' : '未连接' }}
        </el-tag>
      </template>
      <el-descriptions v-if="vtsStats" :column="2" border size="small">
        <el-descriptions-item label="模型名称">{{ vtsStats.model_name || '未知' }}</el-descriptions-item>
        <el-descriptions-item label="FPS">{{ vtsStats.fps || 0 }}</el-descriptions-item>
        <el-descriptions-item label="可用表情">{{ (vtsStats.expressions || []).join(', ') || '无' }}</el-descriptions-item>
        <el-descriptions-item label="运行时长">{{ vtsStats.uptime || 0 }}s</el-descriptions-item>
      </el-descriptions>
      <div class="vts-actions">
        <el-button type="primary" :loading="connecting" @click="connectVTS">
          {{ vtsConnected ? '重新连接' : '连接 VTube Studio' }}
        </el-button>
        <el-alert
          v-if="!vtsConnected"
          type="warning"
          :closable="false"
          style="margin-top: 12px"
        >
          <template #title>
            请确保 VTube Studio 已启动，并在设置中开启 <b>Start API (端口 8001)</b>
          </template>
        </el-alert>
      </div>
    </el-card>

    <!-- 表情测试 -->
    <el-card shadow="hover" class="section-card">
      <template #header><span>😊 表情测试</span></template>
      <el-row :gutter="12">
        <el-col :xs="8" :sm="6" v-for="emo in emotionList" :key="emo.key">
          <el-button
            :type="emo.type"
            class="emo-btn"
            @click="setExpression(emo.key)"
          >
            {{ emojiMap[emo.key] }} {{ emo.label }}
          </el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- 动作测试 -->
    <el-card shadow="hover" class="section-card">
      <template #header><span>🎬 动作测试</span></template>
      <el-row :gutter="12">
        <el-col :xs="8" :sm="6">
          <el-button class="act-btn" @click="triggerHotkey('wave')">
            👋 挥手欢迎
          </el-button>
        </el-col>
        <el-col :xs="8" :sm="6">
          <el-button class="act-btn" @click="triggerHotkey('bow')">
            🙇 鞠躬感谢
          </el-button>
        </el-col>
        <el-col :xs="8" :sm="6">
          <el-button class="act-btn" @click="triggerHotkey('think')">
            🤔 思考歪头
          </el-button>
        </el-col>
        <el-col :xs="8" :sm="6">
          <el-button class="act-btn" @click="greet">
            🎉 完整欢迎
          </el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- 数字人形象配置（基础） -->
    <el-card shadow="hover" class="section-card">
      <template #header><span><el-icon><Setting /></el-icon> 形象设置</span></template>
      <el-form :model="form" label-width="100px" size="default">
        <el-form-item label="角色名称">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="欢迎语">
          <el-input v-model="form.welcome" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="默认语音">
          <el-select v-model="form.voice" placeholder="选择 TTS 发音人">
            <el-option label="晓晓（女声·温暖）" value="zh-CN-XiaoxiaoNeural" />
            <el-option label="云希（男声·新闻）" value="zh-CN-YunxiNeural" />
            <el-option label="晓伊（女声·活泼）" value="zh-CN-XiaoyiNeural" />
            <el-option label="云健（男声·运动）" value="zh-CN-YunjianNeural" />
            <el-option label="云扬（男声·新闻）" value="zh-CN-YunyangNeural" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary">保存设置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Connection, Setting, User } from '@element-plus/icons-vue'
import api from '../../api/chat.js'

const vtsConnected = ref(false)
const vtsStats = ref(null)
const connecting = ref(false)
let statusTimer = null

const form = ref({
  name: '灵小导',
  welcome: '您好！我是灵小导，灵山胜境的AI智能导游，您可以问我关于景区的任何问题～',
  voice: 'zh-CN-XiaoxiaoNeural',
})

const emotionList = [
  { key: 'happy', label: '开心', type: 'success' },
  { key: 'sad', label: '难过', type: 'info' },
  { key: 'surprised', label: '惊讶', type: 'warning' },
  { key: 'angry', label: '愤怒', type: 'danger' },
  { key: 'neutral', label: '重置', type: '' },
]

const emojiMap = { happy: '😊', sad: '😢', surprised: '😲', angry: '😠', neutral: '😐' }

async function checkStatus() {
  try {
    const { data } = await api.get('/vts/status')
    vtsConnected.value = data?.connected || false
    vtsStats.value = data
  } catch {
    vtsConnected.value = false
    vtsStats.value = { connected: false }
  }
}

async function connectVTS() {
  connecting.value = true
  try {
    const { data } = await api.post('/vts/connect')
    vtsConnected.value = data?.connected || false
    ElMessage[data?.connected ? 'success' : 'error'](data?.message || '')
    // 连接成功后刷新统计信息
    await checkStatus()
  } catch {
    ElMessage.error('连接失败，请确认 VTube Studio 已启动')
  } finally {
    connecting.value = false
  }
}

onMounted(() => {
  checkStatus()
  // 每 5 秒轮询 VTS 状态（连接状态和统计数据会实时变化）
  statusTimer = setInterval(checkStatus, 5000)
})

onUnmounted(() => {
  if (statusTimer) clearInterval(statusTimer)
})

async function setExpression(emotion) {
  try {
    await api.post('/vts/expression', { emotion, active: emotion !== 'neutral' })
    ElMessage.success(`表情: ${emotion}`)
  } catch {
    ElMessage.error('VTS 未连接')
  }
}

async function triggerHotkey(id) {
  try {
    await api.post('/vts/hotkey', { hotkey_id: id })
    ElMessage.success(`动作已触发: ${id}`)
  } catch {
    ElMessage.error('VTS 未连接')
  }
}

async function greet() {
  try {
    await api.post('/vts/greet')
    ElMessage.success('欢迎流程已触发')
  } catch {
    ElMessage.error('VTS 未连接')
  }
}

</script>

<style scoped>
.section-card { margin-bottom: 20px; }

.vts-actions { margin-top: 12px; }

.emo-btn, .act-btn {
  width: 100%;
  margin-bottom: 8px;
}
</style>
