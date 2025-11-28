# PROYECTO DE SISTEMATIZACIÓN PUERTA DE ORIÓN

**Sistema Administrativo para el Club Deportivo Puerta de Orión**

---

## Tabla de Contenidos

- [Información del Proyecto](#información-del-proyecto)
- [Descripción General](#descripción-general)
- [Objetivos](#objetivos)
- [Arquitectura del Sistema](#arquitectura-del-sistema)
- [Tecnologías Utilizadas](#tecnologías-utilizadas)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Descripción de Módulos](#descripción-de-módulos)
- [Flujos Principales del Sistema](#flujos-principales-del-sistema)
- [Modelo de Datos](#modelo-de-datos)
- [Reglas de Negocio](#reglas-de-negocio)
- [Requerimientos del Sistema](#requerimientos-del-sistema)
- [Instalación](#instalación)
- [Configuración](#configuración)
- [Ejecución](#ejecución)
- [Endpoints API](#endpoints-api)
- [Despliegue](#despliegue)
- [Plan de Desarrollo](#plan-de-desarrollo)
- [Contribución](#contribución)
- [Licencia](#licencia)
- [Contacto](#contacto)

---

## Información del Proyecto

| Campo | Información |
|-------|-------------|
| **Nombre del Proyecto** | PROYECTO DE SISTEMATIZACIÓN PUERTA DE ORIÓN |
| **Fecha de Inicio** | 11 de Diciembre de 2024 |
| **Fecha de Finalización Estimada** | 19 de Diciembre de 2025 |
| **Institución** | Servicio Nacional de Aprendizaje (SENA) |
| **Centro** | Centro De Desarrollo Agroindustrial, Turístico Y Tecnológico Del Guaviare (CDATTG) |
| **Programa de Formación** | Análisis y Desarrollo de Software (ADSO) |
| **Ficha** | 2923560 |
| **Instructor** | Jhon Hader Rodríguez Perdomo |

### Equipo de Desarrollo

- **KEVIN SANTIAGO PRADA CASTELLANOS**
- **MARIO ALEXANDER CAÑOLA CANO**
- **JHON DEIBY OLARTE BENITEZ**

---

## Descripción General

El sistema administrativo para el **CLUB DEPORTIVO PUERTA DE ORIÓN** es una solución digital desarrollada para optimizar y centralizar los procesos administrativos del club de voleibol ubicado en San José del Guaviare. El sistema busca automatizar el registro y gestión de información de deportistas, reduciendo la carga administrativa que actualmente recae sobre el entrenador, quien debe gestionar manualmente los datos en archivos de Excel.

### Breve Resumen del Proyecto

El CLUB DEPORTIVO PUERTA DE ORIÓN necesita un sistema administrativo que facilite la gestión de información de sus jugadores. Actualmente, el registro y seguimiento de datos como nombres, edades, categorías, pagos de mensualidades y datos antropométricos se realiza manualmente mediante archivos en Excel, lo que representa una carga de trabajo considerable para el entrenador, ya que es el encargado de la administración del club.

El proyecto busca desarrollar una solución digital que automatice estos procesos, permitiendo un almacenamiento eficiente mediante una base de datos estructurada, reduciendo el tiempo invertido en tareas administrativas y procesos agotadores de contabilización. Con esta implementación, se optimizará la gestión del club, permitiendo al entrenador dedicar tiempo a la preparación de los entrenamientos de sus deportistas.

### Justificación y Necesidad del Software

Actualmente, la administración del CLUB PUERTA DE ORIÓN recae en una sola persona, quien debe gestionar manualmente los datos de numerosos jugadores, estos datos son guardados en archivos de Excel. El proceso representa bastante tiempo para el entrenador, que es el responsable de la administración del club. Como consecuencia, se reduce el tiempo disponible para la planificación de los entrenamientos.

La solución digital permitirá la gestión del club mediante una plataforma que les permitirá a los deportistas registrar sus datos personales y así mismo actualizarlos de manera sencilla. Esto reducirá la carga administrativa del entrenador y minimizará errores en la digitación, garantizando una gestión más eficiente de la información.

Además, el sistema ofrecerá funcionalidades adicionales, como la vista y pago de mensualidades, un perfil con datos personales para el deportista y para el administrador, una vista de perfiles de todos sus deportistas y sus mensualidades. La digitalización del proceso también garantizará mayor seguridad y respaldo de la información, evitando pérdidas o inconsistencias en los registros.

### Problemas que Resuelve

El sistema busca solucionar la problemática que tiene el administrador y el entrenador del club al gestionar la información de sus jugadores. Actualmente, este proceso se realiza manualmente en un archivo de Excel con datos que se recogen de un formulario enviado a cada deportista, lo que significa una inversión de tiempo en la digitación de datos.

**Problemas identificados:**

- Pérdida de datos por errores humanos o fallos en el almacenamiento
- Dificultad en la actualización y consulta rápida de información relevante
- Falta de automatización en la gestión e información de pagos
- Carga administrativa excesiva para el entrenador, que también actúa como administrador
- Reducción del tiempo disponible para la planificación de entrenamientos

**Solución implementada:**

- Aplicación web con base de datos en línea que guarda la información en tiempo real
- Filtro de búsqueda para la consulta y actualización de información
- Registro de asistencia más rápido
- Historial de los pagos realizados
- Centralización de datos en una única plataforma

---

## Objetivos

### Objetivo General

Desarrollar un sistema administrativo para el CLUB DEPORTIVO PUERTA DE ORIÓN que automatice el registro de la información de los deportistas. Reduciendo la carga administrativa del entrenador y minimizando errores en el registro de los datos. Nuestro sistema también permitirá que el administrador consulte información de deportistas y sus mensualidades. Tanto el deportista puede consultar sus datos, actualizarlos, informarse sobre sus mensualidades y ver el contenido de la página web; el deportista, al estar enlazado a un acudiente, este también podrá estar actualizado acerca de la información anterior dicha del deportista que acude.

### Objetivos Específicos

- Diseñar una base de datos estructurada que almacene la información de los jugadores, incluyendo datos personales (primer nombre, segundo nombre, primer apellido, segundo apellido, tipo de documento, número de documento, edad, categorías, fecha de nacimiento, número de teléfono, correo electrónico, sexo, tipo de sangre, ciudad donde se radica, con qué institución se respalda el deportista, afiliación de EPS, dirección, si el perfil se encuentra activo o inactivo, alguna enfermedad).

- Implementar una interfaz intuitiva que permita a los aspirantes, deportistas, entrenadores y administradores del sistema registrar, actualizar y ver sus datos de manera rápida y segura, también que pueda ser fácil ejecutar los diferentes apartados de la página web, como: Inscribirse, mensualidades, perfil, jugadores, inicio, calendario y galería.

- Optimizar la gestión administrativa del entrenador mediante la automatización del registro y consulta de información de los deportistas, reduciendo el tiempo invertido en estas tareas y permitiéndole enfocarse en la planificación estratégica del club.

- Garantizar la seguridad y organización de los datos mediante sistemas de acceso controlado y almacenamiento eficiente.

- Facilitar el acceso rápido a la información para mejorar la planificación y seguimiento de los entrenamientos.

---

## Arquitectura del Sistema

### Modelo Arquitectónico

El sistema se desarrollará bajo una **arquitectura Cliente-Servidor**, en la que la interacción entre los usuarios y el servidor se gestionará a través de una plataforma web. Esta arquitectura permite una separación clara entre el cliente y el servidor, lo que facilita la escalabilidad y el mantenimiento del sistema, permitiendo a los usuarios acceder de manera eficiente a las funcionalidades del sistema desde cualquier dispositivo con acceso a Internet.

Para organizar la lógica interna del software en el servidor, se adoptará el **patrón de diseño Modelo-Vista-Controlador (MVC)**. Este patrón divide la aplicación en tres componentes principales:

- **Modelo**: Gestiona la lógica de negocio y los datos del sistema, interactuando con la base de datos y procesando las solicitudes del usuario.

- **Vista**: Es la interfaz de usuario que presenta los datos al usuario y maneja las interacciones visuales. En este caso, la vista será la plataforma web donde los usuarios (aspirantes, deportistas, acudientes, entrenadores y administradores) podrán interactuar con el sistema de manera intuitiva.

- **Controlador**: Actúa como intermediario entre el modelo y la vista, gestionando las solicitudes del usuario, procesando la lógica y actualizando la interfaz con los datos apropiados.

### Componentes Principales del Sistema

```
┌─────────────────────────────────────────────────────────┐
│                    Cliente (Frontend)                   │
│              Plataforma Web (Vue.js)                    │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP/REST
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Servidor (Backend)                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│  │ Controlador│ │  Modelo  │  │   Vista   │          │
│  │ (Flask) │ │ (Flask) │  │  (Vue.js) │          │
│  └──────────┘  └──────────┘  └──────────┘          │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
            ┌─────────────────┐
            │   Base de Datos │
            │     (MySQL)      │
            └─────────────────┘
```

### Componentes del Sistema

- **Cliente**: La plataforma web es el interfaz de acceso para los usuarios (aspirantes, deportistas, acudientes, entrenadores y administradores), que podrán interactuar con el sistema de forma eficiente y amigable.

- **Servidor**: Es el encargado de gestionar la lógica de negocio y facilitar la comunicación con la base de datos, asegurando que las solicitudes de los usuarios se procesen adecuadamente.

- **Base de Datos**: Almacena la información clave del sistema, como datos de los usuarios, entrenamientos, pagos y demás datos relevantes, proporcionando acceso rápido y seguro a los datos.

### Principios de Desarrollo Aplicados

#### Modularidad

El sistema estará dividido en módulos independientes, facilitando su mantenimiento y actualización. Los módulos principales son: Inscribirse, mensualidades, perfil, jugadores, inicio, calendario y galería.

**¿Por qué es importante?**

La modularidad facilita el mantenimiento, la actualización y la escalabilidad del sistema. Al dividir el software en módulos independientes, cada uno con una responsabilidad específica, se puede modificar o actualizar un módulo sin afectar el funcionamiento de los demás. Esto permite realizar correcciones, mejoras o adaptaciones de manera más eficiente, reduciendo el riesgo de introducir errores en otras partes del sistema.

#### Escalabilidad

La arquitectura permitirá futuras expansiones sin comprometer el rendimiento. La escalabilidad es la capacidad que tiene el sistema para adaptarse y funcionar correctamente cuando la carga de trabajo (número de datos) crece, sin que se pierda calidad ni eficiencia.

**¿Por qué es importante?**

La escalabilidad asegura que un sistema pueda adaptarse eficientemente a un aumento en la carga de trabajo o a un crecimiento en la demanda, sin comprometer su rendimiento ni su eficiencia. Un sistema escalable está diseñado con la capacidad de expandirse de manera fluida, permitiendo añadir recursos de acuerdo con las necesidades que vayan surgiendo, sin causar caídas en el desempeño ni generar cuellos de botella.

#### Seguridad

Se implementarán buenas prácticas para proteger los datos personales de los jugadores y garantizar un acceso controlado (esto significa que solo podrán tener acceso a los datos, los administradores). La seguridad son las medidas que se toman para proteger datos y asegurar que solo las personas autorizadas accedan a cierta información o realicen ciertas acciones en el sistema.

**¿Por qué es importante?**

La seguridad es un aspecto crítico en cualquier sistema, ya que protege la información sensible de los usuarios y asegura la integridad de los datos. Implementar medidas de seguridad efectivas evita accesos no autorizados y protege contra posibles amenazas externas e internas, como ataques cibernéticos o el robo de información.

#### Mantenibilidad

Se implementarán buenas prácticas para asegurar que el sistema sea fácil de mantener y actualizar a lo largo del tiempo. Esto incluye el uso de un código modular y bien documentado, lo que permitirá realizar modificaciones o adiciones sin afectar el funcionamiento general del sistema.

**¿Por qué es importante?**

La mantenibilidad garantiza que el sistema pueda seguir funcionando de manera eficiente y efectiva a lo largo del tiempo, incluso a medida que cambian las necesidades del negocio, los usuarios o las tecnologías. Un sistema fácil de mantener puede adaptarse rápidamente a nuevas demandas, ya sea para agregar nuevas funcionalidades, optimizar el rendimiento o corregir errores sin la necesidad de una reescritura completa.

---

## Tecnologías Utilizadas

### Lenguajes de Programación

#### JavaScript

JavaScript es un lenguaje de programación fundamental en el desarrollo web, conocido por su capacidad para crear páginas web interactivas y dinámicas. JavaScript permite que las páginas web reaccionen de manera dinámica ante las acciones de los usuarios, proporcionando una experiencia interactiva e inmersiva.

**Características de JavaScript:**

- Se ejecuta en el navegador para mejorar la experiencia del usuario
- También se puede usar en el backend con Node.js
- No necesita compilación previa; el navegador lo interpreta en tiempo de ejecución
- Es un lenguaje de tipado dinámico
- Soporta programación imperativa, orientada a objetos y funcional
- Usa eventos y funciones callback para manejar acciones sin bloquear el flujo de ejecución
- Permite manejar asincronía con Promises y async/await
- Puede modificar estructuras HTML y estilos CSS en tiempo real (DOM Manipulation)
- Funciona en casi todos los navegadores modernos sin necesidad de instalación adicional

#### Python

Python es un lenguaje de programación de alto nivel, interpretado y de propósito general, conocido por su sintaxis clara y legible. Python es ampliamente utilizado en el desarrollo web del lado del servidor, especialmente con frameworks como Flask y Django. Python se ha convertido en uno de los lenguajes más populares para crear aplicaciones web dinámicas e interactivas.

**Características principales de Python:**

- Lenguaje interpretado que se ejecuta en el servidor
- Sintaxis clara y legible que facilita el mantenimiento del código
- Soporta múltiples bases de datos mediante ORMs como SQLAlchemy (MySQL, PostgreSQL, SQLite)
- Amplia comunidad y abundante documentación
- Lenguaje de código abierto
- Soporta programación orientada a objetos, funcional e imperativa
- Gran ecosistema de librerías y frameworks (Flask, Django, FastAPI)
- Facilita la integración con bases de datos mediante ORMs
- Ideal para desarrollo rápido de aplicaciones web mediante frameworks como Flask

### Frameworks y Herramientas

#### Vue.js

Vue.js es un framework progresivo de JavaScript diseñado para la construcción de interfaces de usuario interactivas y aplicaciones web de una sola página (SPA). Este framework se destaca por su flexibilidad, lo que permite que se pueda integrar fácilmente en proyectos existentes sin requerir una reestructuración completa.

**Características:**

- Enfoque basado en componentes reutilizables
- Sistema reactivo que refleja cambios inmediatamente en la interfaz
- Compatible con herramientas modernas como Vue Router y Pinia (gestión de estado)
- Facilita la creación de aplicaciones modulares y escalables
- Uso de Composition API y composables para lógica reutilizable

**Tecnologías Frontend utilizadas:**

- **Vue.js 3.5.18**: Framework principal
- **Vite 7.0.6**: Build tool y dev server
- **Pinia 3.0.3**: Gestión de estado (reemplazo de Vuex)
- **Vue Router 4.5.1**: Enrutamiento
- **Axios 1.12.2**: Cliente HTTP para API
- **Bootstrap 5.3.7**: Framework CSS
- **Tailwind CSS 4.1.12**: Utility-first CSS
- **SweetAlert2**: Alertas y modales
- **MercadoPago SDK**: Integración de pagos en frontend

#### Python y Flask

Flask es un framework web ligero de Python que facilita el desarrollo de aplicaciones web de manera rápida, eficiente y estructurada. Flask sigue el patrón de diseño Modelo-Vista-Controlador (MVC), lo que mejora la organización del código y facilita su mantenimiento a largo plazo.

**Características de Flask:**

- Separa la lógica de la aplicación (Modelo) de la presentación (Vista) y el control de datos (Controlador)
- Facilita la organización del código y su mantenimiento
- Proporciona SQLAlchemy ORM para interacción sencilla con bases de datos
- Sistema de rutas intuitivo y flexible mediante decoradores
- Sistema de migraciones con Flask-Migrate (Alembic) para gestión de esquemas de bases de datos
- Sistema de autenticación mediante JWT y decoradores personalizados
- Extensibilidad mediante blueprints para modularizar la aplicación
- Integración con herramientas modernas de desarrollo Python

**Tecnologías Backend utilizadas:**

- **Flask ≥3.1.0**: Framework web principal
- **SQLAlchemy 2.0.43**: ORM para base de datos
- **Flask-Migrate 4.0.7**: Migraciones de esquema
- **Flask-CORS 4.0.1**: Manejo de CORS
- **PyJWT 2.8.0**: Autenticación JWT
- **Flask-SQLAlchemy 3.1.1**: Integración SQLAlchemy con Flask
- **PyMySQL 1.1.0**: Driver MySQL
- **MercadoPago SDK 2.3.0**: Integración de pagos
- **Alembic 1.13.1**: Herramienta de migraciones
- **pytest 8.3.4**: Framework de testing
- **pytest-flask 1.3.0**: Extensión Flask para pytest
- **pytest-cov 6.0.0**: Cobertura de código

#### HTML (HyperText Markup Language)

HTML es el lenguaje estándar utilizado para crear y estructurar el contenido de las páginas web. Como lenguaje de marcado, HTML define la estructura básica de un sitio web mediante el uso de etiquetas.

#### CSS (Cascading Style Sheets)

CSS es un lenguaje de hojas de estilo utilizado para definir la presentación visual de las páginas web. A través de CSS, podemos establecer características como colores, tipografías, márgenes, espaciados, tamaños de los elementos, alineación, efectos de transición y mucho más.

### Bases de Datos y Servicios en la Nube

#### MySQL

MySQL es un sistema de gestión de bases de datos relacional (RDBMS) de código abierto, ampliamente utilizado para el almacenamiento y gestión de datos en aplicaciones web y otras plataformas. MySQL se basa en el lenguaje de consulta estructurado SQL, lo que permite a los desarrolladores manipular y gestionar datos de manera eficiente.

**Características:**

- Sigue el modelo relacional
- Escalable para manejar desde pequeñas hasta grandes bases de datos
- Compatible con varios sistemas operativos
- Se integra fácilmente con lenguajes de programación como Python, Java, Node.js y PHP
- Soporta transacciones ACID (Atomicidad, Consistencia, Aislamiento y Durabilidad)

### Herramientas de Desarrollo

#### Git y GitHub

**Git**: Sistema de control de versiones distribuido que permite a los desarrolladores registrar los cambios realizados en los archivos de un proyecto, proporcionando un historial completo de todas las modificaciones.

**GitHub**: Plataforma de desarrollo colaborativo basada en la nube, ampliamente utilizada para el almacenamiento, gestión y colaboración en proyectos de código. Funciona sobre el sistema de control de versiones Git.

#### Herramientas de Diagramación

- **Lucidchart**: Herramienta de diagramación en línea para crear diagramas visuales en tiempo real
- **Draw.io**: Herramienta de diagramación en línea para crear diagramas de flujo, organigramas, diagramas UML
- **Moqups**: Herramienta en línea para la creación de prototipos, diagramas y maquetas de interfaces de usuario (UI)

#### IDE

- **Visual Studio Code**: IDE utilizado para el desarrollo del backend, soporta múltiples lenguajes de programación, es ligero, cuenta con muchas extensiones, tiene control de versiones e incluye una terminal

### Metodologías y Estándares

#### Metodología de Desarrollo

- **Scrum**: Marco de trabajo ágil utilizado para gestionar proyectos complejos de manera iterativa, centrándose en la colaboración, la flexibilidad y en la entrega continua de los avances realizados.

#### Normas y Estándares de Calidad

**Normas IEEE:**

- **IEEE 830-1998**: Proporciona una guía para estructurar el Software Requirements Specification (SRS)
- **IEEE 29119**: Estándar que se centra en el proceso de pruebas de software a lo largo del ciclo de vida del desarrollo

**Normas ISO:**

- **ISO/IEC 9126**: Estándar internacional que establece un marco para evaluar la calidad del software
- **ISO/IEC 27001**: Estándar internacional que establece los requisitos necesarios para establecer, implementar, mantener y mejorar un Sistema de Gestión de Seguridad de la Información (SGSI)

---

## Estructura del Proyecto

El proyecto está organizado siguiendo el patrón MVC (Modelo-Vista-Controlador) y la arquitectura Cliente-Servidor:

```
PUERTA_ORION/
├── backend/                    # Aplicación Flask (Backend)
│   ├── app.py                  # Punto de entrada principal
│   ├── config.py               # Configuración de la aplicación
│   ├── requirements.txt        # Dependencias Python
│   ├── pytest.ini             # Configuración de tests
│   ├── Dockerfile              # Imagen Docker del backend
│   ├── entrypoint.sh           # Script de inicio del contenedor
│   ├── run_seeders.py         # Script para ejecutar seeders
│   ├── migrations/             # Migraciones de base de datos (Alembic)
│   ├── src/
│   │   ├── config/             # Configuración de seeders
│   │   ├── database/           # Configuración de SQLAlchemy
│   │   ├── middleware/         # Decoradores de autenticación
│   │   │   ├── auth_decorator.py
│   │   │   ├── auth_decorator_config.py
│   │   │   └── auth_error_handler.py
│   │   ├── models/             # Modelos de datos (ORM SQLAlchemy)
│   │   │   ├── acudientes/     # Modelos de acudientes
│   │   │   ├── catalogos/      # Modelos de catálogos
│   │   │   ├── categorias/     # Modelos de categorías
│   │   │   ├── deportistas/   # Modelos de deportistas
│   │   │   ├── eventos/        # Modelos de eventos
│   │   │   ├── galeria/        # Modelos de galería
│   │   │   ├── pagos/          # Modelos de pagos
│   │   │   ├── personas/       # Modelos de personas
│   │   │   ├── roles_y_permisos/ # Modelos de roles y permisos
│   │   │   ├── salud/          # Modelos de salud
│   │   │   └── usuarios/       # Modelos de usuarios
│   │   ├── routes/             # Blueprints de endpoints
│   │   │   ├── auth_routes.py
│   │   │   ├── auth_reset.py
│   │   │   ├── deportistas_routes.py
│   │   │   ├── eventos_routes.py
│   │   │   ├── pagos_routes.py
│   │   │   ├── usuarios_routes.py
│   │   │   ├── catalogos_routes.py
│   │   │   ├── galeria_routes.py
│   │   │   ├── mensualidades_routes.py
│   │   │   ├── archivos_routes.py
│   │   │   ├── personas_routes.py
│   │   │   └── dynamic_data_routes.py
│   │   ├── services/           # Lógica de negocio
│   │   │   ├── Auth/           # Servicios de autenticación
│   │   │   ├── catalogos_service.py
│   │   │   ├── deportista_service.py
│   │   │   ├── mercadopago_service.py
│   │   │   └── registro_deportista_service.py
│   │   ├── seeders/            # Scripts de datos iniciales
│   │   └── utils/              # Utilidades y helpers
│   │       ├── logger.py
│   │       ├── http_responses.py
│   │       ├── error_messages.py
│   │       ├── validations.py
│   │       └── request_validators.py
│   ├── static/                 # Archivos estáticos (uploads)
│   ├── tests/                  # Suite de pruebas
│   │   ├── fixtures/           # Datos de prueba
│   │   ├── helpers/            # Utilidades para tests
│   │   ├── integration/        # Tests de integración
│   │   └── unit/               # Tests unitarios
│   └── logs/                   # Archivos de log
├── frontend/                    # Aplicación Vue.js (Frontend)
│   ├── src/
│   │   ├── components/         # Componentes Vue reutilizables
│   │   │   ├── admin/          # Componentes de administración
│   │   │   ├── datos-dinamicos/ # Componentes de catálogos
│   │   │   ├── deportistas/    # Componentes de deportistas
│   │   │   ├── formularios/    # Componentes de formularios
│   │   │   ├── galeria/        # Componentes de galería
│   │   │   ├── layout/         # Componentes de layout
│   │   │   ├── roles/          # Componentes de roles
│   │   │   └── ui/             # Componentes UI básicos
│   │   ├── views/             # Vistas/páginas
│   │   ├── router/            # Configuración de rutas (Vue Router)
│   │   ├── stores/            # Gestión de estado (Pinia)
│   │   │   ├── auth.js
│   │   │   ├── user.js
│   │   │   └── ui.js
│   │   ├── services/          # Servicios de API
│   │   │   ├── authService.js
│   │   │   ├── deportistasService.js
│   │   │   ├── mensualidadesService.js
│   │   │   ├── pagosEfectivoService.js
│   │   │   └── ...
│   │   ├── composables/       # Composables de Vue 3
│   │   │   ├── useAuth.js
│   │   │   ├── useFetch.js
│   │   │   └── useUserRole.js
│   │   ├── config/            # Configuración
│   │   └── utils/             # Utilidades
│   ├── public/                # Archivos estáticos públicos
│   ├── package.json           # Dependencias Node.js
│   └── vite.config.js         # Configuración de Vite
├── docker-compose.yml          # Orquestación de contenedores
└── README.md                   # Este archivo
```

---

## Descripción de Módulos

El sistema está dividido en módulos independientes que facilitan su mantenimiento y actualización:

### 1. Módulo de Página de Inicio

El módulo de página de inicio proporciona una vista general del Club Deportivo Puerta de Orión, mostrando información clave sobre el club, sus objetivos, actividades y novedades. Este módulo está diseñado para ser accesible a todos los roles de usuarios dentro del sistema.

**Funcionalidades por rol:**

- **Aspirantes**: Botón para registrarse en el club, guiándolos hacia el formulario de inscripción
- **Deportistas y Acudientes**: Botón que lleva a la sección de mensualidades
- **Entrenador**: Botón para acceder al registro de deportistas
- **Administrador**: Botón con dos funcionalidades:
  - Ver Deportistas Registrados
  - Gestionar Mensualidades

**Elementos comunes:**

- Botón de Inicio: Lleva a la página principal con imagen representativa del club y noticias recientes
- Botón de Calendario: Acceso directo al calendario de eventos
- Botón de Galería de Imágenes: Acceso a la galería del club

### 2. Módulo de Calendario del Club

El calendario anual es una herramienta clave para organizar y visualizar todos los entrenamientos, torneos y eventos importantes del Club Deportivo Puerta de Orión.

**Funcionalidades por rol:**

- **Administrador**: Capacidad de agregar y modificar eventos en el calendario
- **Entrenador**: Acceso completo a eventos y entrenamientos, puede modificar el calendario de entrenamientos
- **Deportista**: Acceso a su agenda personalizada con entrenamientos programados y torneos
- **Acudiente**: Acceso al calendario del deportista a su cargo
- **Aspirante**: Acceso a eventos generales del club (sin acceso a actividades específicas)

### 3. Módulo de Galería

El módulo de galería permite almacenar y mostrar imágenes relacionadas con el Club Deportivo Puerta de Orión, como fotos de entrenamientos, torneos, eventos y otras actividades importantes.

**Funcionalidades por rol:**

- **Administrador**: Capacidad de agregar, eliminar y modificar imágenes en la galería
- **Otros roles** (entrenadores, deportistas, acudientes, aspirantes): Visualización de las imágenes almacenadas en la galería

### 4. Módulo de Perfiles

El módulo de gestión de información personal permite a los usuarios administrar su perfil personal dentro del sistema, asegurando que la información esté actualizada y sea fácilmente accesible.

**Funcionalidades por rol:**

- **Deportistas y Acudientes**: Capacidad de ver y actualizar su propia información personal
- **Entrenadores, Administradores y Aspirantes**: Solo tienen acceso para ver su propia información personal, sin posibilidad de modificarla
- **Acudientes**: Acceso especial para ver la información de sus acudidos (deportistas a su cargo)

### 5. Módulo de Mensualidades

El módulo de gestión de pagos de mensualidades permite un control claro y eficiente sobre los pagos realizados por los deportistas y acudientes.

**Funcionalidades por rol:**

- **Deportistas y Acudientes**: Capacidad de ver el estado y el historial de los pagos realizados
- **Administrador**: Capacidad de gestionar los pagos de todos los deportistas, registrar pagos, actualizar estados y generar reportes

### 6. Módulo de Inscripción

Este módulo permite a los aspirantes registrarse en el Club Deportivo Puerta de Orión de manera rápida y sencilla. A través de este sistema, los aspirantes podrán completar su inscripción proporcionando la información necesaria.

**Proceso:**

1. El aspirante completa el formulario de inscripción
2. Los datos son ingresados y enviados
3. El administrador revisa la información y aprueba la inscripción
4. El nuevo miembro queda registrado en el sistema

### 7. Módulo de Deportistas

Este módulo permite a los entrenadores acceder a información clave sobre los deportistas, incluyendo datos personales, antropométricos (como peso, altura, índice de masa corporal, entre otros) y eventos.

**Funcionalidades:**

- **Entrenadores**: Acceso exclusivo para ver y actualizar los datos antropométricos de los deportistas, actualizar registros de asistencia
- **Administrador**: Acceso completo para ver, editar y gestionar la información de todos los deportistas

---

## Flujos Principales del Sistema

### Flujo de Registro de Usuarios

```
1. Usuario accede al sistema
2. Selecciona tipo de registro (Aspirante, Deportista, Acudiente)
3. Completa formulario de registro con información requerida
4. Sistema valida datos ingresados
5. Usuario es registrado en el sistema
6. Sistema genera token JWT para autenticación
7. Usuario recibe confirmación y puede acceder al sistema
8. Si es deportista, debe completar perfil con información adicional
```

### Flujo de Autenticación

```
1. Usuario ingresa tipo de documento, número de documento y contraseña
2. Sistema valida credenciales contra base de datos
3. Sistema genera token JWT con información del usuario y roles
4. Token se envía al cliente y se almacena
5. Cliente incluye token en header Authorization para requests subsecuentes
6. Middleware @require_auth valida token en cada request protegida
```

### Flujo de Gestión de Mensualidades

```
1. Deportista/Acudiente accede al módulo de mensualidades
2. Visualiza estado de pagos y mensualidades pendientes
3. Selecciona método de pago (Efectivo o MercadoPago)
4. Si es MercadoPago:
   - Sistema crea preferencia de pago mediante API
   - Usuario es redirigido a MercadoPago
   - Usuario completa pago
   - Webhook de MercadoPago notifica al sistema
   - Sistema actualiza estado del pago
5. Si es efectivo:
   - Administrador registra el pago manualmente
6. Sistema genera confirmación de pago
7. Acudiente puede consultar pagos del deportista a su cargo
```

### Flujo de Registro de Deportista Completo

```
1. Aspirante se registra con información básica
2. Sistema crea usuario con rol "aspirante"
3. Aspirante completa formulario de deportista con:
   - Información básica personal
   - Antecedentes médicos
   - Información escolar
   - Información deportiva
   - Información de acudiente
   - Aceptación de términos y condiciones
4. Sistema valida todos los datos
5. Sistema crea registros relacionados (persona, deportista, acudiente, salud)
6. Sistema asigna categoría según edad
7. Deportista queda registrado y puede acceder al sistema
```

### Flujo de Gestión de Calendario/Eventos

```
1. Administrador/Entrenador accede al módulo de eventos
2. Crea nuevo evento (entrenamiento, torneo, etc.)
3. Asigna tipo de evento, categoría, fecha, hora y descripción
4. Sistema registra evento en base de datos
5. Deportistas y acudientes visualizan eventos relevantes según su categoría
6. Sistema permite filtrar eventos por categoría y fecha
```

### Flujo de Gestión de Galería

```
1. Administrador accede al módulo de galería
2. Sube imágenes relacionadas con eventos o actividades
3. Sistema almacena imágenes en directorio estático
4. Sistema registra metadatos en base de datos
5. Todos los usuarios pueden visualizar imágenes de la galería
6. Sistema permite filtrar por categoría o evento
```

---

## Modelo de Datos

### Modelo Lógico de la Base de Datos

El modelo lógico de la base de datos organiza los datos en tablas interrelacionadas a través de claves primarias y foráneas, facilitando la consulta y manipulación de la información.

### Entidades Principales

#### Personas
```
id_persona (PK)
documento
primer_nombre
segundo_nombre
primer_apellido
segundo_apellido
tipo_documento (FK)
correo_electronico
direccion
telefono
fecha_nacimiento
id_mensualidad (FK)
id_estado (FK)
id_sexo (FK)
id_ciudad (FK)
id_documento (FK)
id_eps (FK)
id_institucion (FK)
id_tipo_sangre (FK)
id_enfermedad (FK)
```

#### Sexo
```
id_sexo (PK)
sexo
```

#### EPS
```
id_eps (PK)
nombre_eps
```

#### Enfermedades
```
id_enfermedad (PK)
id_tipo_enfermedad (FK)
```

#### CiudadResidencia
```
id_ciudad (PK)
nombre_ciudad
```

#### TipoDocumento
```
id_documento (PK)
nombre_documento
```

#### InstitucionRepresentaDeportista
```
id_institucion (PK)
nombre_institucion
```

#### GrupoSanguineo
```
id_tipo_sangre (PK)
tipo_sangre
```

#### TipoEnfermedad
```
id_tipo_enfermedad (PK)
nombre
```

#### Mensualidad
```
id_mensualidad (PK)
estado
fecha_pago
monto_pago
id_metodo_pago (FK)
id_categoria (FK)
```

#### MetodoPago
```
id_metodo_pago (PK)
nombre_metodo
```

#### Cuota
```
id_cuota (PK)
monto_cuota
fecha_cuota
estado
documento
id_metodo_pago (FK)
```

#### Categoria
```
id_categoria (PK)
codigo_categoria
nombre_categoria
edad_min
edad_max
```

#### Entrenamiento
```
id_entrenamiento (PK)
id_categoria (FK)
fecha_entrenamiento
```

#### TipoEntrenamiento
```
id_tipo_entrenamiento (PK)
nombre
descripcion
```

#### Roles
```
id_rol (PK)
nombre_rol
```

#### PersonasRol
```
id_personas_rol (PK)
estado
id_persona (FK)
id_rol (FK)
```

#### RolUsuario
```
id_rol_usuario (PK)
id_usuario (FK)
id_persona (FK)
```

#### Usuario
```
id_usuario (PK)
usuario
password
id_rol_usuario (FK)
id_estado (FK)
```

#### Estado
```
id_estado (PK)
estado
```

#### Asistencia
```
id_asistencia (PK)
estado
```

### Relaciones Principales

- **Personas** → **TipoDocumento** (Muchos a Uno)
- **Personas** → **Mensualidad** (Uno a Muchos)
- **Personas** → **PersonasRol** (Uno a Muchos)
- **PersonasRol** → **Roles** (Muchos a Uno)
- **Mensualidad** → **MetodoPago** (Muchos a Uno)
- **Mensualidad** → **Categoria** (Muchos a Uno)
- **Entrenamiento** → **Categoria** (Muchos a Uno)
- **Usuario** → **RolUsuario** (Uno a Muchos)
- **RolUsuario** → **Personas** (Muchos a Uno)

---

## Reglas de Negocio

### Registro y Gestión de Usuarios

#### Aspirantes

**Información de Registro requerida:**
- Tipo de documento
- Número de documento
- Primer nombre
- Segundo nombre
- Primer apellido
- Segundo apellido
- Fecha de nacimiento
- Correo electrónico
- Teléfono
- Contraseña

**Permisos:**
- Ver información de la página
- Inscribirse al club
- Ver calendario de eventos generales
- Ver galería de imágenes

#### Deportistas

**Información Básica requerida:**
- Primer nombre, segundo nombre
- Primer apellido, segundo apellido
- Tipo de documento, número de documento
- Edad, categoría
- Fecha de nacimiento
- Número de teléfono, correo electrónico
- Sexo, tipo de sangre
- Ciudad donde se radica
- Institución con la que se respalda el deportista
- Afiliación de EPS
- Dirección
- Contraseña

**Antecedentes Médicos:**
- ¿Existe algún tipo de recomendación médica que considere mencionar a tener presente para la deportiva?
- Si existe, ¿cuál?

**Información Escolar:**
- Institución educativa que representa al deportista

**Información Deportiva:**
- ¿Practica o ha practicado antes otro deporte además del voleibol? ¿Cuál(es)?
- ¿Participas o has participado en otras escuelas de formación? ¿Cuál(es)?

**Información de Acudientes:**
- Primer y segundo nombre del acudiente
- Primer y segundo apellido del acudiente
- Teléfono de contacto del acudiente
- Parentesco

**Término de Condiciones:**
- El suscrito PADRE DE FAMILIA, como mayor de edad, declaro que me encuentro de acuerdo en tomar parte del proceso de formación ofertado y libero de toda responsabilidad a la escuela de voleibol PUERTA DE ORION, por cualquier tipo de accidente, lesión o problema de salud que se presenta durante el desarrollo del programa de formación, Y será mi entera responsabilidad como acudiente buscar solución a las situaciones que se presenten. Por lo que renunciamos al derecho de recurrir a la justicia ordinaria y de entablar acciones contra la ESCUELA, SU REPRESENTANTE, O CUERPO TÉCNICO.

**Permisos:**
- Ver y actualizar su propia información
- Consultar sus mensualidades
- Ver calendario de entrenamientos
- Ver galería
- Realizar pagos (si es mayor de edad)

#### Acudientes

**Información de Registro requerida:**
- Tipo de documento
- Número de documento
- Primer nombre, segundo nombre
- Primer apellido, segundo apellido
- Fecha de nacimiento
- Correo
- Teléfono
- Contraseña
- Confirmar contraseña

**Permisos:**
- Ver y actualizar su propia información
- Ver información del deportista a su cargo
- Consultar mensualidades del deportista
- Ver calendario del deportista
- Realizar pagos en nombre del deportista

#### Entrenadores

**Permisos:**
- Ver su propia información (sin modificar)
- Gestionar calendarios de entrenamiento
- Registrar y categorizar deportistas
- Realizar pruebas antropométricas
- Actualizar estado de deportistas o acudientes
- Eliminar deportista o acudiente
- Ver datos antropométricos de deportistas
- Actualizar registros de asistencia

#### Administradores

**Permisos:**
- Consultar información de todos los usuarios
- Manejar información de deportistas y acudientes
- Consultar y registrar asistencias de deportistas
- Notificar novedades a deportistas o acudientes
- Recibir pagos hechos por deportistas o acudientes
- Activar o inactivar estado de deportistas o acudientes
- Eliminar usuarios
- Gestionar mensualidades de todos los deportistas
- Agregar eventos al calendario
- Agregar imágenes a la galería

### Control de Acceso

- Solo el entrenador, deportistas del club y sus acudientes podrán acceder al sistema
- Los deportistas y acudientes solo pueden ver su propia información
- Los roles tienen permisos diferenciados según su nivel de acceso
- El administrador tiene acceso completo al sistema

### Gestión de Mensualidades

- Los deportistas y acudientes pueden ver el estado y historial de pagos
- El administrador puede gestionar todos los pagos
- Se mantiene un registro de mensualidades pagadas y pendientes

### Gestión de Asistencias

- El entrenador puede registrar la asistencia de los deportistas
- Se mantiene evidencia de asistencias o inasistencias
- Los acudientes pueden consultar la asistencia del deportista a su cargo

---

## Requerimientos del Sistema

### Requisitos Funcionales

- Permitir a los usuarios registrarse con algunos de los roles (acudiente, deportista) ya que el deportista debe tener un acudiente responsable
- Permitir iniciar sesión y registrarse, ya sea como aspirante, entrenador, deportista o acudiente
- Permitir a los usuarios cerrar sesión para evitar el alto flujo de usuarios en línea
- Permitir a los usuarios realizar pagos y estar informados acerca de sus mensualidades
- Tener accesibilidad para cambiar los datos agregados a su usuario
- Permitir al administrador un apartado donde mantendrá informado sobre los datos de sus deportistas
- Registrar la asistencia de los deportistas para tener una evidencia de las asistencias o inasistencias
- Mantener informados a los usuarios a partir de la página web acerca del club y sus entrenamientos
- Permitir a los deportistas o acudientes tener la opción de cancelar su inscripción de entrenamiento
- Registrar los cargos de los ayudantes que puedan tener los administradores
- Ver la localización de los escenarios deportivos en los diferentes horarios y categorías correspondientes por día
- Permitir al entrenador agregar el calendario de los entrenamientos
- Tener acceso al calendario de entrenamiento para visualizarlo

### Requisitos No Funcionales

#### Seguridad

- Implementará autenticación mediante tipo de documento, número de documento y contraseña, con la opción de recuperación de cuenta
- Se establecerán roles y permisos para restringir el acceso a datos sensibles según el perfil del usuario
- Tener un control de acceso basado en los roles para tener una mejor seguridad de los datos personales
- Tener control de los datos de los menores de edad con el consentimiento de un tutor legal

#### Rendimiento

- El sistema debe tener la capacidad de soportar múltiples clientes en línea sin saturarse
- Tener un tiempo de respuesta menor de 2 segundos para realizar consultas y generar informes

#### Usabilidad

- Ofrecer una interfaz intuitiva para los usuarios con poca experiencia usando páginas web

#### Compatibilidad

- Compatibilidad con varios sistemas operativos y navegadores (Windows, macOS, Android, iOS)

#### Disponibilidad

- Disponibilidad la mayoría del tiempo, excepto cuando el sistema esté recibiendo mantenimiento

### Limitaciones y Restricciones

- **Alcance funcional**: El sistema solo gestionará datos administrativos y métricas físicas, sin incluir funcionalidades avanzadas como entrenamientos personalizados, análisis de rendimiento en tiempo real y asistencias de los deportistas (en esta primera versión)

- **Acceso a la información**: Solo el entrenador, deportistas del club y sus acudientes podrán acceder al sistema, aclarando que los deportistas y acudientes del mismo podrán ver solo su información, con roles diferenciados según su nivel de permisos

- **Requerimientos técnicos**: El software deberá ejecutarse en dispositivos con conexión a internet y un navegador web actualizado

- **Seguridad de datos**: Se implementarán medidas de seguridad básicas para la protección de información, pero no se integrarán sistemas avanzados como autenticación biométrica o cifrado de extremo a extremo en esta primera versión

---

## Instalación

### Requisitos Previos

- **Python**: Versión 3.10 o superior
- **pip**: Gestor de paquetes de Python
- **Node.js**: Versión 20.19.0 o ≥22.12.0
- **MySQL**: Versión 8.0 o superior
- **Git**: Sistema de control de versiones

### Pasos de Instalación

#### 1. Clonar el Repositorio

```bash
git clone <url-del-repositorio>
cd PUERTA_ORION
```

#### 2. Instalar Dependencias del Backend

```bash
cd backend

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt
```

#### 3. Instalar Dependencias del Frontend

```bash
cd ../frontend
npm install
```

#### 4. Configurar Base de Datos

Crear la base de datos en MySQL:

```sql
CREATE DATABASE puerta_orion CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

---

## Configuración

### Configuración del Backend (Flask)

#### 1. Archivo de Entorno

Copiar el archivo de ejemplo y configurar las variables:

```bash
cd backend
cp config.env.example .env
```

Editar el archivo `.env` con la configuración apropiada:

```env
# Configuración básica de Flask
SECRET_KEY=tu-clave-secreta-muy-segura-aqui
DEBUG=true
FLASK_ENV=development

# Configuración del servidor
HOST=0.0.0.0
PORT=5000

# Configuración de la base de datos
DB_HOST=localhost
DB_PORT=3306
DB_USERNAME=root
DB_PASSWORD=tu-contraseña
DB_NAME=puerta_orion

# Configuración de CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:8080

# Configuración de JWT
JWT_SECRET_KEY=tu-jwt-secret-key-muy-segura
JWT_ACCESS_TOKEN_EXPIRES=3600
```

#### 2. Crear Entorno Virtual

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

#### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

#### 4. Ejecutar Migraciones

```bash
flask db upgrade
```

#### 5. Ejecutar Seeders (Datos Iniciales)

```bash
python run_seeders.py
```

### Configuración del Frontend (Vue.js)

#### 1. Archivo de Configuración

Configurar la URL de la API en el archivo de configuración del frontend:

```javascript
// frontend/src/config/api.js
export const API_URL = process.env.VUE_APP_API_URL || 'http://localhost:5000/api'
```

#### 2. Variables de Entorno

Crear archivo `.env` en el directorio frontend:

```env
VUE_APP_API_URL=http://localhost:5000/api
```

---

## Ejecución

### Modo Desarrollo

#### Backend (Flask)

```bash
cd backend

# Activar entorno virtual
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Ejecutar servidor de desarrollo
python app.py
# O usando Flask CLI:
flask run --host=0.0.0.0 --port=5000 --debug
```

El servidor estará disponible en `http://localhost:5000`

#### Frontend (Vue.js)

```bash
cd frontend
npm run dev
```

El servidor de desarrollo estará disponible en `http://localhost:5173` (o el puerto configurado)

### Modo Producción

#### Backend

```bash
cd backend

# Configurar entorno de producción
export FLASK_ENV=production
export SECRET_KEY=tu-clave-secreta-produccion
export DATABASE_URL=mysql+pymysql://...

# Usar servidor WSGI (gunicorn recomendado)
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

Usar un servidor web como Nginx o Apache configurado para servir la aplicación Flask mediante WSGI.

#### Frontend

```bash
cd frontend
npm run build
```

Los archivos compilados estarán en el directorio `dist/` y deben ser servidos por un servidor web.

---

## Endpoints API

El sistema expone los siguientes endpoints principales organizados por módulos:

### Autenticación
- `POST /api/auth/login` - Iniciar sesión
- `POST /api/auth/register` - Registro de usuarios
- `POST /api/auth/reset-password` - Solicitar recuperación de contraseña
- `POST /api/auth/reset-password/confirm` - Confirmar recuperación de contraseña
- `GET /api/auth/profile` - Obtener perfil del usuario autenticado
- `PUT /api/auth/profile` - Actualizar perfil del usuario

### Deportistas
- `GET /api/deportistas` - Listar deportistas (con paginación y filtros)
- `GET /api/deportistas/:id` - Obtener deportista por ID
- `POST /api/deportistas/registro` - Registro completo de deportista
- `PUT /api/deportistas/:id` - Actualizar deportista
- `DELETE /api/deportistas/:id` - Eliminar deportista

### Eventos
- `GET /api/eventos` - Listar eventos
- `GET /api/eventos/:id` - Obtener evento por ID
- `POST /api/eventos` - Crear evento (requiere autenticación)
- `PUT /api/eventos/:id` - Actualizar evento
- `DELETE /api/eventos/:id` - Eliminar evento

### Pagos y Mensualidades
- `GET /api/mensualidades` - Listar mensualidades
- `GET /api/mensualidades/:id` - Obtener mensualidad por ID
- `POST /api/pagos/crear` - Crear preferencia de pago MercadoPago
- `POST /api/pagos/webhook` - Webhook de MercadoPago
- `POST /api/pagos/efectivo` - Registrar pago en efectivo
- `PUT /api/mensualidades/:id` - Actualizar estado de mensualidad

### Usuarios
- `GET /api/usuarios` - Listar usuarios (solo administradores)
- `GET /api/usuarios/:id` - Obtener usuario por ID
- `PUT /api/usuarios/:id` - Actualizar usuario
- `PUT /api/usuarios/:id/estado` - Activar/desactivar usuario

### Catálogos y Datos Dinámicos
- `GET /api/catalogos` - Obtener catálogos disponibles
- `GET /api/dynamic-data/:tipo` - Obtener datos dinámicos por tipo
- `POST /api/dynamic-data/:tipo` - Crear dato dinámico (solo administradores)
- `PUT /api/dynamic-data/:tipo/:id` - Actualizar dato dinámico
- `DELETE /api/dynamic-data/:tipo/:id` - Eliminar dato dinámico

### Galería
- `GET /api/galeria` - Listar imágenes de la galería
- `POST /api/galeria` - Subir imagen (solo administradores)
- `DELETE /api/galeria/:id` - Eliminar imagen

### Archivos
- `POST /api/archivos/upload` - Subir archivo
- `GET /api/archivos/:id` - Descargar archivo

### Personas
- `GET /api/personas` - Listar personas
- `GET /api/personas/:id` - Obtener persona por ID
- `PUT /api/personas/:id` - Actualizar persona

**Nota**: La mayoría de los endpoints requieren autenticación mediante token JWT en el header `Authorization: Bearer <token>`

---

## Despliegue

### Estrategia de Implementación

#### Servidores y Hosting

El sistema está diseñado para ser desplegado en servidores que soporten:

- **Backend**: Servidor con Python 3.10+, MySQL 8.0+, y servidor web (Nginx/Apache) con WSGI (Gunicorn)
- **Frontend**: Servidor web estático o CDN para servir los archivos compilados

#### Docker en Producción

El proyecto incluye configuración Docker para facilitar el despliegue:

```bash
# Build de imágenes
docker-compose build

# Levantar servicios en producción
docker-compose up -d

# Ver logs
docker-compose logs -f
```

#### Migración de Datos

1. Exportar datos existentes del sistema anterior (si aplica)
2. Transformar datos al formato requerido por el nuevo sistema
3. Importar datos a la nueva base de datos
4. Validar integridad de los datos migrados

### Características Implementadas

#### Integración con MercadoPago

El sistema incluye integración completa con MercadoPago para procesamiento de pagos:

- Creación de preferencias de pago
- Webhooks para notificaciones de pago
- Manejo de estados de transacciones
- Registro de pagos en efectivo como alternativa

#### Sistema de Roles y Permisos

Implementación completa de control de acceso basado en roles:

- Roles: Administrador, Entrenador, Deportista, Acudiente, Aspirante
- Permisos granulares por funcionalidad
- Decoradores de autenticación personalizados
- Validación de permisos en cada endpoint

#### Sistema de Testing

El proyecto incluye suite completa de pruebas:

- Tests unitarios para servicios y lógica de negocio
- Tests de integración para endpoints y flujos completos
- Cobertura de código configurada (mínimo 20%)
- Fixtures y helpers para facilitar testing
- Marcadores personalizados para organizar tests

**Ejecutar tests:**

```bash
cd backend

# Todos los tests
pytest

# Tests unitarios
pytest tests/unit/

# Tests de integración
pytest tests/integration/

# Con cobertura
pytest --cov=src --cov-report=html
```

#### Sistema de Logging

Implementación de logging estructurado:

- Logs de aplicación en `logs/app/`
- Logs de errores en `logs/app/error.log`
- Logs de acceso en `logs/app/access.log`
- Logs de base de datos en `logs/database/db.log`
- Archivo de logs antiguos en `logs/archive/`

### Plan de Capacitación

#### Manuales Técnicos y de Usuario

- Manual de usuario para cada rol (Aspirante, Deportista, Acudiente, Entrenador, Administrador)
- Manual técnico para desarrolladores y administradores del sistema
- Guías de procedimientos para operaciones comunes

#### Sesiones de Formación

- Sesiones de capacitación para administradores y entrenadores
- Tutoriales en video para usuarios finales
- Documentación en línea accesible desde el sistema

### Mantenimiento del Software

#### Soporte Técnico

- Canal de soporte para reportar problemas
- Documentación de problemas comunes y soluciones
- Proceso de escalamiento para problemas críticos

#### Estrategia de Actualización

- Versionado del software
- Proceso de actualización documentado
- Pruebas en entorno de staging antes de producción
- Plan de rollback en caso de problemas

---

## Plan de Desarrollo

### Metodología Utilizada

**Scrum**: Marco de trabajo ágil que se utiliza para gestionar proyectos complejos de manera iterativa, centrándose en la colaboración, la flexibilidad y en la entrega continua de los avances realizados.

**Roles en Scrum:**

- **Product Owner (PO)**: Define el trabajo que se va a realizar, mantiene la lista de tareas o requerimientos
- **Scrum Master**: Coordina el equipo, facilita las reuniones de trabajo y asegura que se sigan los procesos
- **Equipo de Desarrollo**: Construye el producto, escribe el código, realiza pruebas unitarias

### Fases de Desarrollo

1. **Fase #1 – Levantamiento de requisitos**
2. **Fase #2 – Documentación**
3. **Fase #3 – Diseño y modelado**
4. **Fase #4 – Desarrollo del Backend**
5. **Fase #5 – Desarrollo del Frontend**
6. **Fase #6 – Pruebas y validación**
7. **Fase #7 – Despliegue y mantenimiento**

### Plan de Iteraciones y Sprints

Un sprint es un ciclo de trabajo corto y ágil, por lo general suele ser de 1 a 4 semanas en el que un equipo de desarrollo trabaja para completar un conjunto de tareas específicas o funcionalidades del producto.

**Características de los Sprints:**

- Duración fija
- Se establece qué trabajo se va a hacer desde el inicio
- Al final del sprint debe entregarse algo funcional
- Finalizan con una revisión

### Responsabilidades del Equipo

- **Scrum Master**: Coordinar el equipo, facilitar reuniones, asegurar seguimiento de procesos
- **Product Owner**: Definir trabajo a realizar, mantener lista de tareas, asegurar avances del proyecto
- **Desarrolladores**: Construir el producto, escribir código, realizar pruebas unitarias, colaborar en objetivos del Sprint
- **Diseñador UX/UI**: Crear prototipos y mockups, diseñar interfaz de usuario intuitiva
- **Tester/QA**: Diseñar y ejecutar casos de prueba, asegurar calidad, detectar errores
- **Analista**: Reunirse con cliente, transformar necesidades en requisitos técnicos, documentar funcionalidades

---

## Contribución

### Proceso de Contribución

1. Fork del repositorio
2. Crear rama para feature: `git checkout -b feature/nueva-funcionalidad`
3. Commit cambios: `git commit -m "feat: agregar nueva funcionalidad"`
4. Push a la rama: `git push origin feature/nueva-funcionalidad`
5. Crear Pull Request

### Estándares de Código

- Seguir las convenciones de código de Python (PEP 8)
- Seguir las convenciones de código de Vue.js (ESLint/Prettier)
- Escribir código documentado con docstrings
- Realizar pruebas para nuevas funcionalidades
- Usar type hints en Python
- Seguir principios de programación funcional cuando sea posible
- Mantener funciones puras en la capa de servicios

### Convenciones de Commits

Usar [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` Nueva funcionalidad
- `fix:` Corrección de bug
- `docs:` Documentación
- `style:` Formato, punto y coma faltante, etc.
- `refactor:` Refactorización de código
- `test:` Agregar o modificar tests
- `chore:` Tareas de mantenimiento

---

## Licencia

[Especificar licencia del proyecto según corresponda]

---

## Contacto

### Equipo de Desarrollo

- **KEVIN SANTIAGO PRADA CASTELLANOS**
- **MARIO ALEXANDER CAÑOLA CANO**
- **JHON DEIBY OLARTE BENITEZ**

### Institución

**Servicio Nacional de Aprendizaje (SENA)**  
Centro De Desarrollo Agroindustrial, Turístico Y Tecnológico Del Guaviare (CDATTG)  
Programa: Análisis y Desarrollo de Software (ADSO)  
Ficha: 2923560

### Instructor

**Jhon Hader Rodríguez Perdomo**

### Stakeholder

**Jhon Jairo Corredor** - Entrenador y Administrador del Club Deportivo Puerta de Orión

---

## Referencias y Documentación Adicional

### Enlaces de Documentación

- [Entrevista con Stakeholder](https://drive.google.com/file/d/1FxMHnShEXcXHhMk3Y-3xf2nL6rZXWx-r/view?usp=drive_link)
- Diagrama de casos de uso
- Modelo Entidad-Relación (MER)
- Historias de Usuario
- Matriz de Priorización
- Matriz de Stakeholder
- Prototipos y Wireframes (Moqups)

### Fuentes de Información

- Formulario de Inscripción Escuela de Formación 2025 (proporcionado por el stakeholder)
- Entrevista realizada al profe Jhon Jairo Corredor
- Documentación técnica del proyecto

---

**Última actualización**: Marzo 2025
