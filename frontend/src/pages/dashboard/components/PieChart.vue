<template>
  <div class="h-full w-full">
    <Pie
      v-if="chartData.labels.length"
      :data="chartData"
      :options="chartOptions"
      class="h-[250px] w-full"
    />
    <div v-else class="h-[250px] flex items-center justify-center text-gray-400">
      Sin datos
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { Pie } from 'vue-chartjs';
import { Chart as ChartJS, Title, Tooltip, Legend, ArcElement } from 'chart.js';

ChartJS.register(Title, Tooltip, Legend, ArcElement);

const props = defineProps<{
  data: Array<{ label: string; value: number; color: string }>
}>();

const chartData = computed(() => {
  return {
    labels: props.data.map(d => d.label),
    datasets: [
      {
        backgroundColor: props.data.map(d => d.color),
        data: props.data.map(d => d.value)
      }
    ]
  };
});

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom' as const
    }
  }
};
</script>
