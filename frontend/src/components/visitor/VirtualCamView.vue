<template>
  <div class="virtual-cam">
    <div class="cam-container" :class="{ active: camActive, speaking: isSpeaking }">
      <!-- Webcam / Virtual Cam 画面 -->
      <video
        v-show="camActive"
        ref="videoEl"
        autoplay
        playsinline
        muted
        class="cam-video"
      />

      <!-- 未连接 OBS 时的占位 -->
      <div v-if="!camActive" class="cam-placeholder">
        <span class="placeholder-icon">📷</span>
        <span class="placeholder-text">
          {{ vtsConnected ? '请在 OBS 中开启 Virtual Cam' : 'VTube Studio 未连接' }}
        </span>
      </div>

      <!-- 说话状态光环 -->
      <div v-if="isSpeaking" class="speaking-ring"></div>
    </div>

    <div class="cam-controls">
      <el-tooltip content="切换到 Virtual Cam 画面（需先启动 OBS + VTube Studio）">
        <el-button
          size="small"
          :type="camActive ? 'success' : 'info'"
          :icon="camActive ? 'VideoCameraFilled' : 'VideoCamera'"
          circle
          @click="toggleCam"
        />
      </el-tooltip>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { VideoCamera, VideoCameraFilled } from '@element-plus/icons-vue'

defineProps({
  isSpeaking: { type: Boolean, default: false },
  vtsConnected: { type: Boolean, default: false },
})

const videoEl = ref(null)
const camActive = ref(false)
let stream = null

onMounted(async () => {
  // 默认不自动开启摄像头，由用户手动切换
})

async function toggleCam() {
  if (camActive.value) {
    // 关闭摄像头
    if (stream) {
      stream.getTracks().forEach(t => t.stop())
      stream = null
    }
    camActive.value = false
    return
  }

  // 尝试打开 Virtual Cam（OBS Virtual Camera 通常作为第一个非内置摄像头出现）
  try {
    const devices = await navigator.mediaDevices.enumerateDevices()
    const videoDevices = devices.filter(d => d.kind === 'videoinput')
    console.log('Available video devices:', videoDevices.map(d => d.label))

    // 优先选 OBS Virtual Camera
    let deviceId = null
    for (const d of videoDevices) {
      if (d.label.toLowerCase().includes('obs') || d.label.toLowerCase().includes('virtual')) {
        deviceId = d.deviceId
        break
      }
    }
    // 回退到最后一个摄像头（通常是外接的）
    if (!deviceId && videoDevices.length > 1) {
      deviceId = videoDevices[videoDevices.length - 1].deviceId
    }

    const constraints = {
      video: deviceId ? { deviceId: { exact: deviceId } } : true,
    }

    stream = await navigator.mediaDevices.getUserMedia(constraints)
    if (videoEl.value) {
      videoEl.value.srcObject = stream
    }
    camActive.value = true
  } catch (e) {
    console.warn('无法打开 Virtual Cam:', e.message)
    camActive.value = false
  }
}
</script>

<style scoped>
.cam-container {
  position: relative;
  width: 100%;
  aspect-ratio: 3/4;
  max-height: 300px;
  border-radius: 16px;
  overflow: hidden;
  background: linear-gradient(180deg, #1a1a2e, #16213e);
  border: 2px solid transparent;
  transition: border-color 0.3s;
}

.cam-container.active {
  border-color: #409EFF;
}

.cam-container.speaking {
  border-color: #67C23A;
  box-shadow: 0 0 16px rgba(103, 194, 58, 0.4);
}

.cam-video {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 14px;
}

.cam-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  gap: 8px;
  color: #8b8fa3;
}

.placeholder-icon {
  font-size: 36px;
  opacity: 0.6;
}

.placeholder-text {
  font-size: 12px;
  text-align: center;
  padding: 0 16px;
  opacity: 0.7;
}

.speaking-ring {
  position: absolute;
  inset: -3px;
  border-radius: 18px;
  border: 2px solid rgba(103, 194, 58, 0.6);
  animation: ringPulse 0.5s infinite alternate;
  pointer-events: none;
}

@keyframes ringPulse {
  from { border-color: rgba(103, 194, 58, 0.3); }
  to { border-color: rgba(103, 194, 58, 0.8); }
}

.cam-controls {
  display: flex;
  justify-content: center;
  margin-top: 8px;
}
</style>
