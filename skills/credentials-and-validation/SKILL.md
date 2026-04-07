---
name: credentials-and-validation
description: Handle e.firma material, credential_ref allowlists, smoke tests, live validation, and redaction rules safely when working on go-satcfdi integrations or internals.
---

# credentials-and-validation

## Propósito

Usa esta skill cuando la tarea toque credenciales SAT, `sat.NewFiel`, `credential_ref`, smoke tests, live tests, logs sensibles o validación manual contra SAT.

## Cuándo usarla

- Cambios en `sat.NewFiel`, carga de DER o manejo de contraseñas
- Cambios en `satservice/credentials.go`, `credential_ref` o allowlists
- Smoke tests manuales o pruebas live contra SAT
- Revisión de logs, ejemplos o fixtures que podrían exponer secretos

## No usarla

- Si la tarea es puramente estructural y no toca credenciales, seguridad ni validación operativa
- Si ya existe una skill principal y no hay riesgo de secretos o pruebas live

## Reglas duras

- Nunca subas `.cer`, `.key`, contraseñas, tokens, paquetes ni logs sensibles al repositorio.
- `sat.NewFiel` recibe material DER del certificado y la llave privada; no guardes ese material en código fuente.
- `credential_ref` y `credentials` son mutuamente excluyentes.
- Hoy el proveedor soportado para `credential_ref` es `file`, restringido a directorios permitidos del servidor.
- Revisa y redacta logs antes de compartirlos fuera del entorno controlado.
- Cuando cambies autenticación, descarga, credenciales o servicio tipado, corre `go test ./...` y vuelve a validar el smoke test manual.

## Workflow recomendado

1. Para `sat` o `satflow`, carga credenciales desde archivos locales controlados y construye `*sat.Fiel` con `sat.NewFiel`.
2. Para `satservice`, decide si usarás credenciales inline o un descriptor `credential_ref`.
3. Si usas `credential_ref`, crea un descriptor JSON dentro de un directorio permitido y valida rutas canónicas.
4. Corre la suite local primero y luego el smoke test manual con credenciales controladas.
5. Usa las pruebas live solo cuando la tarea realmente requiera compatibilidad SAT real y las variables de entorno estén disponibles.

## Ejemplos correctos

```json
{
  "certificate_path": "cert.der",
  "private_key_path": "key.der",
  "private_key_password": "password"
}
```

- El descriptor anterior es válido para `credential_ref` con `provider=file` cuando vive dentro de un directorio permitido por `satcfdid`.
- Para smoke tests manuales, sigue la secuencia de [docs/smoke-test.md](../../docs/smoke-test.md) y evita compartir salidas con secretos.

## Errores comunes

- Dejar tokens o contraseñas hardcodeadas en ejemplos, tests o fixtures.
- Aceptar rutas absolutas fuera del allowlist en `credential_ref`.
- Compartir logs sin revisar campos sensibles.
- Tratar la suite live como obligatoria en CI.
- Cambiar manejo de credenciales sin actualizar smoke tests, ejemplos y skills relacionadas.

## Fuentes de verdad

- [README.md](../../README.md)
- [docs/smoke-test.md](../../docs/smoke-test.md)
- [docs/service.md](../../docs/service.md)
- [SECURITY.md](../../SECURITY.md)
- [sat/fiel.go](../../sat/fiel.go)
- [satservice/credentials.go](../../satservice/credentials.go)
- [satservice/live_test.go](../../satservice/live_test.go)
- [satservice/server_extended_test.go](../../satservice/server_extended_test.go)

## Verificación

- No hay secretos, DER ni tokens nuevos en el diff.
- Las rutas de `credential_ref` quedan restringidas al allowlist configurado.
- Los cambios sensibles siguen cubiertos por tests locales y por el smoke test manual documentado.
- La documentación pública y las skills siguen alineadas con el manejo real de credenciales.
