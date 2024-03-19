<template>
  <q-layout view="lhh Lpr lff">
    <q-page-container class="container">
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script setup lang="ts"></script>

<style scoped lang="scss">
.container {
  max-width: 1100px;
  margin: 0 auto;
  padding: 20px;
}
</style>
