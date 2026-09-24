<template>
  <div class="h-[400px] w-full rounded-lg overflow-hidden border border-gray-200 shadow-sm relative z-0">
    <l-map ref="map" :zoom="5" :center="[23.6345, -102.5528]" :use-global-leaflet="false">
      <l-tile-layer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        layer-type="base"
        name="OpenStreetMap"
      ></l-tile-layer>

      <l-polygon v-if="polygonCoords.length > 0" :lat-lngs="polygonCoords" color="#196B24" fillColor="#196B24" :fillOpacity="0.4" />
      <l-marker v-if="polygonCoords.length > 0" :lat-lng="polygonCoords[0]">
        <l-tooltip>{{ surfaceLabel }}</l-tooltip>
      </l-marker>
    </l-map>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import 'leaflet/dist/leaflet.css';
import { LMap, LTileLayer, LPolygon, LMarker, LTooltip } from '@vue-leaflet/vue-leaflet';

const props = defineProps<{
  points: Array<{ latitudDecimales: number; longitudDecimales: number; numeroVertice: number }>;
  surfaceLabel: string;
}>();

const polygonCoords = computed(() => {
  if (!props.points || props.points.length === 0) return [];
  // Sorted by numeroVertice ascending
  return props.points.map(p => [p.latitudDecimales, p.longitudDecimales]);
});
</script>
