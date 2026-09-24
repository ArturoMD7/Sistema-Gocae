<script setup lang="ts">
import { useAuthStore } from '../stores/auth'
import { useRouter } from 'vue-router'
import { LogOut, Home, FileText, User, Users, Settings, Database } from 'lucide-vue-next'
import logoMin from '../assets/logo_min.png'
import { ref } from 'vue'

const authStore = useAuthStore()
const router = useRouter()
const isSidebarExpanded = ref(true)

const handleLogout = () => {
  authStore.logout()
  router.push({ name: 'login' })
}
</script>

<template>
  <div class="flex h-screen overflow-hidden">
    <!-- Sidebar -->
    <aside :class="['bg-white text-[#333] transition-all duration-300 flex flex-col border-r border-[#e0e0e0] shadow-[4px_0_10px_rgba(0,0,0,0.05)] z-50 shrink-0', isSidebarExpanded ? 'w-[260px]' : 'w-[70px]']" @mouseenter="isSidebarExpanded = true" @mouseleave="isSidebarExpanded = false">
      
      <!-- Sidebar Header -->
      <div class="py-[11px] px-[20px] flex items-center bg-[#1e5b4f] shadow-[0_2px_5px_rgba(0,0,0,0.1)] overflow-hidden whitespace-nowrap h-[60px]" :class="isSidebarExpanded ? 'justify-start' : 'justify-center px-0'">
        <img :src="logoMin" alt="Pemex" class="w-[40px] max-w-[40px] h-auto object-contain block transition-all duration-300 mx-auto" :class="isSidebarExpanded ? 'mx-0' : ''" />
        <span class="text-white font-bold text-[1.4rem] ml-[15px] transition-all duration-300 inline-block overflow-hidden" :class="isSidebarExpanded ? 'opacity-100 max-w-[200px]' : 'opacity-0 max-w-0 ml-0'">GOCAE</span>
      </div>
      
      <!-- Sidebar Nav -->
      <nav class="flex-1 py-[20px] overflow-y-auto overflow-x-hidden">
        <ul class="m-0 p-0 list-none">
          <li class="m-[8px_12px]">
            <router-link :to="{ name: 'home' }" class="flex items-center text-[#555] no-underline p-[14px_16px] rounded-[8px] transition-all duration-200 w-full text-left font-[inherit] text-[0.95rem] whitespace-nowrap hover:bg-[rgba(30,91,79,0.08)] hover:text-[#1e5b4f]" exact-active-class="!bg-[#1e5b4f] !text-white shadow-[0_4px_6px_rgba(30,91,79,0.2)]" :class="!isSidebarExpanded ? 'justify-center !px-0' : ''">
              <span class="text-[1.3rem] min-w-[24px] flex items-center justify-center transition-transform duration-200 group-hover:scale-110">
                <Home class="w-5 h-5" />
              </span>
              <span class="ml-[16px] font-medium transition-all duration-300" :class="isSidebarExpanded ? 'opacity-100' : 'opacity-0 hidden'">Inicio</span>
            </router-link>
          </li>
          
          <li class="m-[8px_12px]">
            <router-link :to="{ name: 'contracts' }" class="flex items-center text-[#555] no-underline p-[14px_16px] rounded-[8px] transition-all duration-200 w-full text-left font-[inherit] text-[0.95rem] whitespace-nowrap hover:bg-[rgba(30,91,79,0.08)] hover:text-[#1e5b4f]" active-class="!bg-[#1e5b4f] !text-white shadow-[0_4px_6px_rgba(30,91,79,0.2)]" :class="!isSidebarExpanded ? 'justify-center !px-0' : ''">
              <span class="text-[1.3rem] min-w-[24px] flex items-center justify-center transition-transform duration-200 group-hover:scale-110">
                <FileText class="w-5 h-5" />
              </span>
              <span class="ml-[16px] font-medium transition-all duration-300" :class="isSidebarExpanded ? 'opacity-100' : 'opacity-0 hidden'">Contratos</span>
            </router-link>
          </li>

          <!-- Users Menu (Admin Only) -->
          <li v-if="authStore.isAdmin" class="m-[8px_12px]">
            <router-link :to="{ name: 'users' }" class="flex items-center text-[#555] no-underline p-[14px_16px] rounded-[8px] transition-all duration-200 w-full text-left font-[inherit] text-[0.95rem] whitespace-nowrap hover:bg-[rgba(30,91,79,0.08)] hover:text-[#1e5b4f]" active-class="!bg-[#1e5b4f] !text-white shadow-[0_4px_6px_rgba(30,91,79,0.2)]" :class="!isSidebarExpanded ? 'justify-center !px-0' : ''">
              <span class="text-[1.3rem] min-w-[24px] flex items-center justify-center transition-transform duration-200 group-hover:scale-110">
                <Users class="w-5 h-5" />
              </span>
              <span class="ml-[16px] font-medium transition-all duration-300" :class="isSidebarExpanded ? 'opacity-100' : 'opacity-0 hidden'">Usuarios</span>
            </router-link>
          </li>
        </ul>
      </nav>

      <!-- Sidebar Footer -->
      <div class="p-[16px_12px] border-t border-[#eeeeee] bg-[#fcfcfc]">
        <ul class="m-0 p-0 list-none">
          <li class="m-[8px_12px]">
            <router-link :to="{ name: 'settings' }" class="flex items-center text-[#555] no-underline p-[14px_16px] rounded-[8px] transition-all duration-200 w-full text-left font-[inherit] text-[0.95rem] whitespace-nowrap hover:bg-[rgba(30,91,79,0.08)] hover:text-[#1e5b4f]" active-class="!bg-[#1e5b4f] !text-white shadow-[0_4px_6px_rgba(30,91,79,0.2)]" :class="!isSidebarExpanded ? 'justify-center !px-0' : ''">
              <span class="text-[1.3rem] min-w-[24px] flex items-center justify-center transition-transform duration-200 group-hover:scale-110">
                <Settings class="w-5 h-5" />
              </span>
              <span class="ml-[16px] font-medium transition-all duration-300" :class="isSidebarExpanded ? 'opacity-100' : 'opacity-0 hidden'">Ajustes</span>
            </router-link>
          </li>
          <li class="m-[8px_12px]">
            <button @click="handleLogout" class="flex items-center text-[#555] no-underline p-[14px_16px] rounded-[8px] transition-all duration-200 w-full text-left font-[inherit] text-[0.95rem] whitespace-nowrap hover:bg-[rgba(30,91,79,0.08)] hover:text-[#1e5b4f] border-none bg-transparent cursor-pointer" :class="!isSidebarExpanded ? 'justify-center !px-0' : ''">
              <span class="text-[1.3rem] min-w-[24px] flex items-center justify-center transition-transform duration-200 group-hover:scale-110">
                <LogOut class="w-5 h-5" />
              </span>
              <span class="ml-[16px] font-medium transition-all duration-300" :class="isSidebarExpanded ? 'opacity-100' : 'opacity-0 hidden'">Cerrar Sesión</span>
            </button>
          </li>
        </ul>
      </div>
    </aside>

    <!-- Main Content -->
    <main class="flex-1 flex flex-col w-full min-w-0 bg-[#f4f7fa]">
      
      <!-- Top Header -->
      <header class="h-[60px] p-[5px_20px] flex items-center justify-between bg-gradient-to-b from-[#1e5b4f] to-[#024e47] text-white border-b border-white/10 shadow-[0_2px_10px_rgba(0,0,0,0.1)] font-semibold text-[1.2rem] shrink-0">
        <h1 class="m-0 text-white font-bold text-[1.2rem]">Sistema de Gestión de Contratos</h1>
        
        <router-link v-if="authStore.user" :to="`/user-info/${authStore.user.id}`" class="flex items-center gap-[15px] cursor-pointer p-[5px_10px] rounded-[8px] transition-colors duration-200 hover:bg-white/10" title="Ver mi información">
          <span class="text-[0.95rem] font-medium text-white">
            <strong>{{ authStore.user?.first_name }} {{ authStore.user?.last_name || authStore.user?.username }}</strong>
          </span>
          <div class="w-[36px] h-[36px] rounded-full overflow-hidden bg-[#f0f0f0] flex items-center justify-center border-2 border-white/30 text-gray-400">
            <User v-if="!authStore.user?.profile_picture" class="w-5 h-5" />
            <img v-else :src="authStore.user.profile_picture" alt="Avatar" class="w-full h-full object-cover" />
          </div>
        </router-link>
      </header>

      <div class="flex-1 overflow-x-auto p-0">
        <router-view></router-view>
      </div>
    </main>
  </div>
</template>
