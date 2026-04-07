---
name: satflow-download-flow
description: Guide normal Go integrations toward satflow for authentication, submit, polling, token caching, and package download without manual low-level orchestration.
---

# satflow-download-flow

## Propósito

Usa esta skill cuando el usuario necesita integrar `go-satcfdi` desde Go para autenticar con e.firma, crear una solicitud SAT, esperar a estado terminal y descargar paquetes sin manejar el token manualmente.

## Cuándo usarla

- Integraciones Go normales dentro del mismo proceso
- Flujos de descarga masiva de CFDI o Metadata
- Tareas que necesitan caché de token, refresh, reintentos, polling y descarga completa

## No usarla

- Si el usuario necesita control fino de `ObtenerToken`, `Consultar`, `VerificarDescarga` o `DescargarPaquete`; usa [sat-low-level-requests](../sat-low-level-requests/SKILL.md)
- Si el consumidor no está en Go o necesita un contrato remoto tipado; usa [satservice-remote-integration](../satservice-remote-integration/SKILL.md)

## Reglas duras

- Prefiere `satflow.New(...)` sobre `sat.NewClient(...)` para flujos estándar en Go.
- `RFCSolicitante` debe corresponder al RFC dueño de la e.firma y de la consulta.
- `satflow.Client` encapsula caché de token, refresh proactivo, reintentos y polling; no repliques eso en capas superiores salvo necesidad explícita.
- Para `Recibidos + CFDI`, usa `EstadoComprobanteVigente` por defecto salvo instrucción explícita en contrario.
- No combines `UUID` con `RFCContrapartes`, `TipoComprobante`, `Complemento`, `RFCACuentaTerceros` ni `EstadoComprobante != Todos`.
- `Recibidos` acepta máximo 1 `RFCContraparte`; `Emitidos`, máximo 5.
- No persistas `.cer`, `.key`, contraseñas ni tokens en código, fixtures o logs.

## Workflow recomendado

1. Construye `*sat.Fiel` con `sat.NewFiel`.
2. Crea `satflow.Client` con `Fiel` y `RFCSolicitante`.
3. Usa `Download(...)` como ruta canónica para `Submit -> Wait -> FetchPackages`.
4. Usa `Authenticate -> Submit -> Wait -> FetchPackages` solo si necesitas inspección paso a paso.
5. Ajusta `PollPolicy`, `RetryPolicy` o `TokenCache` únicamente cuando haya una razón operativa clara.
6. Si cambias contratos o validaciones, verifica también ejemplos y tests antes de cerrar el cambio.

## Ejemplos correctos

```go
fiel, err := sat.NewFiel(cerDER, keyDER, []byte(password))
if err != nil {
	panic(err)
}

flow, err := satflow.New(satflow.Config{
	Fiel:           fiel,
	RFCSolicitante: "XAXX010101000",
})
if err != nil {
	panic(err)
}

result, err := flow.Download(ctx, satflow.DownloadRequest{
	FechaInicial:      fi,
	FechaFinal:        ff,
	TipoDescarga:      sat.TipoDescargaRecibidos,
	TipoSolicitud:     sat.TipoSolicitudCFDI,
	EstadoComprobante: sat.EstadoComprobanteVigente,
})
if err != nil {
	panic(err)
}

_ = result
```

- Si ya existe código usando `Run(...)`, trátalo como alias válido de `Download(...)` en vez de reescribirlo sin necesidad.

## Errores comunes

- Usar `sat.Client.Consultar(...)` con token manual cuando `satflow` era suficiente.
- Omitir `RFCSolicitante` al crear el flow.
- Enviar `Recibidos + CFDI` con `EstadoComprobanteCancelado`.
- Combinar `UUID` con filtros incompatibles.
- Tratar `package_ids` como si ya fueran bytes descargados.
- Reimplementar polling o refresh de token fuera de `satflow`.

## Fuentes de verdad

- [README.md](../../README.md)
- [sat/query_validate.go](../../sat/query_validate.go)
- [satflow/client.go](../../satflow/client.go)
- [satflow/types.go](../../satflow/types.go)
- [examples/satflow-download/main.go](../../examples/satflow-download/main.go)
- [examples/satflow-walkthrough/main.go](../../examples/satflow-walkthrough/main.go)
- [satflow/client_test.go](../../satflow/client_test.go)

## Verificación

- El código nuevo usa `satflow` cuando el flujo es estándar y está dentro de Go.
- Las combinaciones de filtros respetan `sat/query_validate.go`.
- `go test ./...` sigue pasando.
- Si el cambio toca comportamiento de flujo, prueba también `go run ./examples/satflow-download` con credenciales controladas.
