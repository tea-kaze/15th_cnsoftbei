<template>
  <div class="visitor-container">
    <!-- Header -->
    <header class="visitor-header">
      <DigitalHuman :speaking="isSpeaking" :emotion="currentEmotion" />
      <h1>灵山胜境 · AI智能导游</h1>
      <span class="header-subtitle">灵小导 为您服务</span>
    </header>

    <!-- 路线推荐切换按钮 -->
    <div class="toolbar">
      <button
        class="tool-btn"
        :class="{ active: showRecommend }"
        @click="showRecommend = !showRecommend"
      >
        🗺️ 路线推荐
      </button>
    </div>

    <!-- Chat Messages -->
    <div class="chat-window" ref="chatWindow">
      <!-- 推荐面板 -->
      <RecommendPanel v-if="showRecommend" @ask="onRecommendAsk" />

      <div v-if="!showRecommend && messages.length === 0" class="welcome-message">
        <div class="welcome-icon">🙏</div>
        <h2>您好！我是灵小导</h2>
        <p>灵山胜境的AI智能导游，您可以问我关于景区的任何问题～</p>
        <div class="suggest-questions">
          <span class="suggest-label">试试问我：</span>
          <button v-for="q in suggestQuestions" :key="q" @click="sendText(q)" class="suggest-btn">
            {{ q }}
          </button>
        </div>
      </div>

      <ChatBubble
        v-for="(msg, idx) in messages"
        :key="idx"
        :message="msg"
        @replay-audio="replayAudio(msg)"
      />
    </div>

    <!-- Chat Input -->
    <ChatInput
      :disabled="isLoading"
      @send-text="sendText"
      @send-voice="sendVoice"
    />
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { askQuestionStream, synthesizeSpeech } from '../api/chat.js'
import ChatBubble from '../components/visitor/ChatBubble.vue'
import ChatInput from '../components/visitor/ChatInput.vue'
import DigitalHuman from '../components/visitor/DigitalHuman.vue'
import RecommendPanel from '../components/visitor/RecommendPanel.vue'

const messages = ref([])
const isLoading = ref(false)
const isSpeaking = ref(false)
const currentEmotion = ref('neutral')
const showRecommend = ref(false)
const chatWindow = ref(null)
const audioElement = ref(new Audio())

// 多轮对话历史 (max 6 rounds = 12 messages)
const history = ref([])
const MAX_HISTORY = 12

const suggestQuestions = [
  '灵山大佛有多高？',
  '有哪些推荐的游览路线？',
  '九龙灌浴表演时间是什么？',
  '门票多少钱？',
]

function stripMarkdown(text) {
  // 去掉 markdown 格式，传给 TTS 的必须是纯文本
  return text
    .replace(/\*\*(.+?)\*\*/g, '$1')
    .replace(/^#{1,6}\s+/gm, '')
    .replace(/^[-*+]\s+/gm, '')
    .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
    .replace(/`{1,3}[^`]*`{1,3}/g, '')
    // 去掉 emoji（匹配所有 BMP 外字符 + 常见 emoji 范围）
    .replace(/[\uD800-\uDBFF][\uDC00-\uDFFF]/g, '')
}

function scrollToBottom() {
  nextTick(() => {
    if (chatWindow.value) {
      chatWindow.value.scrollTop = chatWindow.value.scrollHeight
    }
  })
}

function addMessage(role, text, audioUrl = null, timestamps = null) {
  const msg = {
    role,
    text,
    audioUrl,
    timestamps,
    time: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }),
  }
  messages.value.push(msg)
  scrollToBottom()
  return msg
}

async function sendText(text) {
  if (isLoading.value || !text.trim()) return

  showRecommend.value = false
  addMessage('user', text)
  isLoading.value = true

  try {
    // 流式回答
    const aiMsg = addMessage('assistant', '')
    let fullAnswer = ''

    for await (const event of askQuestionStream(text, [...history.value])) {
      if (event.token) {
        fullAnswer += event.token
        // 找到消息并更新 text（通过索引引用，因为 addMessage 后就是最后一个）
        const idx = messages.value.indexOf(aiMsg)
        if (idx >= 0) {
          messages.value[idx].text = fullAnswer
        }
        scrollToBottom()
      }
      if (event.done) {
        currentEmotion.value = event.emotion || 'neutral'
      }
    }

    // 更新对话历史（最多保留 MAX_HISTORY 条）
    history.value.push(
      { role: 'user', content: text },
      { role: 'assistant', content: fullAnswer }
    )
    if (history.value.length > MAX_HISTORY) {
      history.value = history.value.slice(-MAX_HISTORY)
    }

    // 流式完成后 TTS 合成并自动播放
    if (fullAnswer) {
      try {
        isSpeaking.value = true
        const tts = await synthesizeSpeech(stripMarkdown(fullAnswer))
        const idx = messages.value.indexOf(aiMsg)
        if (idx >= 0) {
          messages.value[idx].audioUrl = tts.audio_url
          messages.value[idx].timestamps = tts.word_timestamps
          messages.value[idx].audioDuration = tts.duration_ms
        }
        // 自动播放语音
        audioElement.value.src = tts.audio_url
        audioElement.value.onended = () => {
          isSpeaking.value = false
          currentEmotion.value = 'neutral'
        }
        audioElement.value.onerror = () => {
          isSpeaking.value = false
        }
        audioElement.value.play().catch(e => {
          console.warn('Auto-play blocked:', e)
          isSpeaking.value = false
        })
      } catch (ttsErr) {
        console.warn('TTS failed:', ttsErr)
        isSpeaking.value = false
      }
    }
  } catch (e) {
    addMessage('assistant', '抱歉，服务暂时不可用，请稍后再试 🙏')
    isSpeaking.value = false
  } finally {
    isLoading.value = false
  }
}

async function sendVoice(transcript) {
  await sendText(transcript)
}

function replayAudio(msg) {
  if (!msg.audioUrl) return
  isSpeaking.value = true
  audioElement.value.src = msg.audioUrl
  audioElement.value.onended = () => {
    isSpeaking.value = false
    currentEmotion.value = 'neutral'
  }
  audioElement.value.play().catch(e => {
    console.warn('Audio play failed:', e)
    isSpeaking.value = false
  })
}

function onRecommendAsk(question) {
  showRecommend.value = false
  sendText(question)
}
</script>

<style scoped>
.visitor-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  max-width: 480px;
  margin: 0 auto;
  background: linear-gradient(180deg, #f8f4eb 0%, #fff 100%);
}

.visitor-header {
  text-align: center;
  padding: 8px 20px 12px;
  background: linear-gradient(135deg, #8B4513, #A0522D);
  color: #fff;
  flex-shrink: 0;
}

.visitor-header h1 {
  font-size: 18px;
  font-weight: 600;
}

.header-subtitle {
  font-size: 12px;
  opacity: 0.85;
}

.toolbar {
  display: flex;
  gap: 8px;
  padding: 6px 16px;
  background: #fff;
  border-bottom: 1px solid #EFEBE9;
  flex-shrink: 0;
}

.tool-btn {
  background: #F8F4EB;
  border: 1px solid #D7CCC8;
  border-radius: 14px;
  padding: 4px 12px;
  font-size: 12px;
  color: #6D4C41;
  cursor: pointer;
  transition: all 0.2s;
}

.tool-btn:hover,
.tool-btn.active {
  background: #8B4513;
  color: #fff;
  border-color: #8B4513;
}

.chat-window {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.welcome-message {
  text-align: center;
  padding: 40px 20px;
}

.welcome-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.welcome-message h2 {
  font-size: 20px;
  color: #5D4037;
  margin-bottom: 8px;
}

.welcome-message p {
  font-size: 14px;
  color: #8D6E63;
  margin-bottom: 20px;
}

.suggest-questions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
}

.suggest-label {
  width: 100%;
  font-size: 12px;
  color: #A1887F;
}

.suggest-btn {
  background: #fff;
  border: 1px solid #D7CCC8;
  border-radius: 16px;
  padding: 6px 14px;
  font-size: 13px;
  color: #6D4C41;
  cursor: pointer;
  transition: all 0.2s;
}

.suggest-btn:hover {
  background: #EFEBE9;
  border-color: #8D6E63;
}
</style>
