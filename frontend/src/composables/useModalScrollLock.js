import { watch, onUnmounted, onMounted } from 'vue';

/**
 * Composable para bloquear el scroll del body cuando un modal está abierto
 * Preserva la posición del scroll para evitar que la página vuelva al inicio
 * @param {import('vue').Ref<boolean>} mostrar - Referencia reactiva que indica si el modal está visible
 */
export function useModalScrollLock(mostrar) {
  let scrollPosition = 0;
  let originalScrollBehavior = '';

  function bloquearScroll() {
    // Guardar la posición actual del scroll
    // Using globalThis instead of window for better cross-platform compatibility
    scrollPosition = (typeof globalThis !== 'undefined' && globalThis.pageYOffset) || document.documentElement.scrollTop || document.body.scrollTop || 0;

    // Guardar el comportamiento de scroll original
    originalScrollBehavior = document.documentElement.style.scrollBehavior || (typeof globalThis !== 'undefined' && globalThis.getComputedStyle ? globalThis.getComputedStyle(document.documentElement).scrollBehavior : '');

    // Aplicar la posición guardada al body antes de fijarlo
    document.body.style.top = `-${scrollPosition}px`;
    document.body.style.position = 'fixed';
    document.body.style.width = '100%';
    document.body.style.overflow = 'hidden';
    document.body.classList.add('modal-open');
    document.documentElement.classList.add('modal-open');
    document.documentElement.style.overflow = 'hidden';
  }

  function desbloquearScroll() {
    // Desactivar temporalmente scroll-behavior: smooth para evitar animación
    document.documentElement.style.scrollBehavior = 'auto';
    document.body.style.scrollBehavior = 'auto';

    // Remover las clases y estilos
    document.body.classList.remove('modal-open');
    document.documentElement.classList.remove('modal-open');
    document.body.style.top = '';
    document.body.style.position = '';
    document.body.style.width = '';
    document.body.style.overflow = '';
    document.documentElement.style.overflow = '';

    // Restaurar la posición del scroll sin animación usando requestAnimationFrame
    // Using globalThis instead of window for better cross-platform compatibility
    requestAnimationFrame(() => {
      if (typeof globalThis !== 'undefined' && globalThis.scrollTo) {
        globalThis.scrollTo({
          top: scrollPosition,
          left: 0,
          behavior: 'auto'
        });
      } else if (typeof globalThis !== 'undefined' && globalThis.window && globalThis.window.scrollTo) { // NOSONAR: S7764
        globalThis.window.scrollTo({
          top: scrollPosition,
          left: 0,
          behavior: 'auto'
        });
      }

      // Restaurar el comportamiento de scroll original después de restaurar la posición
      requestAnimationFrame(() => {
        if (originalScrollBehavior) {
          document.documentElement.style.scrollBehavior = originalScrollBehavior;
          document.body.style.scrollBehavior = originalScrollBehavior;
        } else {
          document.documentElement.style.scrollBehavior = '';
          document.body.style.scrollBehavior = '';
        }
      });
    });
  }

  // Bloquear scroll del body cuando el modal está abierto
  watch(mostrar, (nuevoValor) => {
    if (nuevoValor) {
      bloquearScroll();
    } else {
      desbloquearScroll();
    }
  }, { immediate: true });

  // También bloquear cuando el componente se monta si ya está visible
  onMounted(() => {
    const valorMostrar = typeof mostrar === 'function' ? mostrar() : (mostrar?.value ?? false);
    if (valorMostrar) {
      bloquearScroll();
    }
  });

  // Limpiar al desmontar el componente
  onUnmounted(() => {
    desbloquearScroll();
  });
}


