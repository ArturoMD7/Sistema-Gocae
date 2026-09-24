<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import api from '../api/axios'
import { Activity, CircleDollarSign, Drill, FileText, Layers, MapPinned, TrendingUp } from 'lucide-vue-next'

interface Bucket {
  estatus?: string;
  modalidad?: string;
  tipo_yacimiento?: string;
  count: number;
}

interface TopMetric {
  contract_id: string;
  total: string | number;
}

const loading = ref(true)
const error = ref('')
const dashboard = ref<any>(null)
const contracts = ref<any[]>([])

const formatNumber = (value: number | string | null | undefined, digits = 0) => {
  const parsed = Number(value || 0)
  return new Intl.NumberFormat('es-MX', { maximumFractionDigits: digits }).format(parsed)
}

const formatMoney = (value: number | string | null | undefined, currency = 'USD') => {
  const parsed = Number(value || 0)
  return new Intl.NumberFormat('es-MX', {
    style: 'currency',
    currency,
    maximumFractionDigits: 0,
  }).format(parsed)
}

const loadDashboard = async () => {
  loading.value = true
  error.value = ''
  try {
    const [dashboardResponse, contractsResponse] = await Promise.all([
      api.get('contracts/dashboard/'),
      api.get('contracts/'),
    ])
    dashboard.value = dashboardResponse.data
    contracts.value = contractsResponse.data
  } catch (e) {
    error.value = 'No se pudo cargar el dashboard de contratos'
  } finally {
    loading.value = false
  }
}

const completionRate = computed(() => {
  const committed = Number(dashboard.value?.committed_wells || 0)
  if (!committed) return 0
  return Math.round((Number(dashboard.value?.completed_wells || 0) / committed) * 100)
})

const maxBucket = (items: Bucket[]) => Math.max(...items.map((item) => item.count), 1)
const maxTop = (items: TopMetric[]) => Math.max(...items.map((item) => Number(item.total || 0)), 1)

onMounted(loadDashboard)
</script>

<template>
  <div class="p-8 max-w-7xl mx-auto space-y-6">
    <div class="flex flex-col md:flex-row md:items-end md:justify-between gap-4">
      <div>
        <h1 class="text-3xl font-bold text-[#1e5b4f]">Dashboard GOCAE</h1>
        <p class="text-gray-500 mt-1">Vista general de contratos, inversiones e ingresos.</p>
      </div>
      <router-link :to="{ name: 'contracts' }" class="bg-[#1e5b4f] hover:bg-[#024e47] text-white px-4 py-2 rounded-lg flex items-center gap-2 font-medium transition-colors shadow-sm w-fit">
        <FileText class="w-5 h-5" />
        Ver contratos
      </router-link>
    </div>

    <div v-if="error" class="bg-red-50 text-red-700 p-4 rounded-lg border border-red-200">{{ error }}</div>
    <div v-if="loading" class="bg-white rounded-lg border border-[#e0e0e0] p-8 text-center text-gray-500">Cargando dashboard...</div>

    <template v-else-if="dashboard">
      <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        <div class="bg-white rounded-lg border border-[#e0e0e0] p-5">
          <div class="flex items-center justify-between text-[#1e5b4f] mb-4">
            <span class="text-sm font-semibold text-gray-500">Contratos</span>
            <FileText class="w-5 h-5" />
          </div>
          <p class="text-3xl font-bold text-gray-900">{{ dashboard.total_contracts }}</p>
          <p class="text-sm text-gray-500 mt-1">{{ dashboard.active_contracts }} vigentes</p>
        </div>

        <div class="bg-white rounded-lg border border-[#e0e0e0] p-5">
          <div class="flex items-center justify-between text-[#1e5b4f] mb-4">
            <span class="text-sm font-semibold text-gray-500">Superficie</span>
            <MapPinned class="w-5 h-5" />
          </div>
          <p class="text-3xl font-bold text-gray-900">{{ formatNumber(dashboard.surface_km2, 1) }}</p>
          <p class="text-sm text-gray-500 mt-1">km2 contractuales</p>
        </div>

        <div class="bg-white rounded-lg border border-[#e0e0e0] p-5">
          <div class="flex items-center justify-between text-[#1e5b4f] mb-4">
            <span class="text-sm font-semibold text-gray-500">Pozos</span>
            <Drill class="w-5 h-5" />
          </div>
          <p class="text-3xl font-bold text-gray-900">{{ formatNumber(dashboard.completed_wells) }}/{{ formatNumber(dashboard.committed_wells) }}</p>
          <p class="text-sm text-gray-500 mt-1">{{ completionRate }}% terminados</p>
        </div>

        <div class="bg-white rounded-lg border border-[#e0e0e0] p-5">
          <div class="flex items-center justify-between text-[#1e5b4f] mb-4">
            <span class="text-sm font-semibold text-gray-500">Ingresos Estado</span>
            <CircleDollarSign class="w-5 h-5" />
          </div>
          <p class="text-3xl font-bold text-gray-900">{{ formatMoney(dashboard.revenue_mxn, 'MXN') }}</p>
          <p class="text-sm text-gray-500 mt-1">{{ formatMoney(dashboard.revenue_usd) }} USD</p>
        </div>
      </div>

      <div class="grid grid-cols-1 xl:grid-cols-3 gap-6">
        <div class="bg-white rounded-lg border border-[#e0e0e0] p-6">
          <div class="flex items-center gap-2 mb-5 text-[#1e5b4f]">
            <Activity class="w-5 h-5" />
            <h2 class="text-lg font-semibold text-gray-800">Estatus</h2>
          </div>
          <div class="space-y-4">
            <div v-for="item in dashboard.by_status" :key="item.estatus || 'Sin estatus'">
              <div class="flex justify-between text-sm mb-1">
                <span class="text-gray-700 truncate pr-3">{{ item.estatus || 'Sin estatus' }}</span>
                <span class="font-semibold text-gray-900">{{ item.count }}</span>
              </div>
              <div class="h-2 bg-gray-100 rounded-full overflow-hidden">
                <div class="h-full bg-[#1e5b4f]" :style="{ width: `${(item.count / maxBucket(dashboard.by_status)) * 100}%` }"></div>
              </div>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-lg border border-[#e0e0e0] p-6">
          <div class="flex items-center gap-2 mb-5 text-[#1e5b4f]">
            <Layers class="w-5 h-5" />
            <h2 class="text-lg font-semibold text-gray-800">Modalidad</h2>
          </div>
          <div class="space-y-4">
            <div v-for="item in dashboard.by_modality" :key="item.modalidad || 'Sin modalidad'">
              <div class="flex justify-between text-sm mb-1">
                <span class="text-gray-700">{{ item.modalidad || 'Sin modalidad' }}</span>
                <span class="font-semibold text-gray-900">{{ item.count }}</span>
              </div>
              <div class="h-2 bg-gray-100 rounded-full overflow-hidden">
                <div class="h-full bg-[#840016]" :style="{ width: `${(item.count / maxBucket(dashboard.by_modality)) * 100}%` }"></div>
              </div>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-lg border border-[#e0e0e0] p-6">
          <div class="flex items-center gap-2 mb-5 text-[#1e5b4f]">
            <TrendingUp class="w-5 h-5" />
            <h2 class="text-lg font-semibold text-gray-800">Inversion ejercida</h2>
          </div>
          <p class="text-2xl font-bold text-gray-900 mb-5">{{ formatMoney(dashboard.investment_usd) }}</p>
          <div class="space-y-4">
            <div v-for="item in dashboard.top_investments" :key="item.contract_id">
              <div class="flex justify-between text-sm mb-1 gap-3">
                <span class="text-gray-700 truncate">{{ item.contract_id }}</span>
                <span class="font-semibold text-gray-900">{{ formatMoney(item.total) }}</span>
              </div>
              <div class="h-2 bg-gray-100 rounded-full overflow-hidden">
                <div class="h-full bg-[#308c1d]" :style="{ width: `${(Number(item.total || 0) / maxTop(dashboard.top_investments)) * 100}%` }"></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg border border-[#e0e0e0] overflow-hidden">
        <div class="p-5 border-b border-[#e0e0e0] flex items-center justify-between">
          <h2 class="text-lg font-semibold text-gray-800">Contratos recientes</h2>
          <span class="text-sm text-gray-500">{{ contracts.length }} registros</span>
        </div>
        <div class="overflow-x-auto">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="bg-white border-b border-[#e0e0e0] text-[#1e5b4f]">
                <th class="p-3 font-semibold text-sm">Contrato</th>
                <th class="p-3 font-semibold text-sm">Operador</th>
                <th class="p-3 font-semibold text-sm">Modalidad</th>
                <th class="p-3 font-semibold text-sm">Yacimiento</th>
                <th class="p-3 font-semibold text-sm">Estatus</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="contract in contracts.slice(0, 8)" :key="contract.id" class="border-b border-[#e0e0e0] hover:bg-gray-50/50">
                <td class="p-3 text-sm font-medium text-gray-900">{{ contract.contract_id }}</td>
                <td class="p-3 text-sm text-gray-700">{{ contract.operador_principal || 'N/A' }}</td>
                <td class="p-3 text-sm text-gray-700">{{ contract.modalidad || 'N/A' }}</td>
                <td class="p-3 text-sm text-gray-700">{{ contract.tipo_yacimiento || 'N/A' }}</td>
                <td class="p-3 text-sm text-gray-700">{{ contract.estatus || 'N/A' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </template>
  </div>
</template>
