# REQUISITOS FUNCIONALES DEL SISTEMA
## Sistema Administrativo para el Club Deportivo Puerta de Orión

*Versión del Documento:* 1.0  
*Fecha:* Diciembre 2025  
*Estándares:* IEEE 830-1998, ISO/IEC 25010

---

## TABLA DE CONTENIDOS

1. [Introducción](#1-introducción)
2. [Requisitos de Autenticación y Seguridad](#2-requisitos-de-autenticación-y-seguridad)
3. [Requisitos de Registro y Gestión de Usuarios](#3-requisitos-de-registro-y-gestión-de-usuarios)
4. [Requisitos de Gestión de Roles y Permisos](#4-requisitos-de-gestión-de-roles-y-permisos)
5. [Requisitos de Gestión de Deportistas](#5-requisitos-de-gestión-de-deportistas)
6. [Requisitos de Gestión de Acudientes](#6-requisitos-de-gestión-de-acudientes)
7. [Requisitos de Gestión de Mensualidades y Pagos](#7-requisitos-de-gestión-de-mensualidades-y-pagos)
8. [Requisitos de Gestión de Eventos y Calendario](#8-requisitos-de-gestión-de-eventos-y-calendario)
9. [Requisitos de Galería de Imágenes](#9-requisitos-de-galería-de-imágenes)
10. [Requisitos de Perfiles y Actualización de Información](#10-requisitos-de-perfiles-y-actualización-de-información)
11. [Requisitos de Panel de Administración](#11-requisitos-de-panel-de-administración)

---

## 1. INTRODUCCIÓN

Este documento presenta la lista de requisitos funcionales del Sistema Administrativo para el Club Deportivo Puerta de Orión que están implementados y deben ser documentados oficialmente.

*Total de Requisitos Funcionales Documentados: 28*

---

## 2. REQUISITOS DE AUTENTICACIÓN Y SEGURIDAD

*RF-001* *Inicio de Sesión*: El sistema debe permitir a los usuarios iniciar sesión utilizando tipo de documento, número de documento y contraseña.

*RF-002* *Cierre de Sesión*: El sistema debe permitir a los usuarios cerrar sesión de forma segura, invalidando el token actual.

*RF-003* *Recuperación de Contraseña*: El sistema debe permitir a los usuarios solicitar y restablecer su contraseña mediante correo electrónico con token de recuperación.

*RF-004* *Control de Acceso Basado en Roles (RBAC)*: El sistema debe implementar control de acceso basado en roles, restringiendo funcionalidades según el rol del usuario.

---

## 3. REQUISITOS DE REGISTRO Y GESTIÓN DE USUARIOS

*RF-005* *Registro de Usuarios*: El sistema debe permitir a nuevos usuarios registrarse al club, proporcionando información básica personal y credenciales de acceso.

*RF-006* *Registro de Deportistas*: El sistema debe permitir el registro completo de deportistas con información personal, médica, escolar y deportiva.

*RF-007* *Registro de Acudientes*: El sistema debe permitir el registro de acudientes con el número de documento del deportista.

*RF-008* *Registro de Usuarios por Administrador*: El sistema debe permitir a los administradores registrar nuevos usuarios en el sistema.

*RF-009* *Gestión de Usuarios*: El sistema debe permitir a administradores actualizar información, activar/desactivar usuarios y cambiar roles gestionables (entrenador, administrador).

---

## 4. REQUISITOS DE GESTIÓN DE ROLES Y PERMISOS

*RF-010* *Múltiples Roles por Usuario*: El sistema debe permitir que un usuario tenga múltiples roles simultáneamente y seleccionar un rol activo para la sesión actual.

---

## 5. REQUISITOS DE GESTIÓN DE DEPORTISTAS

*RF-011* *Gestión de Deportistas*: El sistema debe permitir listar, buscar, actualizar y gestionar el estado de deportistas registrados, con paginación y filtros por categoría y estado.

*RF-012* *Asociar Acudiente a Deportista*: El sistema debe permitir asociar un acudiente existente a un deportista.

---

## 6. REQUISITOS DE GESTIÓN DE ACUDIENTES

*RF-013* *Visualización de Información del Deportista*: El sistema debe permitir a un acudiente ver la información completa de todos los deportistas a su cargo, incluyendo datos personales, mensualidades y eventos.

*RF-014* *Asociación de Deportistas*: El sistema debe permitir a un acudiente asociar deportistas a su cuenta.

---

## 7. REQUISITOS DE GESTIÓN DE MENSUALIDADES Y PAGOS

*RF-015* *Gestión de Mensualidades*: El sistema debe permitir a administradores crear, actualizar, activar, desactivar, buscar y filtrar mensualidades para deportistas por estado (Pagado, Pendiente, Vencido).

*RF-016* *Cálculo y Actualización de Saldo*: El sistema debe calcular automáticamente el saldo pendiente de una mensualidad basándose en los abonos realizados y actualizar el estado cuando el saldo llega a cero.

*RF-017* *Validación de Mensualidades*: El sistema debe prevenir la creación de mensualidades duplicadas para el mismo deportista en el mismo mes y año.

*RF-018* *Gestión de Abonos*: El sistema debe permitir registrar, ver, actualizar y eliminar abonos a una mensualidad, validando que el monto no supere el saldo pendiente.

*RF-019* *Integración con MercadoPago*: El sistema debe permitir crear preferencias de pago en MercadoPago para mensualidades o abonos.

---

## 8. REQUISITOS DE GESTIÓN DE EVENTOS Y CALENDARIO

*RF-020* *Gestión de Eventos*: El sistema debe permitir a administradores y entrenadores crear, eliminar, ver y actualizar eventos.

*RF-021* *Calendario de Eventos*: El sistema debe proporcionar una vista de calendario con todos los eventos organizados por fecha.

---

## 9. REQUISITOS DE GALERÍA DE IMÁGENES

*RF-022* *Gestión de Imágenes*: El sistema debe permitir a administradores crear, actualizar, ver y eliminar imágenes de la galería, con validación de tipo de archivo y tamaño máximo.

---

## 10. REQUISITOS DE PERFILES Y ACTUALIZACIÓN DE INFORMACIÓN

*RF-023* *Gestión de Perfil Propio*: El sistema debe permitir a los usuarios ver y actualizar su propio perfil completo con toda la información asociada.

---

## 11. REQUISITOS DE PANEL DE ADMINISTRACIÓN

*RF-024* *Acceso al Panel de Administración*: El sistema debe proporcionar un panel de administración accesible solo para SuperAdmin y Administrador.

*RF-025* *Gestión desde Panel*: El sistema debe proporcionar interfaces en el panel de administración para gestionar usuarios y datos dinámicos del sistema.

---

## RESUMEN

*Total de Requisitos Funcionales Documentados: 26*

El sistema implementa un total de 26 requisitos funcionales esenciales organizados en 11 módulos principales, cubriendo las áreas críticas de operación del Club Deportivo Puerta de Orión.

---

*Documento generado mediante análisis exhaustivo del código fuente y documentación existente.*

*Última actualización*: Diciembre 2025