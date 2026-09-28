# ACOMPAS

**Asistente conversacional de IA para pacientes con cáncer de páncreas.**

ACOMPAS ayuda a los pacientes con cáncer de páncreas a comprender su
documentación clínica y a prepararse mejor para sus consultas con el
oncólogo. No diagnostica ni sustituye el criterio médico: es una
herramienta de apoyo para la comprensión y la preparación.

🚧 **Proyecto en desarrollo.** Lanzamiento previsto: verano de 2027.
Más información: [acompas-ia.es](https://www.acompas-ia.es)

*[Read in English](README.md)*

---

## Qué es ACOMPAS

Un diagnóstico de cáncer de páncreas genera una gran cantidad de
documentación clínica llena de terminología especializada que puede
resultar difícil de comprender sin formación médica. ACOMPAS traduce
esa documentación a un lenguaje sencillo y ayuda a los pacientes a
preparar preguntas para sus consultas de oncología.

El proyecto está desarrollado por voluntarios, con carácter no
lucrativo, en colaboración con [ACANPAN](https://asociacioncancerdepancreas.org/),
la asociación española de pacientes con cáncer de páncreas.

## Cómo funciona (visión general)

- **Conversación asistida por IA**, con respuestas fundamentadas en
  guías clínicas y publicaciones médicas seleccionadas.
- **Privacidad desde el diseño**: los documentos clínicos se
  anonimizan antes de ser utilizados por el sistema. La identidad del
  paciente nunca se almacena en la base de datos de la aplicación.

Puedes encontrar más información sobre el proyecto en
[acompas-ia.es](https://www.acompas-ia.es).

## Estado del proyecto

Actualmente se encuentra en las primeras fases de desarrollo
(Fase 0 / Fase 1). Este repositorio se irá completando
progresivamente a medida que avance la implementación.

## Entorno de desarrollo

ACOMPAS utiliza Docker como entorno de desarrollo de referencia. El
objetivo es que todos los colaboradores puedan ejecutar los mismos
servicios localmente, independientemente del sistema operativo del
equipo anfitrión.

### Requisitos

- Git
- Docker Desktop con integración con WSL2 en Windows
- Docker Engine / Docker Compose en Linux o macOS

Para el flujo de desarrollo estándar no es necesario instalar
directamente Python, PostgreSQL ni Node.js en el equipo anfitrión.

### Primera configuración

Clona el repositorio y entra en el directorio del proyecto:

```bash
git clone git@github.com:ACOMPAS-IA/acompas.git
cd acompas
```

Crea el archivo de entorno local:

```bash
cp .env.example .env
```

Inicia el entorno de desarrollo:

```bash
docker compose up -d --build
```

Comprueba los servicios en ejecución:

```bash
docker compose ps
```

El endpoint de salud del backend debe devolver:

```json
{"status":"ok"}
```

Puedes comprobarlo con:

```bash
curl http://localhost:8000/health
```

### Detener el entorno

Para detener los servicios:

```bash
docker compose down
```

El volumen local de PostgreSQL se conserva salvo que se elimine
explícitamente.

### Flujo de desarrollo

Los cambios deben desarrollarse en ramas de funcionalidad y enviarse
mediante Pull Requests. Los pushes directos a `main` no forman parte
del flujo de trabajo habitual.

Ejemplo:

```bash
git switch -c feature/ACO-XXX-descripcion-corta
```

Antes de abrir un Pull Request, comprueba que los tests correspondientes
pasan correctamente y que el entorno Docker se inicia sin errores.

## Equipo

- **Miguel Martínez** — Responsable y fundador del proyecto. Ingeniero
  informático y también paciente de cáncer de páncreas; su experiencia
  fue la motivación directa para crear ACOMPAS. Trabaja junto a Javier
  en la dirección técnica y la implementación del proyecto.
- **Javier Pérez** — Responsable técnico (voluntario). Trabaja junto a
  Miguel en la dirección técnica del proyecto y es responsable de la
  implementación principal desarrollada hasta ahora, incluyendo el
  pipeline de generación aumentada mediante recuperación (RAG),
  compuesto por la ingesta de documentos, embeddings y búsqueda
  semántica, así como de la arquitectura del sistema.

Buscamos ampliar nuestro equipo técnico de voluntarios (backend,
IA/NLP y frontend). Si estás interesado en colaborar, ponte en
contacto con nosotros.

## Colaboración

ACOMPAS se desarrolla en colaboración con **ACANPAN**, que aporta
contexto clínico, acceso a pacientes y validación del producto.

## Contacto

📧 [info@acompas-ia.es](mailto:info@acompas-ia.es)

## Licencia

Este proyecto está licenciado bajo [AGPL-3.0](LICENSE).
