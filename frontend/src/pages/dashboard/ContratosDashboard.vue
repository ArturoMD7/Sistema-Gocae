<template>
  <div class="p-6 bg-gray-50 min-h-screen">
    <div v-if="loading" class="flex flex-col items-center justify-center h-64">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-[#1e5b4f]"></div>
      <p class="mt-4 text-gray-600">Cargando datos del dashboard...</p>
    </div>

    <div v-else-if="error" class="bg-red-50 text-red-600 p-4 rounded-lg border border-red-200">
      {{ error }}
    </div>

    <div v-else-if="dashboardData && selectedContratoId">
      <!-- Encabezado con selector de contrato -->
      <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6 flex justify-between items-center">
        <div>
          <p class="text-sm text-gray-500 font-semibold mb-1 uppercase tracking-wide">
            Gerencia de Operación de Contratos y Asociaciones de Exploración
          </p>
          <div class="flex items-center gap-3">
            <select 
              v-model="selectedContratoId" 
              class="text-2xl font-bold text-[#1e5b4f] bg-transparent border-none p-0 focus:ring-0 cursor-pointer"
            >
              <option v-for="cid in dashboardData.contratoIds" :key="cid" :value="cid">
                {{ cid }}
              </option>
            </select>
          </div>
        </div>
        <div>
          <img src="../../assets/logo_min.png" alt="Pemex" class="h-12 opacity-80" />
        </div>
      </div>

      <!-- Primera Fila -->
      <div class="grid grid-cols-1 lg:grid-cols-4 gap-6 mb-6">
        <!-- Datos Relevantes -->
        <div class="bg-white p-5 rounded-lg shadow-sm border border-gray-200 lg:col-span-1">
          <h2 class="text-lg font-bold text-[#1e5b4f] mb-4">Datos relevantes</h2>
          <div class="space-y-0">
            <div v-for="(stat, idx) in contractStats" :key="idx" class="flex justify-between py-2 border-b border-[#196B24]/20 text-sm">
              <span class="font-semibold text-gray-700">{{ stat.label }}</span>
              <span class="text-gray-900 text-right">{{ stat.value || '-' }}</span>
            </div>
          </div>
          <button 
            @click="showGeologyModal = true"
            class="w-full mt-5 px-4 py-2 border-2 border-[#196B24] text-[#196B24] hover:bg-[#196B24] hover:text-white transition-colors rounded font-semibold text-sm"
          >
            Ver Datos Geológicos
          </button>
        </div>

        <!-- Inversiones -->
        <div class="bg-white p-5 rounded-lg shadow-sm border border-gray-200 lg:col-span-1 flex flex-col">
          <h2 class="text-lg font-bold text-[#1e5b4f] mb-4">Inversiones</h2>
          <div class="flex-1 min-h-[250px]">
            <AnnualInvestmentChart :data="annualInvestments" />
          </div>
          <div class="mt-4 pt-4 border-t border-gray-100 flex justify-between items-center">
            <span class="text-gray-600 font-semibold">Total ejercido</span>
            <span class="text-xl font-bold text-gray-900">
              {{ formatCurrency(totalInversionEjercida) }}
            </span>
          </div>
        </div>

        <!-- Plan de Exploración -->
        <div class="bg-white p-5 rounded-lg shadow-sm border border-gray-200 lg:col-span-2">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6 h-full">
            <div>
              <h2 class="text-lg font-bold text-[#1e5b4f] mb-4">Plan de exploración y unidades de trabajo</h2>
              <div class="space-y-0">
                <div v-for="(unit, idx) in workUnits" :key="idx" class="flex justify-between py-2 border-b border-[#196B24]/20 text-sm">
                  <span class="font-semibold text-gray-700">{{ unit.label }}</span>
                  <span class="text-gray-900">{{ unit.value || '-' }}</span>
                </div>
              </div>
            </div>
            <div class="flex flex-col">
              <h2 class="text-lg font-bold text-[#1e5b4f] mb-4">Distribución del valor de la producción</h2>
              <div class="flex-1">
                <PieChart :data="productionValueBreakdown" />
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Segunda Fila -->
      <div class="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <!-- Mapa -->
        <div class="bg-white p-5 rounded-lg shadow-sm border border-gray-200 lg:col-span-1">
          <h2 class="text-lg font-bold text-[#1e5b4f] mb-2 flex items-center justify-between">
            <span>Ubicación:</span>
            <span class="text-gray-700 font-semibold text-base">{{ selectedContrato?.estado || 'Desconocido' }}</span>
          </h2>
          <MexicoMap 
            :points="selectedUbicaciones" 
            :surfaceLabel="`Superficie: ${selectedContrato?.superficie.toFixed(2)} km²`"
          />
        </div>

        <!-- Participación y Timeline -->
        <div class="lg:col-span-3 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div class="bg-white p-5 rounded-lg shadow-sm border border-gray-200 md:col-span-1 flex flex-col">
            <h2 class="text-lg font-bold text-[#1e5b4f] mb-4">Interés de participación</h2>
            <div class="flex-1">
              <PieChart :data="participationInterestData" />
            </div>
          </div>
          
          <div class="bg-white p-5 rounded-lg shadow-sm border border-gray-200 md:col-span-2">
            <h2 class="text-lg font-bold text-[#1e5b4f] mb-4">Línea de tiempo</h2>
            <TimelinePlot :items="selectedLineasTiempo" />
          </div>
        </div>
      </div>
    </div>

    <!-- Modal Geológico -->
    <div v-if="showGeologyModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
      <div class="bg-white rounded-lg shadow-xl w-full max-w-3xl overflow-hidden flex flex-col max-h-[90vh]">
        <div class="p-4 border-b border-[#196B24]/20 flex justify-between items-center">
          <h3 class="text-xl font-bold text-[#196B24]">Datos Geológicos - {{ selectedContratoId }}</h3>
          <button @click="showGeologyModal = false" class="text-gray-500 hover:text-gray-800 text-2xl leading-none">&times;</button>
        </div>
        <div class="p-6 overflow-y-auto bg-gray-50/50">
          <div v-if="!selectedGeologicos.length" class="text-center text-gray-500 my-4">
            No hay datos geológicos disponibles para este contrato.
          </div>
          <div v-for="geo in selectedGeologicos" :key="geo.geologicoId" class="bg-white p-4 rounded border-l-4 border-[#196B24] shadow-sm mb-4 grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div><span class="block text-gray-500 text-xs">Provincia Petrolera</span> <span class="font-semibold">{{ geo.ProvinciaPetrolera || '-' }}</span></div>
            <div><span class="block text-gray-500 text-xs">Provincia Geológica</span> <span class="font-semibold">{{ geo.ProvinciaGeologica || '-' }}</span></div>
            <div><span class="block text-gray-500 text-xs">Superficie del Área Contractual</span> <span class="font-semibold">{{ geo.SuperficieAcontractual || '-' }} km²</span></div>
            <div><span class="block text-gray-500 text-xs">Cobertura Sísmica 3D</span> <span class="font-semibold">{{ geo.CoberturaSismica3D || '-' }}</span></div>
            <div><span class="block text-gray-500 text-xs">Edad Play</span> <span class="font-semibold">{{ geo.EdadPlay || '-' }}</span></div>
            <div><span class="block text-gray-500 text-xs">Litología</span> <span class="font-semibold">{{ geo.Litologia || '-' }}</span></div>
            <div class="md:col-span-2"><span class="block text-gray-500 text-xs">Hidrocarburo Esperado</span> <span class="font-semibold">{{ geo.HidrocarburoEsperado || '-' }}</span></div>
          </div>
        </div>
        <div class="p-4 border-t border-gray-200 text-right bg-white">
          <button @click="showGeologyModal = false" class="px-4 py-2 bg-gray-200 text-gray-800 rounded hover:bg-gray-300 font-medium">Cerrar</button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import AnnualInvestmentChart from './components/AnnualInvestmentChart.vue';
import PieChart from './components/PieChart.vue';
import MexicoMap from './components/MexicoMap.vue';
import TimelinePlot from './components/TimelinePlot.vue';
import apiClient from '../../api/axios';

const loading = ref(true);
const error = ref('');
const dashboardData = ref<any>(null);
const selectedContratoId = ref('');
const showGeologyModal = ref(false);

const fetchDashboardData = async () => {
  try {
    loading.value = true;
    const response = await apiClient.get('dashboard/');
    dashboardData.value = response.data;
    if (dashboardData.value.contratoIds?.length > 0) {
      selectedContratoId.value = dashboardData.value.contratoIds[0];
    }
  } catch (err: any) {
    console.error('Error fetching dashboard:', err);
    error.value = 'No se pudieron cargar los datos del dashboard.';
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchDashboardData();
});

const formatCurrency = (val: number) => {
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(val);
};

// Computed properties based on selectedContratoId
const selectedContrato = computed(() => {
  if (!dashboardData.value) return null;
  return dashboardData.value.contratos.find((c: any) => c.contratoId === selectedContratoId.value) || dashboardData.value.contratos[0];
});

const selectedInversiones = computed(() => {
  if (!dashboardData.value) return [];
  return dashboardData.value.inversiones.filter((i: any) => i.contratoId === selectedContratoId.value);
});

const selectedUbicaciones = computed(() => {
  if (!dashboardData.value) return [];
  return dashboardData.value.ubicaciones
    .filter((u: any) => u.contratoId === selectedContratoId.value)
    .sort((a: any, b: any) => a.numeroVertice - b.numeroVertice);
});

const selectedLineasTiempo = computed(() => {
  if (!dashboardData.value) return [];
  return dashboardData.value.lineasTiempo.filter((l: any) => l.contratoId === selectedContratoId.value);
});

const selectedGeologicos = computed(() => {
  if (!dashboardData.value) return [];
  return dashboardData.value.geologicos.filter((g: any) => g.contratoId === selectedContratoId.value);
});

const contractStats = computed(() => {
  if (!selectedContrato.value) return [];
  const c = selectedContrato.value;
  return [
    { label: 'Operador', value: c.operadorPrincipal },
    { label: 'Modalidad', value: c.modalidad },
    { label: 'Fecha de Firma de CEE', value: c.fechaFirma },
    { label: 'Vigencia', value: String(c.vence) },
    { label: 'Tipo de yacimiento', value: c.tipoYacimient },
    { label: 'Participación del estado', value: `${(c.participacionEstado || 0).toFixed(2)}%` },
    { label: 'Pozos comprometidos', value: c.pozosComprometidos },
    { label: 'Pozos terminados', value: c.pozosTerminados },
    { label: 'Estatus', value: c.estatus },
  ];
});

const totalInversionEjercida = computed(() => {
  return selectedInversiones.value.reduce((acc: number, inv: any) => acc + (inv.montoEjercidoUsd || 0), 0);
});

const annualInvestments = computed(() => {
  const map: Record<string, { year: number; month: string; total: number }> = {};
  selectedInversiones.value.forEach((inv: any) => {
    const key = `${inv.anio}-${inv.mes}`;
    if (!map[key]) {
      map[key] = { year: inv.anio, month: inv.mes, total: 0 };
    }
    map[key].total += inv.montoEjercidoUsd || 0;
  });
  return Object.values(map).sort((a, b) => {
    if (a.year !== b.year) return a.year - b.year;
    return a.month.localeCompare(b.month, 'es');
  });
});

const workUnits = computed(() => {
  if (!dashboardData.value || !selectedContratoId.value) return [];
  const pmt = dashboardData.value.programasMinimosTrabajo.find((p: any) => p.contratoId === selectedContratoId.value);
  if (!pmt) return [];
  return [
    { label: 'Programa mínimo de trabajo', value: pmt.programaMinimoTrabajoUt },
    { label: 'Incremento al PMT', value: pmt.incrementoPmtUt },
    { label: 'Periodo adicional', value: pmt.periodoAdicionalUt },
    { label: 'PMT total', value: pmt.pmtTotalRequerido },
    { label: 'Acreditadas', value: pmt.acreditadasReales },
    { label: 'Fecha límite PMT', value: pmt.fechaLimite },
  ];
});

const productionValueBreakdown = computed(() => {
  if (!selectedContrato.value) return [];
  const pe = selectedContrato.value.participacionEstado || 0;
  return [
    { label: 'Participación contratista', value: Number((100 - pe).toFixed(1)), color: '#006d77' },
    { label: 'Participación del estado', value: Number(pe.toFixed(1)), color: '#83c5be' },
  ];
});

const participationInterestData = computed(() => {
  if (!dashboardData.value || !selectedContratoId.value) return [];
  const contratistas = dashboardData.value.contratistas.filter((c: any) => c.contratoId === selectedContratoId.value);
  const valid = contratistas.filter((c: any) => c.porcentajeParticipacion !== null && c.tipoParticipacion?.toLowerCase() !== 'obligado solidario');
  const colors = ['#1e5b4f', '#2f7d6c', '#5d9b90', '#89b9b0', '#b4d6cf'];
  return valid.map((c: any, index: number) => ({
    label: `${c.empresaNombre}, ${c.tipoParticipacion}`,
    value: c.porcentajeParticipacion || 0,
    color: colors[index % colors.length]
  }));
});
</script>
