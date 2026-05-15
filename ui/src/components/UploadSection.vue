<script setup>
import { ref } from 'vue'
import { uploadDocument, generateReview } from '../api/documents.js'

const emit = defineEmits(['document-uploaded', 'review-generated', 'status'])

const ALLOWED_TYPES = ['application/pdf', 'image/png']
const ALLOWED_EXTENSIONS = ['.pdf', '.png']
const dragOver = ref(false)
const uploading = ref(false)
const generating = ref(false)
const file = ref(null)
const documentId = ref(null)

function isValidFile(f) {
  if (ALLOWED_TYPES.includes(f.type)) return true
  const ext = '.' + f.name.split('.').pop().toLowerCase()
  return ALLOWED_EXTENSIONS.includes(ext)
}

function onDrop(e) {
  dragOver.value = false
  const f = e.dataTransfer?.files?.[0] || e.target?.files?.[0]
  if (!f) return
  if (!isValidFile(f)) {
    emit('status', { type: 'error', text: 'Only .pdf and .png files are allowed' })
    return
  }
  file.value = f
}

function onDragOver(e) {
  e.preventDefault()
  dragOver.value = true
}
function onDragLeave() {
  dragOver.value = false
}

async function handleUpload() {
  if (!file.value) return
  uploading.value = true
  try {
    const { data } = await uploadDocument(file.value)
    documentId.value = data.document_id
    emit('document-uploaded', data.document_id)
    emit('status', { type: 'success', text: `Uploaded ${file.value.name}` })
  } catch {
    emit('status', { type: 'error', text: 'Upload failed' })
  } finally {
    uploading.value = false
  }
}

async function handleGenerate() {
  if (!documentId.value) return
  generating.value = true
  try {
    const { data } = await generateReview(documentId.value)
    emit('review-generated', data.review)
    emit('status', { type: 'success', text: 'Review draft generated' })
  } catch {
    emit('status', { type: 'error', text: 'Generation failed' })
  } finally {
    generating.value = false
  }
}

function removeFile() {
  file.value = null
  documentId.value = null
}
</script>

<template>
  <div class="p-4 border-b border-gray-200">
    <h2 class="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-3">
      Upload Document
    </h2>

    <div
      v-if="!file"
      class="relative"
      @dragover="onDragOver"
      @dragleave="onDragLeave"
      @drop="onDrop"
    >
      <label
        class="flex flex-col items-center justify-center w-full h-32 border-2 border-dashed rounded-lg cursor-pointer transition-colors"
        :class="dragOver ? 'border-blue-400 bg-blue-50' : 'border-gray-300 hover:border-blue-300 hover:bg-gray-50'"
      >
        <svg class="w-8 h-8 mb-2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6h.1a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
        </svg>
        <p class="text-sm text-gray-500"><span class="font-medium text-blue-600">Click to browse</span> or drag & drop</p>
        <p class="text-xs text-gray-400 mt-1">PDF or PNG only</p>
        <input type="file" accept=".pdf,.png" class="hidden" @change="onDrop" />
      </label>
    </div>

    <div v-else class="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
      <div class="flex-1 min-w-0">
        <p class="text-sm font-medium text-gray-700 truncate">{{ file.name }}</p>
        <p class="text-xs text-gray-400">{{ (file.size / 1024).toFixed(1) }} KB</p>
      </div>
      <button
        class="text-xs text-gray-400 hover:text-red-500 transition-colors"
        @click="removeFile"
      >
        Remove
      </button>
    </div>

    <div class="flex gap-2 mt-3">
      <button
        v-if="file && !documentId"
        class="flex-1 px-3 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        :disabled="uploading"
        @click="handleUpload"
      >
        {{ uploading ? 'Uploading...' : 'Upload' }}
      </button>
      <button
        v-if="documentId"
        class="flex-1 px-3 py-2 text-sm font-medium text-white bg-green-600 rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        :disabled="generating"
        @click="handleGenerate"
      >
        {{ generating ? 'Generating...' : 'Generate Review' }}
      </button>
    </div>
  </div>
</template>
