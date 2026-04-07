---
name: choose-layer
description: Decide whether a task in go-satcfdi should use sat, satflow, or satservice, then route the agent to the correct workflow skill before writing code.
---

# choose-layer

## Propósito

Usa esta skill al inicio de cualquier tarea sobre `go-satcfdi` para elegir la capa correcta y evitar implementar una solución en el nivel equivocado.

## Cuándo usarla

- Cuando el usuario pide una integración nueva y todavía no está claro si conviene `sat`, `satflow` o `satservice`
- Cuando una tarea mezcla Go, otros lenguajes, CLI, Connect/gRPC o un servicio remoto
- Cuando un cambio puede mover reglas SAT entre capas

## No usarla

- Si la capa ya quedó fijada y la tarea ya está dentro de un workflow concreto
- Si solo vas a revisar detalles locales de una skill ya elegida

## Reglas duras

- Prefiere `satflow` para integraciones Go normales dentro del mismo proceso.
- Usa `sat` solo cuando de verdad se necesite control explícito de token, autenticación o llamadas paso por paso.
- Usa `satservice` cuando el consumidor viva en otro proceso o lenguaje, o cuando necesite un contrato remoto tipado.
- No muevas validaciones SAT ni reglas de combinación de filtros fuera del paquete `sat`.
- No introduzcas lógica fiscal o de negocio específica de una empresa en el core.

## Workflow recomendado

1. Identifica dónde vive el consumidor: mismo proceso Go, otro proceso o otro lenguaje.
2. Si es Go y el flujo es estándar de descarga, carga [satflow-download-flow](../satflow-download-flow/SKILL.md).
3. Si es Go y se requiere control fino de autenticación, token o secuencia SOAP, carga [sat-low-level-requests](../sat-low-level-requests/SKILL.md).
4. Si el consumidor es remoto o necesita Connect/gRPC/gRPC-Web, carga [satservice-remote-integration](../satservice-remote-integration/SKILL.md).
5. Si la tarea toca secretos, `credential_ref`, smoke tests o validación live, carga también [credentials-and-validation](../credentials-and-validation/SKILL.md).

## Ejemplos correctos

- “Necesito descargar CFDI desde un backend Go sin pelearme con tokens”.
  Elige `satflow` y carga `satflow-download-flow`.
- “Ya tengo un token SAT y quiero controlar `Consultar -> Verificar -> Descargar` manualmente”.
  Elige `sat` y carga `sat-low-level-requests`.
- “Quiero consumir el flujo desde Python y PHP”.
  Elige `satservice` y carga `satservice-remote-integration`.

## Errores comunes

- Elegir `satservice` para una integración Go local solo porque “suena más moderna”.
- Elegir `sat` para un flujo estándar y terminar reimplementando caché de token, polling y reintentos.
- Elegir `satflow` cuando el requisito real es exponer un contrato remoto a otros lenguajes.
- Copiar reglas de validación SAT a la capa equivocada en vez de reutilizar `sat`.

## Fuentes de verdad

- [README.md](../../README.md)
- [docs/integration.md](../../docs/integration.md)
- [docs/service.md](../../docs/service.md)
- [proto/satcfdi/v1/service.proto](../../proto/satcfdi/v1/service.proto)
- [sat/query_validate.go](../../sat/query_validate.go)

## Verificación

- La capa elegida coincide con el lugar donde vive el consumidor y con el nivel de control requerido.
- La solución no duplica reglas SAT ya existentes en `sat`.
- La siguiente skill de workflow quedó explícitamente identificada antes de editar código.
