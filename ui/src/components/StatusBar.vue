<script setup>
defineProps({
  messages: {
    type: Array,
    default: () => [],
  },
})
</script>

<template>
  <div class="flex items-center gap-2 px-4 py-2 text-sm text-gray-600 bg-white border-t border-gray-200">
    <template v-if="messages.length">
      <span
        v-for="msg in messages.slice(-3)"
        :key="msg.id"
        class="flex items-center gap-1"
      >
        <span
          class="inline-block w-2 h-2 rounded-full"
          :class="{
            'bg-green-500': msg.type === 'success',
            'bg-blue-500': msg.type === 'info',
            'bg-red-500': msg.type === 'error',
          }"
        />
        {{ msg.text }}
      </span>
    </template>
    <span v-else class="text-gray-400">Ready</span>
  </div>
</template>
