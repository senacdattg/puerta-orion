<script setup>
import Encabezado from '../components/layout/encabezado.vue';
import Login from '../components/ui/login.vue';
</script>

<template>
    <main>
        <Encabezado :sin-menu="true"/>
        <Login />
    </main>
</template>
