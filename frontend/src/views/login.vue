<script setup>
import Encabezado from '../components/layout/encabezado.vue';
import Login from '../components/ui/login.vue';
import Pie from '../components/ui/pie.vue';
</script>

<template>
    <main>
        <Encabezado :sin-menu="true"/>
        <Login />
        <Pie />
    </main>
</template>
