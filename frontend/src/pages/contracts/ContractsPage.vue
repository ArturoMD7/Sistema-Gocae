<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import api from '../../api/axios'
import { Edit, Search } from 'lucide-vue-next'
import { useAuthStore } from '../../stores/auth'

const authStore = useAuthStore()
const contracts = ref<any[]>([])
const loading = ref(true)
const error = ref('')
const query = ref('')
const statusFilter = ref('')

const fetchContracts = async () => {
  loading.value = true
  error.value = ''
  try {
    const response = await api.get('contracts/')
    contracts.value = response.data
  } catch (e) {
    error.value = 'Error al cargar contratos'
  } finally {
    loading.value = false
  }
}

const statuses = computed(() => {
  const unique = new Set(contracts.value.map((contract) => contract.estatus).filter(Boolean))
  return Array.from(unique).sort()
})

const filteredContracts = computed(() => {
  const text = query.value.trim().toLowerCase()
  return contracts.value.filter((contract) => {
    const matchesText = !text || [
      contract.contract_id,
      contract.operador_principal,
      contract.modalidad,
      contract.tipo_yacimiento,
      contract.estado,
    ].some((value) => String(value || '').toLowerCase().includes(text))
    const matchesStatus = !statusFilter.value || contract.estatus === statusFilter.value
    return matchesText && matchesStatus
  })
})

onMounted(fetchContracts)
</script>

<template>
  <div class="p-8 max-w-7xl mx-auto space-y-6">
    <div class="flex flex-col md:flex-row md:items-end md:justify-between gap-4">
      <div>
        <h1 class="text-3xl font-bold text-[#1e5b4f]">Contratos</h1>
        <p class="text-gray-500 mt-1">{{ filteredContracts.length }} registros disponibles</p>
      </div>
    </div>

    <div class="bg-white rounded-lg border border-[#e0e0e0] p-4">
      <div class="grid grid-cols-1 md:grid-cols-[1fr_260px] gap-3">
        <label class="relative block">
          <Search class="w-5 h-5 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input v-model="query" type="search" class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-[#1e5b4f] focus:border-[#1e5b4f] outline-none" placeholder="Buscar contrato, operador o zona" />
        </label>
        <select v-model="statusFilter" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-[#1e5b4f] focus:border-[#1e5b4f] outline-none">
          <option value="">Todos los estatus</option>
          <option v-for="status in statuses" :key="status" :value="status">{{ status }}</option>
        </select>
      </div>
    </div>

    <div v-if="error" class="bg-red-50 text-red-700 p-4 rounded-lg border border-red-200">{{ error }}</div>
    <div class="bg-white rounded-lg border border-[#e0e0e0] overflow-hidden">
      <div v-if="loading" class="p-8 text-center text-gray-500">Cargando contratos...</div>
      <div v-else class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="bg-white border-b border-[#e0e0e0] text-[#1e5b4f]">
              <th class="p-3 font-semibold text-sm">Contrato</th>
              <th class="p-3 font-semibold text-sm">Operador</th>
              <th class="p-3 font-semibold text-sm">Modalidad</th>
              <th class="p-3 font-semibold text-sm">Area</th>
              <th class="p-3 font-semibold text-sm">Superficie</th>
              <th class="p-3 font-semibold text-sm">Estatus</th>
              <th v-if="authStore.isAdmin" class="p-3 font-semibold text-sm text-center">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="contract in filteredContracts" :key="contract.id" class="border-b border-[#e0e0e0] hover:bg-gray-50/50 transition-colors">
              <td class="p-3 text-sm font-medium text-gray-900">{{ contract.contract_id }}</td>
              <td class="p-3 text-sm text-gray-700 min-w-[220px]">{{ contract.operador_principal || 'N/A' }}</td>
              <td class="p-3 text-sm text-gray-700">{{ contract.modalidad || 'N/A' }}</td>
              <td class="p-3 text-sm text-gray-700">{{ contract.area || 'N/A' }}</td>
              <td class="p-3 text-sm text-gray-700">{{ contract.superficie_km2 || 'N/A' }}</td>
              <td class="p-3 text-sm text-gray-700 min-w-[220px]">{{ contract.estatus || 'N/A' }}</td>
              <td v-if="authStore.isAdmin" class="p-3 text-center">
                <router-link :to="{ name: 'contract-edit', params: { id: contract.id } }" class="inline-flex text-gray-700 hover:text-[#1e5b4f] transition-colors" title="Editar">
                  <Edit class="w-[18px] h-[18px]" />
                </router-link>
              </td>
            </tr>
            <tr v-if="filteredContracts.length === 0">
              <td :colspan="authStore.isAdmin ? 7 : 6" class="p-8 text-center text-gray-500">No se encontraron contratos.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
