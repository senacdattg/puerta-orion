<script setup>
import Encabezado from '../components/iu/encabezado.vue';
import Login from '../components/iu/login.vue'
import Pie from '../components/iu/pie.vue';
</script>

<template>
    <main>
        <Encabezado :sin-menu="true"/>
        <Login />
        <Pie />
    </main>
</template>
