# AGENTS.md

Este repositorio incluye un sistema repo-local de skills para ayudar a agentes de IA a integrar y mantener `go-satcfdi` sin inventar reglas SAT ni romper flujos sensibles.

## Inicio rápido

1. Empieza por [choose-layer](skills/choose-layer/SKILL.md) para elegir entre `sat`, `satflow` y `satservice`.
2. Carga exactamente una skill de workflow principal según la capa elegida.
3. Carga también [credentials-and-validation](skills/credentials-and-validation/SKILL.md) si la tarea toca e.firma, `credential_ref`, smoke tests, live tests o logs sensibles.

## Mapa del proyecto

- `sat`
  Núcleo de bajo nivel y sin estado. Mantiene autenticación, envelopes SOAP, validación de solicitudes y operaciones unitarias.
- `satflow`
  Orquestación de alto nivel para Go. Agrega caché de token, refresh, reintentos, polling y descarga completa de paquetes.
- `satservice`
  Servicio tipado sobre Connect, gRPC y gRPC-Web para otros procesos o lenguajes.

## Reglas de trabajo

- Mantén las reglas SAT y la validación de consultas dentro de `sat`; no las dupliques en `satflow`, `satservice`, CLI ni ejemplos.
- Prefiere ejemplos y tests existentes antes de inventar nuevos patrones de uso.
- No subas certificados, llaves, contraseñas, tokens, paquetes ni logs sensibles.
- Si la tarea modifica API pública, contrato Protobuf, validaciones, credenciales o ejemplos, revisa las skills afectadas en el mismo cambio.

## Índice de skills

- [choose-layer](skills/choose-layer/SKILL.md)
  Router inicial para escoger la capa correcta y la siguiente skill.
- [satflow-download-flow](skills/satflow-download-flow/SKILL.md)
  Ruta recomendada para integraciones Go estándar con descarga masiva.
- [sat-low-level-requests](skills/sat-low-level-requests/SKILL.md)
  Uso intencional de `sat.Client` cuando sí hace falta control fino.
- [satservice-remote-integration](skills/satservice-remote-integration/SKILL.md)
  Integración remota mediante `SATService` y `SATFlowService`.
- [credentials-and-validation](skills/credentials-and-validation/SKILL.md)
  Manejo seguro de credenciales, `credential_ref`, smoke tests y validación live.

## Contrato de mantenimiento

Debes revisar `AGENTS.md`, las skills afectadas y el benchmark en `testdata/agent-skills/benchmark.json` cuando cambie cualquiera de estos grupos:

- `README.md`, `docs/*.md`, `examples/**` o `cmd/**` con cambios visibles para integradores
- `proto/satcfdi/v1/service.proto` o clientes generados que cambien el contrato remoto
- `sat/query_validate.go`, `sat/types.go`, `sat/errors.go` o el flujo público de `satflow`
- `satservice/credentials.go`, `satservice/server.go` o tests que cambien credenciales, streaming o mapeo de errores

Mantén las skills delgadas: enlaza a las fuentes de verdad en vez de copiar la documentación completa.

## Validación

- `python3 ./scripts/validate-agent-skills.py`
- `go test ./...`
- `go test -race ./...`
- Benchmark manual para prompts reales: [testdata/agent-skills/benchmark.json](testdata/agent-skills/benchmark.json)
