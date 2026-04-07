---
name: sat-low-level-requests
description: Use sat.Client directly for intentional low-level control over authentication, query submission, verification, package download, and CFDI validation without reimplementing SAT rules.
---

# sat-low-level-requests

## Propósito

Usa esta skill cuando el usuario sí necesita control explícito sobre autenticación, token SAT, solicitud de descarga, verificación, descarga de paquetes o validación de CFDI usando `sat.Client`.

## Cuándo usarla

- Integraciones Go que requieren separar `ObtenerToken`, `Consultar`, `VerificarDescarga` o `DescargarPaquete`
- Casos donde ya existe un token SAT y no quieres delegar su ciclo de vida a `satflow`
- Cambios de validación, errores SAT o construcción de requests en el core

## No usarla

- Si el flujo estándar dentro de Go no necesita control fino; usa [satflow-download-flow](../satflow-download-flow/SKILL.md)
- Si el consumidor es remoto o multilenguaje; usa [satservice-remote-integration](../satservice-remote-integration/SKILL.md)

## Reglas duras

- `sat.Client` es una capa de operaciones unitarias y sin estado; el token, la Fiel y los requests viven en el llamador.
- Usa `ObtenerToken` para autenticar y reutiliza el token vigente; no inventes un almacenamiento opaco dentro de `sat`.
- Mantén la validación de filtros y combinaciones en `sat/query_validate.go`.
- No reconstruyas envelopes SOAP o firmado XML fuera de `sat`.
- Si un cambio en `sat` afecta a `satflow` o `satservice`, actualiza también las capas que dependen de ese comportamiento.
- Usa `ObtenerEstadoCFDI` solo para validación de CFDI; no lo mezcles con el flujo de descarga masiva.

## Workflow recomendado

1. Crea `*sat.Fiel` con `sat.NewFiel`.
2. Construye un `sat.Client` con `sat.NewClient(...)`.
3. Llama `ObtenerToken(...)` si no tienes un token SAT vigente.
4. Construye `sat.ConsultaRequest` respetando las reglas de `sat/query_validate.go`.
5. Ejecuta `Consultar -> VerificarDescarga -> DescargarPaquete` solo en el orden que tu caso requiera.
6. Si tocas validación o errores, revisa tests del paquete `sat` y el impacto en `satflow`/`satservice`.

## Ejemplos correctos

```go
client := sat.NewClient(sat.Config{})

token, err := client.ObtenerToken(ctx, fiel)
if err != nil {
	panic(err)
}

resp, err := client.Consultar(ctx, fiel, sat.ConsultaRequest{
	Token:              token,
	RFCSolicitante:     "XAXX010101000",
	FechaInicial:       fi,
	FechaFinal:         ff,
	TipoDescarga:       sat.TipoDescargaEmitidos,
	TipoSolicitud:      sat.TipoSolicitudMetadata,
	EstadoComprobante:  sat.EstadoComprobanteTodos,
	RFCContrapartes:    []string{"AAA010101AAA"},
})
if err != nil {
	panic(err)
}

_ = resp
```

- Para validar un CFDI usa `client.ObtenerEstadoCFDI(ctx, sat.ValidacionRequest{...})` en un flujo separado.

## Errores comunes

- Usar `sat` para un flujo estándar y terminar duplicando lo que ya resuelve `satflow`.
- Saltarse `sat/query_validate.go` y construir combinaciones inválidas de filtros.
- Tratar `sat.Client` como si tuviera caché de token o estado interno de orquestación.
- Tocar reglas de validación en CLI o `satservice` en vez de hacerlo en `sat`.
- Mezclar validación de CFDI con solicitudes de descarga masiva.

## Fuentes de verdad

- [README.md](../../README.md)
- [sat/client.go](../../sat/client.go)
- [sat/types.go](../../sat/types.go)
- [sat/query_validate.go](../../sat/query_validate.go)
- [sat/errors.go](../../sat/errors.go)
- [sat/client_test.go](../../sat/client_test.go)
- [cmd/satcfdi/commands.go](../../cmd/satcfdi/commands.go)

## Verificación

- El cambio realmente requiere control fino y no sería más simple con `satflow`.
- La validación sigue centralizada en `sat`.
- Los tests relevantes de `sat` cubren el comportamiento tocado.
- `go test ./...` sigue pasando después del cambio.
