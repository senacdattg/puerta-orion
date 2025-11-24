import { watch, onUnmounted } from 'vue';

/**
 * Composable para bloquear el scroll del body cuando un modal está abierto
 * @param {import('vue').Ref<boolean>} mostrar - Referencia reactiva que indica si el modal está visible
 */
export function useModalScrollLock(mostrar) {
  // Bloquear scroll del body cuando el modal está abierto
  watch(mostrar, (nuevoValor) => {
    if (nuevoValor) {
      document.body.classList.add('modal-open');
      document.documentElement.classList.add('modal-open');
    } else {
      document.body.classList.remove('modal-open');
      document.documentElement.classList.remove('modal-open');
    }
  });

  // Limpiar al desmontar el componente
  onUnmounted(() => {
    document.body.classList.remove('modal-open');
    document.documentElement.classList.remove('modal-open');
  });
}


