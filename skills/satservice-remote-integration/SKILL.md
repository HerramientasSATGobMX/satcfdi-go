---
name: satservice-remote-integration
description: Guide remote or multilang integrations toward satservice, including SATService vs SATFlowService, credential sources, streaming package download, and Connect/gRPC contract rules.
---

# satservice-remote-integration

## Propósito

Usa esta skill cuando `go-satcfdi` se va a consumir desde otro proceso o lenguaje mediante `SATService` o `SATFlowService` sobre Connect, gRPC o gRPC-Web.

## Cuándo usarla

- Integraciones desde Python, PHP u otros procesos no Go
- Casos donde el servicio tipado debe exponer un contrato remoto estable
- Tareas sobre `service.proto`, `satservice`, `satcfdid`, `credential_ref` o streaming

## No usarla

- Si el consumidor ya vive en el mismo proceso Go y no necesita un boundary remoto; usa [satflow-download-flow](../satflow-download-flow/SKILL.md) o [sat-low-level-requests](../sat-low-level-requests/SKILL.md)
- Si la tarea solo cambia detalles internos del core SOAP sin impacto en el contrato remoto

## Reglas duras

- Usa `SATService` para operaciones unitarias y `SATFlowService` para orquestación síncrona de alto nivel.
- `RunDownloadFlow` autentica, envía la solicitud y hace polling, pero no descarga paquetes; devuelve `request_id`, estado final y `package_ids`.
- En requests firmados debe existir exactamente uno entre `credentials` y `credential_ref`.
- Si el paquete puede ser grande, prefiere `StreamDownloadPackage`; `DownloadPackage` queda para compatibilidad y payloads pequeños.
- `credential_ref` solo funciona si el servidor fue configurado con directorios permitidos.
- Mantén `satservice` delgado: traduce transporte y errores, pero no dupliques reglas SAT ni lógica de negocio.

## Workflow recomendado

1. Decide si el cliente remoto necesita operaciones unitarias (`SATService`) o flujo completo (`SATFlowService`).
2. Elige la fuente de credenciales: inline para desarrollo simple o `credential_ref` para operación controlada por el servidor.
3. Si el flujo termina con `package_ids`, descarga cada paquete con `SATService`.
4. Para paquetes grandes o límites unary, usa `StreamDownloadPackage`.
5. Si cambias el contrato Protobuf o el mapeo de errores, revisa ejemplos, clientes generados y tests extendidos.

## Ejemplos correctos

- Cliente remoto que solo quiere `request_id` y `package_ids`.
  Usa `SATFlowService.RunDownloadFlow`.
- Cliente remoto que ya tiene `package_id` y espera payload grande.
  Usa `SATService.StreamDownloadPackage`.
- Cliente Python o PHP.
  Sigue los ejemplos de [examples/README.md](../../examples/README.md) en vez de inventar un contrato alterno.

## Errores comunes

- Esperar que `RunDownloadFlow` devuelva bytes de paquetes.
- Usar `DownloadPackage` para paquetes grandes cuando el servicio ya soporta streaming.
- Enviar `credentials` y `credential_ref` al mismo tiempo.
- Permitir que `credential_ref` apunte fuera del allowlist del servidor.
- Duplicar reglas de validación de `sat` dentro de handlers o clientes remotos.

## Fuentes de verdad

- [docs/service.md](../../docs/service.md)
- [proto/satcfdi/v1/service.proto](../../proto/satcfdi/v1/service.proto)
- [satservice/server.go](../../satservice/server.go)
- [satservice/credentials.go](../../satservice/credentials.go)
- [satservice/server_extended_test.go](../../satservice/server_extended_test.go)
- [examples/service-run-download-flow/main.go](../../examples/service-run-download-flow/main.go)
- [examples/README.md](../../examples/README.md)

## Verificación

- La solución usa `satservice` solo cuando existe una necesidad real de boundary remoto.
- El request firmado usa exactamente una fuente de credenciales.
- La elección entre unary y streaming coincide con el tamaño esperado del paquete.
- Cambios en contrato, errores o credenciales siguen cubiertos por `go test ./...`.
