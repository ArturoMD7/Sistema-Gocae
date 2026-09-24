<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../../api/axios'
import { ArrowLeft, Save } from 'lucide-vue-next'
import SubTableEditor from './components/SubTableEditor.vue'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const error = ref('')
const success = ref('')
const form = ref<any>({})
const activeTab = ref('general')

const fields = [
  { key: 'contract_id', label: 'ID Contrato', type: 'text' },
  { key: 'modalidad', label: 'Modalidad', type: 'select', options: ['Licencia', 'Producción Compartida', 'Asociación', 'Servicios'] },
  { key: 'ronda', label: 'Ronda', type: 'text' },
  { key: 'licitacion', label: 'Licitacion', type: 'text' },
  { key: 'area', label: 'Area', type: 'text' },
  { key: 'pozos_comprometidos', label: 'Pozos comprometidos', type: 'number' },
  { key: 'pozos_terminados', label: 'Pozos terminados', type: 'number' },
  { key: 'operador_principal', label: 'Operador principal', type: 'text' },
  { key: 'tipo_licitante', label: 'Tipo licitante', type: 'select', options: ['Individual', 'Consorcio', 'Migración', 'Asociación Pemex'] },
  { key: 'tipo_yacimiento', label: 'Tipo yacimiento', type: 'select', options: ['Terrestre', 'Aguas Someras', 'Aguas Profundas'] },
  { key: 'estado', label: 'Estado', type: 'text' },
  { key: 'superficie_km2', label: 'Superficie km2', type: 'number' },
  { key: 'fecha_firma', label: 'Fecha firma', type: 'text' },
  { key: 'duracion_anios', label: 'Duracion anios', type: 'number' },
  { key: 'vence', label: 'Vence', type: 'text' },
  { key: 'estatus', label: 'Estatus', type: 'select', options: ['Vigente', 'En Renuncia', 'Terminación Anticipada', 'Terminado', 'Suspendido'] },
  { key: 'participacion_estado', label: 'Participacion Estado', type: 'number' }
]

const loadContract = async () => {
  loading.value = true
  error.value = ''
  try {
    const response = await api.get(`contracts/${encodeURIComponent(route.params.id as string)}/`)
    form.value = response.data
  } catch (e) {
    error.value = 'Error al cargar contrato'
  } finally {
    loading.value = false
  }
}

const saveContract = async () => {
  loading.value = true
  error.value = ''
  success.value = ''
  try {
    await api.put(`contracts/${encodeURIComponent(route.params.id as string)}/`, form.value)
    success.value = 'Contrato actualizado'
  } catch (e: any) {
    error.value = e.response?.data ? JSON.stringify(e.response.data) : 'Error al actualizar contrato'
  } finally {
    loading.value = false
  }
}

onMounted(loadContract)

const tabs = [
  { id: 'general', label: 'Datos Generales' },
  { id: 'lineas-tiempo', label: 'Línea de Tiempo' },
  { id: 'geologicos', label: 'Datos Geológicos' },
  { id: 'inversiones', label: 'Inversiones' },
  { id: 'pmt', label: 'Prog. Mínimo de Trabajo' },
  { id: 'contratistas', label: 'Contratistas' },
  { id: 'ubicaciones', label: 'Ubicaciones' },
]

const subTables: Record<string, any> = {
  'lineas-tiempo': { endpoint: 'lineas-tiempo', pkField: 'id_timeline', fields: [{key:'id_timeline', label:'ID', type:'text'}, {key:'fecha', label:'Fecha', type:'text'}, {key:'evento', label:'Evento', type:'textarea'}, {key:'detalles', label:'Detalles', type:'textarea'}] },
  'geologicos': { endpoint: 'geologicos', pkField: 'id_datgeo', fields: [{key:'id_datgeo', label:'ID', type:'text'}, {key:'provincia_petrolera', label:'Prov. Petrolera', type:'text'}, {key:'provincia_geologica', label:'Prov. Geológica', type:'text'}, {key:'superficie', label:'Superficie', type:'text'}, {key:'cobertura', label:'Cobertura', type:'text'}, {key:'edad_play', label:'Edad Play', type:'text'}, {key:'litologias', label:'Litologías', type:'textarea'}, {key:'hidrocarburo', label:'Hidrocarburo', type:'text'}] },
  'inversiones': { endpoint: 'inversiones', pkField: 'id_inversion', fields: [{key:'id_inversion', label:'ID', type:'text'}, {key:'anio', label:'Año', type:'number'}, {key:'mes', label:'Mes', type:'text'}, {key:'monto_ejercido_usd', label:'Monto Ejercido USD', type:'number'}] },
  'pmt': { endpoint: 'pmt', pkField: 'id_pmt', fields: [{key:'id_pmt', label:'ID', type:'text'}, {key:'programa_minimo', label:'Prog. Mínimo', type:'number'}, {key:'incremento', label:'Incremento', type:'number'}, {key:'periodo_adicional', label:'Periodo Adicional', type:'number'}, {key:'total_requerido', label:'Total Requerido', type:'number'}, {key:'acreditadas', label:'Acreditadas', type:'number'}, {key:'fecha_limite', label:'Fecha Límite', type:'text'}] },
  'contratistas': { endpoint: 'contratistas', pkField: 'id_socio', fields: [{key:'id_socio', label:'ID Socio', type:'text'}, {key:'empresa_nombre', label:'Empresa', type:'text'}, {key:'tipo_participacion', label:'Tipo Participación', type:'text'}, {key:'porcentaje_participacion', label:'% Participación', type:'number'}] },
  'ubicaciones': { endpoint: 'ubicaciones', pkField: 'id_punto', fields: [{key:'id_punto', label:'ID Punto', type:'text'}, {key:'numero_vertice', label:'Vertice', type:'number'}, {key:'longitud', label:'Longitud', type:'number'}, {key:'latitud', label:'Latitud', type:'number'}] },
}

</script>

<template>
  <div class="p-8 max-w-6xl mx-auto space-y-6">
    <div class="flex items-center gap-4">
      <button @click="router.back()" class="p-2 text-gray-500 hover:text-[#1e5b4f] hover:bg-gray-200 rounded-full transition-colors" title="Regresar">
        <ArrowLeft class="w-6 h-6" />
      </button>
      <div>
        <h1 class="text-3xl font-bold text-[#1e5b4f]">Contrato: {{ form.contract_id || 'Cargando...' }}</h1>
        <p class="text-gray-500 mt-1">Gestión unificada del contrato y su información vinculada</p>
      </div>
    </div>

    <!-- Tabs -->
    <div class="border-b border-gray-200 overflow-x-auto">
      <nav class="flex space-x-6 px-2 min-w-max" aria-label="Tabs">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          :class="[
            activeTab === tab.id ? 'border-[#1e5b4f] text-[#1e5b4f]' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
            'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors'
          ]"
        >
          {{ tab.label }}
        </button>
      </nav>
    </div>

    <div v-if="error" class="bg-red-50 text-red-700 p-4 rounded-lg border border-red-200">{{ error }}</div>
    <div v-if="success" class="bg-green-50 text-green-700 p-4 rounded-lg border border-green-200">{{ success }}</div>

    <!-- Tab 1: Datos Generales -->
    <form v-if="activeTab === 'general'" @submit.prevent="saveContract" class="bg-white rounded-lg border border-[#e0e0e0] p-6 space-y-6 shadow-sm">
      <div v-if="loading && !form.id" class="p-8 text-center text-gray-500">Cargando contrato...</div>
      <template v-else>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          <label v-for="field in fields" :key="field.key" class="block">
            <span class="block text-sm font-medium text-gray-700 mb-1">{{ field.label }}</span>
            <select v-if="field.type === 'select'" v-model="form[field.key]" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-[#1e5b4f] focus:border-[#1e5b4f] outline-none transition-all text-sm bg-white">
              <option value="" disabled>Seleccionar...</option>
              <option v-for="opt in field.options" :key="opt" :value="opt">{{ opt }}</option>
            </select>
            <input v-else v-model="form[field.key]" :type="field.type" :step="field.type === 'number' ? '0.0001' : undefined" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-[#1e5b4f] focus:border-[#1e5b4f] outline-none transition-all text-sm" />
          </label>
        </div>
        <div class="flex justify-end pt-4 border-t border-gray-100">
          <button type="submit" :disabled="loading" class="bg-[#1e5b4f] hover:bg-[#024e47] text-white px-6 py-2.5 rounded-lg flex items-center gap-2 font-medium transition-colors shadow-sm disabled:opacity-70">
            <Save class="w-5 h-5" />
            {{ loading ? 'Guardando...' : 'Guardar cambios' }}
          </button>
        </div>
      </template>
    </form>

    <!-- Sub Tables -->
    <div v-else class="bg-white rounded-lg border border-[#e0e0e0] p-6 shadow-sm">
      <SubTableEditor 
        v-if="form.contract_id"
        :key="activeTab"
        :endpoint="subTables[activeTab].endpoint"
        :contratoId="form.contract_id"
        :pkField="subTables[activeTab].pkField"
        :fields="subTables[activeTab].fields"
      />
    </div>

  </div>
</template>
