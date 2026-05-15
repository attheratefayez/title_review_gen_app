<script setup>
import { ref, watch } from 'vue'
import { MdEditor } from 'md-editor-v3'
import 'md-editor-v3/lib/style.css'
import { saveReview } from '../api/documents.js'

const props = defineProps({
  documentId: { type: String, default: null },
  modelValue: { type: String, default: '' },
})

const emit = defineEmits(['update:modelValue', 'status'])

const saving = ref(false)
const localContent = ref(props.modelValue)

watch(() => props.modelValue, (val) => {
  localContent.value = val
})

watch(localContent, (val) => {
  emit('update:modelValue', val)
})

async function handleSave() {
  if (!props.documentId) return
  saving.value = true
  try {
    await saveReview(props.documentId, localContent.value)
    emit('status', { type: 'success', text: 'Review saved' })
  } catch {
    emit('status', { type: 'error', text: 'Save failed' })
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="flex-1 flex flex-col min-h-0 p-4">
    <div class="flex items-center justify-between mb-3">
      <h2 class="text-sm font-semibold text-gray-700 uppercase tracking-wide">
        Title Review Draft
      </h2>
      <button
        class="px-3 py-1.5 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        :disabled="!documentId || saving"
        @click="handleSave"
      >
        {{ saving ? 'Saving...' : 'Save' }}
      </button>
    </div>

    <div class="flex-1 min-h-0 border border-gray-200 rounded-lg overflow-hidden">
      <MdEditor
        v-if="localContent"
        v-model="localContent"
        :toolbars="['bold', 'italic', 'heading', 'strike', 'quote', 'code', 'link', 'unordered-list', 'ordered-list', 'preview', 'previewOnly']"
        language="en-US"
        class="h-full"
      />
      <div v-else class="flex items-center justify-center h-full text-sm text-gray-400">
        Upload a document and generate a review to get started
      </div>
    </div>
  </div>
</template>
