"""
Módulo para configurar tareas programadas (scheduled tasks) usando APScheduler.

Responsabilidad:
- Configurar y ejecutar tareas automáticas del sistema.
- Gestionar el scheduler de manera centralizada.
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from flask import Flask
from ..utils.logger import obtener_registrador

logger = obtener_registrador('aplicacion')
scheduler = None


def init_scheduler(app: Flask) -> None:
    """
    Inicializa el scheduler con las tareas programadas.
    
    Args:
        app: Instancia de la aplicación Flask.
    """
    global scheduler
    
    if scheduler is not None:
        logger.warning("Scheduler ya está inicializado")
        return
    
    scheduler = BackgroundScheduler()
    scheduler.start()
    
    # Configurar tareas
    _configure_scheduled_tasks(app)
    
    logger.info("Scheduler inicializado exitosamente")


def _configure_scheduled_tasks(app: Flask) -> None:
    """
    Configura las tareas programadas del sistema.
    
    Args:
        app: Instancia de la aplicación Flask.
    """
    # Ejecutar renovación automática de mensualidades diariamente a las 2:00 AM
    scheduler.add_job(
        func=_renovar_mensualidades_automaticamente,
        trigger=CronTrigger(hour=2, minute=0),  # Ejecutar todos los días a las 2:00 AM
        args=[app],
        id='renovar_mensualidades',
        name='Renovación automática de mensualidades',
        replace_existing=True,
        max_instances=1  # Solo una instancia a la vez
    )
    
    logger.info("Tarea de renovación automática de mensualidades programada: Diariamente a las 2:00 AM")


def _renovar_mensualidades_automaticamente(app: Flask) -> None:
    """
    Ejecuta la renovación automática de mensualidades.
    Esta función se ejecuta dentro del contexto de la aplicación Flask.
    
    Args:
        app: Instancia de la aplicación Flask.
    """
    with app.app_context():
        try:
            from ..routes.mensualidades_routes import _renovar_mensualidades_automaticamente
            
            logger.info("Iniciando renovación automática de mensualidades...")
            resultado = _renovar_mensualidades_automaticamente()
            
            if resultado.get('success'):
                logger.info(
                    "Renovación automática completada: %d renovadas, %d bloqueadas",
                    resultado.get('renovadas', 0),
                    resultado.get('bloqueadas', 0)
                )
            else:
                logger.error(
                    "Error en renovación automática: %s",
                    resultado.get('error', 'Error desconocido')
                )
        except Exception as exc:
            logger.error("Error ejecutando renovación automática: %s", str(exc))


def shutdown_scheduler() -> None:
    """Detiene el scheduler de manera segura."""
    global scheduler
    
    if scheduler is not None:
        scheduler.shutdown()
        scheduler = None
        logger.info("Scheduler detenido")


def get_scheduler() -> BackgroundScheduler | None:
    """
    Obtiene la instancia del scheduler.
    
    Returns:
        Instancia del scheduler o None si no está inicializado.
    """
    return scheduler


def get_scheduler_status() -> dict:
    """
    Obtiene el estado del scheduler y las tareas programadas.
    
    Returns:
        Diccionario con el estado del scheduler y las tareas programadas.
    """
    if scheduler is None:
        return {
            'activo': False,
            'tareas': [],
            'mensaje': 'Scheduler no inicializado'
        }
    
    jobs = []
    for job in scheduler.get_jobs():
        next_run = job.next_run_time
        jobs.append({
            'id': job.id,
            'nombre': job.name,
            'proxima_ejecucion': next_run.isoformat() if next_run else None,
            'activo': job.next_run_time is not None
        })
    
    return {
        'activo': scheduler.running,
        'tareas': jobs,
        'total_tareas': len(jobs)
    }

