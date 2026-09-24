<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '../../stores/auth'
import { useRouter } from 'vue-router'
import { Lock, User, LogIn, Info } from 'lucide-vue-next'
import pemexLogo from '../../assets/pemexlogo.png'

const identifier = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)
const showHelp = ref(false)
const year = new Date().getFullYear()

const authStore = useAuthStore()
const router = useRouter()

const handleLogin = async () => {
  if (!identifier.value || !password.value) {
    error.value = 'Por favor ingresa todos los campos'
    return
  }

  loading.value = true
  error.value = ''

  try {
    await authStore.login(identifier.value, password.value)
    router.push({ name: 'home' })
  } catch (err: any) {
    error.value = 'Error: Email o contraseña incorrectos'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-[#f8f9fa] to-[#e9ecef] px-4">
    <div class="max-w-[450px] w-full bg-white rounded-xl shadow-[0_10px_30px_rgba(0,0,0,0.10)] hover:shadow-[0_15px_35px_rgba(0,0,0,0.15)] hover:-translate-y-1 transition-all duration-300 overflow-hidden">
      
      <div class="p-10 pt-10 pb-10">
        <div class="text-center mb-6">
          <img :src="pemexLogo" alt="Pemex" class="w-[180px] h-auto mx-auto mb-4" />
          <h1 class="font-bold text-pemex-primary m-0 mb-1 text-2xl">SAAI</h1>
          <h3 class="font-bold text-pemex-primary m-0 mb-1 text-xl">Iniciar Sesión</h3>
          <p class="text-gray-500 m-0">Ingrese sus credenciales para continuar</p>
        </div>

        <div v-if="error" class="bg-[#fde8ea] text-[#7a1023] border border-[#f3c6cd] p-3 rounded-lg text-sm mb-4">
          {{ error }}
        </div>

        <form @submit.prevent="handleLogin" class="space-y-4">
          <div class="relative">
            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <User class="h-5 w-5 text-gray-500" />
            </div>
            <input v-model="identifier" type="text" required class="focus:ring-pemex-primary focus:border-pemex-primary focus:shadow-[0_0_0_0.2rem_rgba(132,0,22,0.15)] block w-full pl-10 sm:text-base border-gray-300 rounded-lg py-3 border outline-none transition-all text-gray-700" placeholder="Correo electrónico" />
          </div>

          <div class="relative">
            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Lock class="h-5 w-5 text-gray-500" />
            </div>
            <input v-model="password" type="password" required class="focus:ring-pemex-primary focus:border-pemex-primary focus:shadow-[0_0_0_0.2rem_rgba(132,0,22,0.15)] block w-full pl-10 sm:text-base border-gray-300 rounded-lg py-3 border outline-none transition-all text-gray-700" placeholder="Contraseña" />
          </div>

          <button type="submit" :disabled="loading" class="w-full flex justify-center items-center gap-2 py-3 px-4 border border-transparent rounded-lg shadow-sm text-base font-semibold text-white bg-pemex-primary hover:bg-pemex-accent hover:-translate-y-0.5 hover:shadow-[0_5px_15px_rgba(132,0,22,0.30)] focus:outline-none transition-all disabled:opacity-70 disabled:cursor-not-allowed">
            <LogIn v-if="!loading" class="h-5 w-5" />
            <svg v-else class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            {{ loading ? 'Accediendo...' : 'Acceder' }}
          </button>

          <div class="text-center mt-4 pt-2">
            <a href="#" @click.prevent="showHelp = true" class="text-pemex-primary hover:text-pemex-accent hover:underline font-medium transition-colors inline-flex items-center gap-2">
              <Info class="w-4 h-4" />
              ¿Necesitas Ayuda?
            </a>
          </div>

          <div class="text-center mt-4">
            <p class="text-pemex-redlight text-sm font-medium">
              Copyright © {{ year }} Petróleos Mexicanos. Derechos reservados.
            </p>
          </div>
        </form>

        <!-- Help Modal -->
        <div v-if="showHelp" class="fixed inset-0 bg-black/50 backdrop-blur-[3px] flex justify-center items-center z-50">
          <div class="bg-white p-[24px_30px] rounded-[10px] w-[380px] max-w-[90%] shadow-[0_8px_30px_rgba(0,0,0,0.25)] animate-[fadeIn_0.2s_ease-in-out]">
            <h3 class="text-center mb-4 text-[#006847] font-bold text-lg flex items-center justify-center gap-2">
              <Info class="w-5 h-5" /> Contáctanos:
            </h3>

            <h3 class="font-semibold text-gray-800 mb-2 italic">Gerencia de Asuntos Internos</h3>

            <ul class="text-sm text-gray-700 space-y-3 pl-0 list-none">
              <li>
                <b>Coordinación GAI:</b><br/>
                Alejandra Gayosso Cabello<br/>
                <a href="mailto:alejandra.gayosso@pemex.com" class="text-pemex-primary hover:underline">alejandra.gayosso@pemex.com</a>
              </li>

              <li>
                <b>Administrador del Sistema:</b><br/>
                Ing. Jaime Morales García<br/>
                <a href="mailto:jaime.morales@pemex.com" class="text-pemex-primary hover:underline">jaime.morales@pemex.com</a>
              </li>
            </ul>

            <button @click="showHelp = false" class="mt-[18px] w-full p-[10px] bg-[#006847] hover:bg-[#004e34] text-white font-bold rounded-[6px] transition-colors cursor-pointer">
              Cerrar
            </button>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>
