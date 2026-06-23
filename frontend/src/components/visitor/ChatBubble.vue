<template>
  <div :class="['chat-bubble', message.role === 'user' ? 'user-bubble' : 'ai-bubble']">
    <div v-if="message.role === 'assistant'" class="ai-avatar">🧑‍💼</div>
    <div class="bubble-content">
      <div
        v-if="message.role === 'assistant'"
        class="bubble-text"
        v-html="renderMarkdown(message.text)"
      />
      <div v-else class="bubble-text">{{ message.text }}</div>
      <div class="bubble-footer">
        <span class="bubble-time">{{ message.time }}</span>
        <button
          v-if="message.role === 'assistant' && message.audioUrl"
          class="replay-btn"
          @click="$emit('replayAudio')"
        >🔊</button>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  message: {
    type: Object,
    required: true,
  },
})

defineEmits(['replayAudio'])

function renderMarkdown(text) {
  if (!text) return ''
  let html = text
    // 先处理 **bold**
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    // 段落之间空行
    .replace(/\n\n+/g, '</p><p>')
    // 单行换行
    .replace(/\n/g, '<br>')
  // 包裹在 p 标签中
  html = '<p>' + html + '</p>'
  return html
}
</script>

<style scoped>
.chat-bubble {
  display: flex;
  margin-bottom: 16px;
  max-width: 85%;
}

.user-bubble {
  margin-left: auto;
  flex-direction: row-reverse;
}

.ai-bubble {
  margin-right: auto;
}

.ai-avatar {
  width: 36px;
  height: 36px;
  font-size: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-right: 8px;
}

.user-bubble .ai-avatar {
  display: none;
}

.bubble-content {
  display: flex;
  flex-direction: column;
}

.bubble-text {
  padding: 10px 14px;
  border-radius: 16px;
  font-size: 14px;
  line-height: 1.6;
  word-break: break-word;
}

.user-bubble .bubble-text {
  background: linear-gradient(135deg, #8B4513, #A0522D);
  color: #fff;
  border-bottom-right-radius: 4px;
}

.ai-bubble .bubble-text {
  background: #fff;
  color: #3E2723;
  border: 1px solid #E8E0D5;
  border-bottom-left-radius: 4px;
}

.bubble-footer {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 2px 8px 0;
}

.bubble-time {
  font-size: 11px;
  color: #BDBDBD;
}

.replay-btn {
  background: none;
  border: none;
  font-size: 14px;
  cursor: pointer;
  opacity: 0.6;
  transition: opacity 0.2s;
}

.replay-btn:hover {
  opacity: 1;
}
</style>
