<template>
  <div class="chat-input-bar">
    <!-- Voice Input Button -->
    <button
      :class="['voice-btn', { recording: isRecording, unsupported: !voiceSupported }]"
      @click="toggleRecording"
      :disabled="disabled"
      :title="isRecording ? '点击停止录音' : (voiceSupported ? '语音输入' : '语音输入不可用')"
    >
      {{ isRecording ? '⏹' : '🎤' }}
    </button>
    <span v-if="isRecording" class="recording-hint">说完点击停止</span>

    <!-- Text Input -->
    <input
      ref="textInput"
      v-model="inputText"
      type="text"
      class="text-input"
      placeholder="问我关于灵山胜境的任何问题..."
      :disabled="disabled"
      @keydown.enter="handleSend"
    />

    <!-- Send Button -->
    <button
      class="send-btn"
      @click="handleSend"
      :disabled="disabled || !inputText.trim()"
    >
      发送
    </button>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  disabled: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['sendText', 'sendVoice'])

const inputText = ref('')
const isRecording = ref(false)
const textInput = ref(null)
const voiceSupported = ref(true)

// 当前录音实例（每次录音新建，避免复用导致的状态问题）
let currentRecognition = null

function createRecognition() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
  if (!SpeechRecognition) {
    voiceSupported.value = false
    return null
  }

  let finalTranscript = ''

  const rec = new SpeechRecognition()
  rec.lang = 'zh-CN'
  rec.continuous = true
  rec.interimResults = true

  rec.onstart = () => {
    isRecording.value = true
    ElMessage.success('正在聆听...说完后点击按钮停止')
  }

  rec.onresult = (event) => {
    if (!isRecording.value) return

    let interim = ''
    for (let i = event.resultIndex; i < event.results.length; i++) {
      const result = event.results[i]
      if (result.isFinal) {
        finalTranscript += result[0].transcript
      } else {
        interim += result[0].transcript
      }
    }
    inputText.value = (finalTranscript + interim).trim()
  }

  rec.onerror = (event) => {
    isRecording.value = false
    console.warn('[Speech] Error:', event.error, event.message)
    const errors = {
      'not-allowed': '麦克风权限被拒绝，请在浏览器设置中允许访问麦克风',
      'no-speech': '未检测到语音。可能原因：1)麦克风未工作 2)网络受限（Web Speech API 依赖 Google 服务器，国内网络可能无法访问）',
      'audio-capture': '未找到麦克风设备，请检查设备连接',
      'network': '网络连接失败。Web Speech API 依赖 Google 服务器，国内用户可能需要使用 VPN',
      'aborted': '语音识别已中止。请重试或使用文字输入',
      'service-not-allowed': '语音服务不可用。国内网络可能无法访问 Google 语音服务，建议使用文字输入',
      'language-not-supported': '当前浏览器不支持中文语音识别',
    }
    const msg = errors[event.error] || `语音识别失败(${event.error})，建议使用文字输入`
    ElMessage.warning(msg)
  }

  rec.onend = () => {
    isRecording.value = false
    currentRecognition = null
  }

  return rec
}

function toggleRecording() {
  if (isRecording.value) {
    // 手动停止 → 发送文本
    try { currentRecognition?.stop() } catch {}
    isRecording.value = false
    const text = inputText.value.trim()
    if (text) {
      inputText.value = ''
      emit('sendVoice', text)
    } else {
      ElMessage.info('未识别到语音，请再试一次')
    }
    currentRecognition = null
    return
  }

  // 开始录音 → 每次新建实例
  const rec = createRecognition()
  if (!rec) {
    ElMessage.info('您的浏览器不支持语音输入，请使用文字输入')
    textInput.value?.focus()
    return
  }

  currentRecognition = rec
  inputText.value = ''
  try {
    rec.start()
  } catch (e) {
    isRecording.value = false
    currentRecognition = null
    ElMessage.warning('语音启动失败，请重试')
    console.warn('Speech start error:', e)
  }
}

function handleSend() {
  if (props.disabled || !inputText.value.trim()) return
  emit('sendText', inputText.value.trim())
  inputText.value = ''
  textInput.value?.focus()
}
</script>

<style scoped>
.chat-input-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  background: #fff;
  border-top: 1px solid #E8E0D5;
  flex-shrink: 0;
}

.voice-btn {
  width: 40px;
  height: 40px;
  border: none;
  border-radius: 50%;
  background: #F5F0EB;
  font-size: 18px;
  cursor: pointer;
  flex-shrink: 0;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.voice-btn.recording {
  background: #FF5252;
  animation: pulse 1.2s infinite;
}

.voice-btn.unsupported {
  opacity: 0.3;
  cursor: not-allowed;
}

.recording-hint {
  font-size: 11px;
  color: #FF5252;
  white-space: nowrap;
  animation: blink 1s infinite;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.15); }
}

.text-input {
  flex: 1;
  height: 40px;
  border: 1px solid #E8E0D5;
  border-radius: 20px;
  padding: 0 16px;
  font-size: 14px;
  outline: none;
  background: #FAFAFA;
  transition: border-color 0.2s;
}

.text-input:focus {
  border-color: #A0522D;
  background: #fff;
}

.send-btn {
  height: 40px;
  padding: 0 16px;
  border: none;
  border-radius: 20px;
  background: linear-gradient(135deg, #8B4513, #A0522D);
  color: #fff;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  flex-shrink: 0;
  transition: opacity 0.2s;
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.send-btn:not(:disabled):hover {
  opacity: 0.9;
}
</style>
