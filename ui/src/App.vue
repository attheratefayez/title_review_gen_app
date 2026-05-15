<script setup>
import { ref } from 'vue'
import UploadSection from './components/UploadSection.vue'
import ReviewEditor from './components/ReviewEditor.vue'
import ChatPanel from './components/ChatPanel.vue'
import StatusBar from './components/StatusBar.vue'

const documentId = ref(null)
const review = ref('')
const statusMessages = ref([])
const chatOpen = ref(true)

function addStatus(msg) {
  const id = Date.now()
  statusMessages.value.push({ ...msg, id })
  setTimeout(() => {
    statusMessages.value = statusMessages.value.filter(m => m.id !== id)
  }, 3000)
}

function onDocumentUploaded(id) {
  documentId.value = id
}

function onReviewGenerated(content) {
  review.value = content
}
</script>

<template>
  <div class="h-screen flex flex-col">
    <header class="flex items-center justify-between px-4 py-3 bg-white border-b border-gray-200 shrink-0">
      <h1 class="text-lg font-bold text-gray-800">Document Reviewer</h1>
      <button
        class="lg:hidden text-sm text-blue-600 hover:text-blue-800"
        @click="chatOpen = !chatOpen"
      >
        {{ chatOpen ? 'Hide Chat' : 'Show Chat' }}
      </button>
    </header>

    <div class="flex flex-1 min-h-0">
      <div class="flex-1 flex flex-col min-w-0">
        <UploadSection
          @document-uploaded="onDocumentUploaded"
          @review-generated="onReviewGenerated"
          @status="addStatus"
        />
        <ReviewEditor
          v-model="review"
          :document-id="documentId"
          @status="addStatus"
        />
      </div>

      <ChatPanel
        v-if="chatOpen"
        @status="addStatus"
      />
    </div>

    <StatusBar :messages="statusMessages" />
  </div>
</template>
