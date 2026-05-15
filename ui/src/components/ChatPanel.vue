<script setup>
import { ref, nextTick } from 'vue'
import { sendMessage } from '../api/chat.js'

const emit = defineEmits(['status'])

const messages = ref([])
const input = ref('')
const sending = ref(false)
const list = ref(null)

async function handleSend() {
  const text = input.value.trim()
  if (!text || sending.value) return

  input.value = ''
  messages.value.push({ role: 'user', content: text })
  sending.value = true
  scrollDown()

  try {
    const { data } = await sendMessage(text)
    messages.value.push({ role: 'assistant', content: data.response })
    scrollDown()
  } catch {
    emit('status', { type: 'error', text: 'Chat request failed' })
    sending.value = false
  } finally {
    sending.value = false
  }
}

function scrollDown() {
  nextTick(() => {
    if (list.value) {
      list.value.scrollTop = list.value.scrollHeight
    }
  })
}

function onKeydown(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    handleSend()
  }
}
</script>

<template>
  <div class="w-80 flex flex-col bg-white border-l border-gray-200">
    <h2 class="text-sm font-semibold text-gray-700 uppercase tracking-wide px-4 py-3 border-b border-gray-200">
      Chat
    </h2>

    <div ref="list" class="flex-1 overflow-y-auto px-4 py-3 space-y-3">
      <div
        v-for="(msg, i) in messages"
        :key="i"
        class="flex"
        :class="msg.role === 'user' ? 'justify-end' : 'justify-start'"
      >
        <div
          class="max-w-[85%] rounded-lg px-3 py-2 text-sm whitespace-pre-wrap"
          :class="msg.role === 'user'
            ? 'bg-blue-600 text-white'
            : 'bg-gray-100 text-gray-800'"
        >
          {{ msg.content }}
        </div>
      </div>
      <p v-if="!messages.length" class="text-sm text-gray-400 text-center pt-4">
        Ask questions about the document or request changes to the review
      </p>
    </div>

    <div class="border-t border-gray-200 p-3">
      <div class="flex gap-2">
        <textarea
          v-model="input"
          class="flex-1 resize-none rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          rows="2"
          placeholder="Type a message..."
          :disabled="sending"
          @keydown="onKeydown"
        />
        <button
          class="self-end px-3 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          :disabled="!input.trim() || sending"
          @click="handleSend"
        >
          <svg v-if="sending" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
          <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>
