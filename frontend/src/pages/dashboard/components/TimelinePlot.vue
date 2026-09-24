<template>
  <div class="h-full max-h-[400px] overflow-y-auto pr-2">
    <div v-if="items.length === 0" class="text-gray-400 p-4 text-center">
      No hay eventos en la línea de tiempo.
    </div>
    <div v-else class="relative border-l-2 border-[#196B24] ml-3 mt-2">
      <div v-for="(item, index) in items" :key="index" class="mb-6 ml-6 relative">
        <span class="absolute flex items-center justify-center w-6 h-6 bg-[#196B24] rounded-full -left-9 ring-4 ring-white">
          <svg class="w-3 h-3 text-white" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 16 12">
            <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M1 5.917 5.724 10.5 15 1.5"/>
          </svg>
        </span>
        <h3 class="flex items-center mb-1 text-sm font-semibold text-gray-900">{{ item.evento }}</h3>
        <time class="block mb-2 text-xs font-normal leading-none text-gray-500">{{ item.fecha }}</time>
        <p class="mb-4 text-sm font-normal text-gray-600">{{ item.detallesEvento }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  items: Array<{ fecha: string; evento: string; detallesEvento: string }>
}>();
</script>
