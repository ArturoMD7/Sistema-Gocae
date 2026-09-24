<template>
  <div class="h-full w-full">
    <Bar
      v-if="chartData.labels.length"
      :data="chartData"
      :options="chartOptions"
      class="h-[300px] w-full"
    />
    <div v-else class="h-[300px] flex items-center justify-center text-gray-400">
      Sin datos de inversión
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { Bar } from 'vue-chartjs';
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale } from 'chart.js';

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale);

const props = defineProps<{
  data: Array<{ year: number; month: string; total: number }>
}>();

const chartData = computed(() => {
  const labels = props.data.map(d => `${d.year}-${d.month}`);
  const values = props.data.map(d => d.total);

  return {
    labels,
    datasets: [
      {
        label: 'Inversión (USD)',
        backgroundColor: '#196B24',
        data: values
      }
    ]
  };
});

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false
    }
  },
  scales: {
    y: {
      beginAtZero: true
    }
  }
};
</script>
