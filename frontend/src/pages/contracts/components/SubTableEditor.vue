<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import api from '../../../api/axios'
import { Edit, Trash2, Plus, Save, X, Search, ChevronUp, ChevronDown } from 'lucide-vue-next'

const props = defineProps<{
  endpoint: string
  contratoId: string
  pkField: string
  fields: Array<{ key: string; label: string; type: string }>
}>()

const rows = ref<any[]>([])
const loading = ref(false)
const error = ref('')
const editing = ref<any | null>(null)
const isCreating = ref(false)
const form = ref<any>({})

const searchQuery = ref('')
const sortKey = ref(props.fields[0].key)
const sortAsc = ref(true)

const fetchRows = async () => {
  loading.value = true
  try {
    const res = await api.get(`${props.endpoint}/?contrato_id=${encodeURIComponent(props.contratoId)}`)
    rows.value = res.data
  } catch (e) {
    error.value = 'Error al cargar datos'
  } finally {
    loading.value = false
  }
}

watch(() => props.contratoId, fetchRows)
onMounted(fetchRows)

const startCreate = () => {
  isCreating.value = true
  const defaultObj: any = { contrato: props.contratoId }
  props.fields.forEach(f => {
    if (f.key !== props.pkField && f.key !== 'contrato') {
      defaultObj[f.key] = f.type === 'number' ? null : ''
    }
  })
  form.value = defaultObj
  editing.value = defaultObj
}

const startEdit = (row: any) => {
  isCreating.value = false
  form.value = { ...row }
  editing.value = row
}

const cancelEdit = () => {
  editing.value = null
}

const saveRow = async () => {
  loading.value = true
  error.value = ''
  try {
    if (isCreating.value) {
      await api.post(`${props.endpoint}/`, form.value)
    } else {
      await api.put(`${props.endpoint}/${form.value[props.pkField]}/`, form.value)
    }
    editing.value = null
    fetchRows()
  } catch (e: any) {
    error.value = e.response?.data ? JSON.stringify(e.response.data) : 'Error al guardar'
  } finally {
    loading.value = false
  }
}

const deleteRow = async (row: any) => {
  if (!confirm('¿Eliminar este registro?')) return
  loading.value = true
  try {
    await api.delete(`${props.endpoint}/${row[props.pkField]}/`)
    fetchRows()
  } catch (e) {
    error.value = 'Error al eliminar'
  } finally {
    loading.value = false
  }
}

const setSort = (key: string) => {
  if (sortKey.value === key) {
    sortAsc.value = !sortAsc.value
  } else {
    sortKey.value = key
    sortAsc.value = true
  }
}

const filteredAndSortedRows = computed(() => {
  let result = rows.value
  
  if (searchQuery.value) {
    const lowerQuery = searchQuery.value.toLowerCase()
    result = result.filter(row => 
      props.fields.some(f => String(row[f.key] || '').toLowerCase().includes(lowerQuery))
    )
  }

  result.sort((a, b) => {
    const valA = a[sortKey.value] ?? ''
    const valB = b[sortKey.value] ?? ''
    if (valA < valB) return sortAsc.value ? -1 : 1
    if (valA > valB) return sortAsc.value ? 1 : -1
    return 0
  })

  return result
})

</script>

<template>
  <div class="space-y-4">
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
      <div class="relative w-full sm:w-72">
        <Search class="w-4 h-4 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
        <input v-model="searchQuery" type="text" placeholder="Buscar en esta pestaña..." class="w-full pl-9 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-[#1e5b4f] focus:border-[#1e5b4f] outline-none" />
      </div>
      <button v-if="!editing" @click="startCreate" class="bg-[#1e5b4f] hover:bg-[#024e47] text-white px-4 py-2 rounded-lg flex items-center gap-2 text-sm font-medium transition-colors shadow-sm whitespace-nowrap">
        <Plus class="w-4 h-4" /> Nuevo Registro
      </button>
    </div>

    <div v-if="error" class="bg-red-50 text-red-600 p-3 rounded-lg text-sm border border-red-200">
      {{ error }}
    </div>

    <!-- Edit Form -->
    <form v-if="editing" @submit.prevent="saveRow" class="bg-gray-50 border border-gray-200 p-5 rounded-xl space-y-4 shadow-sm">
      <div class="flex justify-between items-center mb-2">
        <h4 class="font-semibold text-[#1e5b4f]">{{ isCreating ? 'Crear Nuevo Registro' : 'Editar Registro' }}</h4>
        <button type="button" @click="cancelEdit" class="text-gray-400 hover:text-gray-700 bg-gray-200 hover:bg-gray-300 p-1.5 rounded-full transition-colors"><X class="w-4 h-4"/></button>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <label v-for="field in fields" :key="field.key" class="block">
          <span class="block text-xs font-semibold text-gray-600 mb-1.5">{{ field.label }}</span>
          <textarea v-if="field.type === 'textarea'" v-model="form[field.key]" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-[#1e5b4f] focus:border-[#1e5b4f] outline-none text-sm bg-white" rows="3"></textarea>
          <input v-else v-model="form[field.key]" :type="field.type" :step="field.type === 'number' ? 'any' : undefined" :disabled="!isCreating && field.key === pkField" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-[#1e5b4f] focus:border-[#1e5b4f] outline-none text-sm disabled:bg-gray-100 disabled:text-gray-500 bg-white" />
        </label>
      </div>
      <div class="flex justify-end pt-3">
        <button type="submit" :disabled="loading" class="bg-[#196B24] hover:bg-[#124d1a] text-white px-5 py-2.5 rounded-lg flex items-center gap-2 text-sm font-medium transition-colors shadow-sm disabled:opacity-50">
          <Save class="w-4 h-4" /> {{ loading ? 'Guardando...' : 'Guardar cambios' }}
        </button>
      </div>
    </form>

    <!-- Data Table -->
    <div v-else class="bg-white rounded-xl border border-gray-200 overflow-x-auto shadow-sm">
      <table class="w-full text-left text-sm">
        <thead>
          <tr class="bg-gray-50 border-b border-gray-200 text-gray-700">
            <th v-for="field in fields" :key="field.key" @click="setSort(field.key)" class="p-3 font-semibold cursor-pointer hover:bg-gray-100 transition-colors select-none">
              <div class="flex items-center gap-1">
                {{ field.label }}
                <span v-if="sortKey === field.key" class="text-[#1e5b4f]">
                  <ChevronUp v-if="sortAsc" class="w-3.5 h-3.5" />
                  <ChevronDown v-else class="w-3.5 h-3.5" />
                </span>
              </div>
            </th>
            <th class="p-3 font-semibold text-center w-24">Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in filteredAndSortedRows" :key="row[pkField]" class="border-b border-gray-100 hover:bg-[#f8faf9] transition-colors">
            <td v-for="field in fields" :key="field.key" class="p-3 text-gray-700 max-w-[250px] truncate">
              {{ row[field.key] !== null && row[field.key] !== '' ? row[field.key] : '-' }}
            </td>
            <td class="p-3">
              <div class="flex items-center justify-center gap-3">
                <button @click="startEdit(row)" class="text-gray-400 hover:text-[#1e5b4f] transition-colors" title="Editar"><Edit class="w-4 h-4" /></button>
                <button @click="deleteRow(row)" class="text-gray-400 hover:text-red-600 transition-colors" title="Eliminar"><Trash2 class="w-4 h-4" /></button>
              </div>
            </td>
          </tr>
          <tr v-if="filteredAndSortedRows.length === 0">
            <td :colspan="fields.length + 1" class="p-8 text-center text-gray-400">
              <p class="mb-1 text-base">No hay registros para mostrar</p>
              <p class="text-xs">Usa el botón "Nuevo Registro" para agregar información</p>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
