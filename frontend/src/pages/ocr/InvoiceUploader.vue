<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { UploadCloud, CheckCircle, AlertTriangle, FileText, Download, Loader2 } from 'lucide-vue-next'
import apiClient from '../../api/axios'
import axios from 'axios'

const isDragging = ref(false)
const isLoading = ref(false)
const processingStatus = ref('')
const files = ref<File[]>([])
const results = ref<any[]>([])
const errorMsg = ref('')

const contracts = ref<any[]>([])
const selectedContractId = ref('')

const pctOperador = ref(70.0)
const pctSocio = ref(30.0)

// Cargar contratos de Django al montar
onMounted(async () => {
  try {
    const response = await apiClient.get('contracts/')
    contracts.value = response.data
  } catch (error) {
    console.error("Error cargando contratos", error)
  }
})

// Actualizar porcentajes cuando se selecciona un contrato
const handleContractChange = () => {
  const contract = contracts.value.find(c => c.id === selectedContractId.value)
  if (contract) {
    pctOperador.value = contract.participacion_operador || 70.0
    pctSocio.value = contract.participacion_socio || 30.0
  }
}

const handleDragOver = (e: DragEvent) => { e.preventDefault(); isDragging.value = true }
const handleDragLeave = (e: DragEvent) => { e.preventDefault(); isDragging.value = false }
const handleDrop = (e: DragEvent) => {
  e.preventDefault()
  isDragging.value = false
  if (e.dataTransfer?.files) {
    addFiles(Array.from(e.dataTransfer.files))
  }
}
const handleFileSelect = (e: Event) => {
  const target = e.target as HTMLInputElement
  if (target.files) {
    addFiles(Array.from(target.files))
  }
}

const addFiles = (newFiles: File[]) => {
  errorMsg.value = ''
  for (const file of newFiles) {
    if (file.name.toLowerCase().endsWith('.xml')) {
      if (!files.value.some(f => f.name === file.name)) {
        files.value.push(file)
      }
    }
  }
}

const removeFile = (index: number) => {
  files.value.splice(index, 1)
}

const processXMLs = async () => {
  if (files.value.length === 0) return
  isLoading.value = true
  errorMsg.value = ''
  results.value = []
  
  let processed = 0
  
  for (const file of files.value) {
    processingStatus.value = `Procesando: ${file.name} (${processed + 1}/${files.value.length})`
    const formData = new FormData()
    formData.append('file', file)
    formData.append('pct_operador', pctOperador.value.toString())
    formData.append('pct_socio', pctSocio.value.toString())

    try {
      const response = await axios.post('http://localhost:8001/api/extract/invoice', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      if (response.data.status === 'success') {
        results.value = [...results.value, ...response.data.data]
      }
    } catch (err: any) {
      console.error(err)
    }
    processed++
  }
  
  processingStatus.value = ''
  isLoading.value = false
}

const downloadExcel = async () => {
  if (results.value.length === 0) return
  try {
    const response = await axios.post('http://localhost:8001/api/export/excel', 
      { data: results.value },
      { responseType: 'blob' }
    )
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', 'Facturas_Extraidas.xlsx')
    document.body.appendChild(link)
    link.click()
    link.remove()
  } catch (error) {
    alert("Error al descargar Excel")
  }
}

const columns = computed(() => {
  if (results.value.length === 0) return []
  return Object.keys(results.value[0])
})
</script>

<template>
  <div class="p-8 pb-20 max-w-[1600px] mx-auto">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-3xl font-bold text-[#1e5b4f]">Extractor Masivo de Facturas (XML)</h1>
      <button 
        v-if="results.length > 0"
        @click="downloadExcel"
        class="bg-green-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-green-700 transition flex items-center gap-2"
      >
        <Download class="w-5 h-5" />
        Descargar Excel
      </button>
    </div>

    <!-- Panel de Configuración -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
      <h2 class="text-lg font-semibold mb-4 border-b pb-2">Configuración de Extracción</h2>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Seleccionar Contrato (Opcional)</label>
          <select v-model="selectedContractId" @change="handleContractChange" class="w-full border rounded p-2 focus:ring-[#1e5b4f] focus:border-[#1e5b4f]">
            <option value="">-- Usar 70% / 30% por defecto --</option>
            <option v-for="c in contracts" :key="c.id" :value="c.id">
              {{ c.id }} - {{ c.nombre_bloque }}
            </option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Porcentaje Operador (%)</label>
          <input type="number" step="0.01" v-model="pctOperador" class="w-full border rounded p-2 focus:ring-[#1e5b4f] focus:border-[#1e5b4f]" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Porcentaje Socio (%)</label>
          <input type="number" step="0.01" v-model="pctSocio" class="w-full border rounded p-2 focus:ring-[#1e5b4f] focus:border-[#1e5b4f]" />
        </div>
      </div>
    </div>

    <!-- Zona de Drop -->
    <div 
      class="bg-white border-2 border-dashed rounded-xl p-10 text-center transition-colors duration-200 cursor-pointer mb-6"
      :class="isDragging ? 'border-[#1e5b4f] bg-[#1e5b4f]/5' : 'border-gray-300 hover:border-[#1e5b4f]/50'"
      @dragover="handleDragOver"
      @dragleave="handleDragLeave"
      @drop="handleDrop"
      @click="$refs.fileInput.click()"
    >
      <!-- webkitdirectory multiple lets you select folders -->
      <input type="file" ref="fileInput" class="hidden" accept=".xml" multiple webkitdirectory @change="handleFileSelect" />
      <UploadCloud class="w-16 h-16 mx-auto text-gray-400 mb-4" :class="{'text-[#1e5b4f]': isDragging}" />
      
      <div>
        <h3 class="text-lg font-medium text-gray-900 mb-1">Haz clic o arrastra una carpeta de facturas aquí</h3>
        <p class="text-sm text-gray-500">Puedes seleccionar múltiples archivos XML a la vez.</p>
      </div>
    </div>

    <div v-if="files.length > 0" class="mb-6">
      <div class="flex justify-between items-center mb-2">
        <h3 class="font-medium text-gray-700">{{ files.length }} archivos listos para procesar</h3>
        <button @click="files = []" class="text-sm text-red-600 hover:underline">Limpiar lista</button>
      </div>
      <div class="flex flex-wrap gap-2 max-h-32 overflow-y-auto bg-gray-50 p-2 rounded border">
        <div v-for="(f, i) in files" :key="i" class="bg-white border text-xs px-2 py-1 rounded flex items-center gap-1 shadow-sm">
          <FileText class="w-3 h-3 text-[#1e5b4f]" />
          <span class="truncate max-w-[150px]">{{ f.name }}</span>
          <button @click="removeFile(i)" class="ml-1 text-red-500 hover:text-red-700 font-bold">×</button>
        </div>
      </div>
    </div>

    <div v-if="errorMsg" class="bg-red-50 text-red-600 p-4 rounded-lg mb-6 flex items-center gap-3">
      <AlertTriangle class="w-5 h-5 shrink-0" />
      {{ errorMsg }}
    </div>

    <!-- Botón Procesar -->
    <div class="flex flex-col items-center justify-center mb-8" v-if="files.length > 0">
      <button 
        @click="processXMLs" 
        :disabled="isLoading"
        class="bg-[#1e5b4f] text-white px-8 py-3 rounded-lg font-medium hover:bg-[#154239] transition flex items-center gap-2 disabled:opacity-50"
      >
        <Loader2 v-if="isLoading" class="w-5 h-5 animate-spin" />
        <span v-if="isLoading">Procesando lote...</span>
        <span v-else>Extraer Datos de {{ files.length }} facturas</span>
      </button>
      <span v-if="processingStatus" class="mt-2 text-sm text-gray-600 font-medium">{{ processingStatus }}</span>
    </div>

    <!-- Resultados Completos -->
    <div v-if="results.length > 0" class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
      <div class="p-4 border-b flex justify-between items-center bg-gray-50">
        <h2 class="font-semibold text-lg flex items-center gap-2">
          <CheckCircle class="w-5 h-5 text-green-600" /> Vista Previa Completa
        </h2>
        <span class="text-sm bg-blue-100 text-blue-800 px-3 py-1 rounded-full font-medium">
          {{ results.length }} filas extraídas
        </span>
      </div>
      <div class="overflow-auto max-h-[700px]">
        <table class="w-full text-left border-collapse text-[13px]">
          <thead class="sticky top-0 bg-gray-100 shadow-sm z-10">
            <tr>
              <th v-for="col in columns" :key="col" class="p-2 border-b border-gray-200 font-semibold text-gray-700 whitespace-nowrap">
                {{ col }}
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, idx) in results" :key="idx" class="hover:bg-[#1e5b4f]/5 border-b border-gray-100">
              <td v-for="col in columns" :key="col" class="p-2 whitespace-nowrap max-w-[200px] truncate" :title="String(row[col])">
                <span v-if="col === 'Alertas' && row[col]" class="text-red-600 font-medium bg-red-50 px-1 rounded">{{ row[col] }}</span>
                <span v-else-if="col === 'Estado' && row[col] === 'Error'" class="text-red-600 font-medium">{{ row[col] }}</span>
                <span v-else>{{ row[col] }}</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

  </div>
</template>
