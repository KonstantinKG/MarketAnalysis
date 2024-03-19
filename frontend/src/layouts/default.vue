<template>
  <q-layout view="lhh Lpr lff">
    <q-page-container class="container">
      <router-view />
    </q-page-container>

    <!--    <q-drawer-->
    <!--      v-model="drawer"-->
    <!--      :width="200"-->
    <!--      :breakpoint="700"-->
    <!--      bordered-->
    <!--    >-->
    <!--      <q-scroll-area class="fit">-->
    <!--        <div class="q-pa-sm">-->
    <!--          <div v-for="n in 50" :key="n">Drawer {{ n }} / 50</div>-->
    <!--        </div>-->
    <!--      </q-scroll-area>-->
    <!--    </q-drawer>-->
  </q-layout>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const drawer = ref(true)
</script>

<style scoped lang="scss">
.container {
  max-width: 1100px;
  margin: 0 auto;
  padding: 20px;
}
</style>
