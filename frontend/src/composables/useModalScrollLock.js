import { watch, onUnmounted } from 'vue';

/**
 * Composable para bloquear el scroll del body cuando un modal está abierto
 * Preserva la posición del scroll para evitar que la página vuelva al inicio
 * @param {import('vue').Ref<boolean>} mostrar - Referencia reactiva que indica si el modal está visible
 */
export function useModalScrollLock(mostrar) {
  let scrollPosition = 0;

  // Bloquear scroll del body cuando el modal está abierto
  watch(mostrar, (nuevoValor) => {
    if (nuevoValor) {
      // Guardar la posición actual del scroll
      scrollPosition = window.pageYOffset || document.documentElement.scrollTop || document.body.scrollTop || 0;

      // Aplicar la posición guardada al body antes de fijarlo
      document.body.style.top = `-${scrollPosition}px`;
      document.body.classList.add('modal-open');
      document.documentElement.classList.add('modal-open');
    } else {
      // Remover las clases y estilos
      document.body.classList.remove('modal-open');
      document.documentElement.classList.remove('modal-open');
      document.body.style.top = '';

      // Restaurar la posición del scroll
      window.scrollTo(0, scrollPosition);
    }
  });

  // Limpiar al desmontar el componente
  onUnmounted(() => {
    document.body.classList.remove('modal-open');
    document.documentElement.classList.remove('modal-open');
    document.body.style.top = '';
  });
}


