# Requisitos para llevar este sistema a un repositorio privado de una organización

Este repositorio de prueba es público y personal. En una organización con repositorios privados
cambian la seguridad, el coste, el cumplimiento y los permisos. Este documento lista qué hace
falta y por qué.

> Los límites de cuota, los nombres de ajustes y las condiciones contractuales cambian con el
> tiempo. Todo lo marcado con **(verificar)** debe comprobarse en la documentación oficial o con
> el equipo legal antes de decidir.

## 1. Resumen rápido (checklist)

| # | Requisito | Quién lo decide |
|---|---|---|
| 1 | Aprobación de seguridad y legal para enviar código privado a la API de Anthropic | Seguridad / Legal |
| 2 | Cuenta de la API (Consola de Anthropic) de la organización, con límites de gasto | Finanzas / Plataforma |
| 3 | Secret `ANTHROPIC_API_KEY` a nivel de organización o de repo (idealmente en un *environment*) | Admin de GitHub |
| 4 | Actions habilitado y acciones de terceros permitidas (idealmente fijadas por SHA) | Owner de la org |
| 5 | Instalar y aprobar la GitHub App de Claude para los repos concretos | Owner de la org |
| 6 | Permitir que Actions cree PR (o usar una GitHub App propia) | Owner de la org |
| 7 | Rulesets / protección de ramas y CODEOWNERS en `.github/` | Admin del repo |
| 8 | Plan de GitHub con minutos de Actions suficientes | Finanzas |
| 9 | Política sobre quién puede poner las etiquetas que disparan los workflows | Admin del repo |
| 10 | Red y runners compatibles con las salidas necesarias | Plataforma / Red |
| 11 | Auditoría, retención de logs y monitorización de coste | Seguridad / Plataforma |

## 2. Datos, privacidad y cumplimiento

- **El código privado se envía a un servicio externo.** Cada ejecución manda a la API de
  Anthropic el diff, archivos del repo y la descripción de la PR. Hace falta aprobación de
  seguridad y legal antes de activarlo.
- **Contrato y términos.** Para uso corporativo conviene la API con términos comerciales (no un
  token de una suscripción personal). Revisar retención de datos, uso para entrenamiento, DPA y,
  si se necesita, retención cero **(verificar con el contrato)**.
- **Residencia y soberanía de datos.** Si el código no puede salir de cierto proveedor o región,
  la action admite usar Claude a través de Amazon Bedrock o Google Vertex AI con autenticación
  OIDC (por eso existe el permiso `id-token: write`). Claude también puede estar disponible en
  Microsoft Foundry **(verificar disponibilidad y cómo se integra con la action)**.
- **Información sensible.** Los agentes pueden ver cualquier archivo del checkout. No debe haber
  secretos ni datos personales en el repo, y los workflows no deben enviar variables de entorno ni
  secrets en los prompts.
- **Marcos de cumplimiento** (SOC 2, ISO 27001, RGPD, sectoriales): documentar este flujo como un
  tratamiento más de datos y como un proveedor más.

## 3. Cuenta de la API y costes

- **Cuenta organizativa** en la Consola de Anthropic, con un **workspace dedicado** a CI.
- **Una API key por repositorio o entorno**, no compartida con personas. Rotación periódica y
  revocación inmediata si se filtra.
- **Límites de gasto** en el workspace y alertas de consumo.
- **Topes por ejecución** en el propio sistema: `--max-turns` en `claude_args` y en el script,
  `timeout-minutes` en los jobs (ya hay 45 y 20 minutos), `concurrency` por PR (ya existe) y, si
  hace falta, un límite de ejecuciones por día.
- **Estimación**: el pipeline de tests hace como mínimo 3 llamadas a Claude (analista, escritor,
  revisor) y hasta unas 10 si se agotan las rondas. Los revisores añaden 1 llamada por cada
  push a una PR. En equipos con muchas PR esto es coste recurrente y hay que presupuestarlo.
- **Minutos de GitHub Actions.** Los repos públicos no consumen cuota; los privados sí, según el
  plan de la organización **(verificar cuota actual y precio por minuto)**. Cada ejecución
  consume unos 1–5 minutos por workflow.

## 4. Secretos y entornos

- Guardar `ANTHROPIC_API_KEY` como secret **de organización** (con acceso restringido a repos
  concretos) o de repo. Nadie debe pegarla en chats, issues ni archivos.
- Recomendado: un **environment** de GitHub (por ejemplo `claude-ci`) con el secret dentro y
  reglas de protección: ramas permitidas y, si procede, revisores obligatorios.
- **Nunca usar `pull_request_target`** con este tipo de workflows y no pasar secrets a PR de forks.
  En repos privados los forks suelen estar desactivados o limitados; comprobarlo.
- Los workflows actuales solo se ejecutan para PR del propio repo
  (`head.repo.full_name == github.repository`). Mantener esa guarda.

## 5. GitHub Actions: política de la organización

- **Actions habilitado** para el repo y con permiso para ejecutar acciones de terceros.
- **Lista de acciones permitidas** que incluya, como mínimo: `actions/checkout`,
  `actions/setup-python`, `actions/setup-node` y `anthropics/claude-code-action`.
- **Fijar versiones por SHA** (no `@v1` ni `@v4`) y mantenerlas con Dependabot para
  `github-actions`. Lo mismo con `npm install -g @anthropic-ai/claude-code`: fijar versión.
- **Permisos por defecto del `GITHUB_TOKEN`** en solo lectura; cada workflow declara los suyos
  (ya lo hace). Revisar que `contents: write` solo esté en los workflows que lo necesitan
  (`claude-test-pipeline` y `claude-docs`).
- **«Allow GitHub Actions to create and approve pull requests»** debe estar activo a nivel de
  organización y de repo para que los workflows abran PR. Muchas organizaciones lo bloquean:
  hay que pedirlo. Alternativa mejor, ver sección 7.
- Si hay **runners autoalojados**, deben tener Python 3.12, Node 22, `git` y `gh`, y estar
  aislados (efímeros) porque ejecutan código de PR.

## 6. La GitHub App de Claude

- Instalarla en la organización y **limitar el acceso a repos seleccionados**.
- La instalación en una organización requiere aprobación de un **owner**.
- Permisos que necesita: lectura/escritura de contenidos, PR e issues, según el flujo.
- Revisar qué permisos pide la app antes de aprobarla y documentar quién es responsable.
- Para que el bot pueda revisar PR creadas por otro bot hay que usar `allowed_bots` con el
  nombre exacto (`"claude"`), nunca `"*"`.

## 7. Identidad de las PR generadas

Con el `GITHUB_TOKEN`, las PR y pushes creados por los workflows **no disparan otros workflows**.
Eso implica que los checks obligatorios (`tests`, revisores) no se ejecutan sobre las PR de Claude
y, si hay protección de ramas con checks requeridos, **esas PR nunca podrán fusionarse**.

Opciones:
1. **GitHub App propia de la organización** (recomendado): se genera un token de instalación con
   `actions/create-github-app-token` y se usa en `git push` y `gh pr create`. Tiene permisos
   mínimos, identidad propia y auditoría clara.
2. Un PAT de una cuenta de servicio: más sencillo, pero está ligado a una cuenta y suele ser
   más amplio de lo necesario. Evitar PAT de personas.

## 8. Protección de ramas y gobierno del código

- **Rulesets o protección de ramas** en `main`: PR obligatoria, número mínimo de revisores
  humanos, checks requeridos (`tests`), historial lineal si se desea y sin push directo.
- **Que el bot nunca pueda aprobar ni fusionar.** No activar «approve pull requests» para
  Actions si no es imprescindible. Un humano debe revisar y fusionar toda PR generada.
- **Permitir la creación de ramas `claude/*`** al token usado, o restringirla a la App del
  punto 7.
- **CODEOWNERS** sobre `.github/**` (workflows y scripts) y `docs/`: cualquier cambio en estos
  archivos debe requerir la revisión del equipo de plataforma/seguridad. Un workflow con
  `contents: write` y acceso a la API key es una superficie sensible.
- **Revisión humana de lo generado:** los tests y la documentación de Claude son un borrador.
  Ya se vio que el revisor puede aceptar tests debilitados.

## 9. Quién puede disparar el sistema

Los workflows generadores se activan con etiquetas (`generar-tests`, `actualizar-docs`).
Poner una etiqueta requiere al menos permiso de *triage* en el repo, lo que ya limita el acceso.

En una organización conviene además:
- Restringir a un equipo concreto quién tiene ese permiso, o validar en el workflow el actor
  (`github.event.sender`) contra una lista o un equipo.
- Tratar la descripción de la PR, los comentarios y los nombres de archivo como **entrada no
  confiable** (inyección de prompts). Los agentes ya tienen herramientas mínimas y una barrera
  que solo admite archivos nuevos en `tests/`; mantener ese principio de mínimo privilegio y no
  ampliar `--allowedTools` sin revisión.
- Los revisores deben seguir siendo de solo lectura.

## 10. Red y runners

- Los runners alojados por GitHub salen a Internet sin restricciones. Si la organización filtra
  el tráfico saliente o usa runners autoalojados, hay que permitir: `api.anthropic.com`,
  `github.com` / `api.github.com`, el registro de npm y PyPI (o espejos internos).
- Si la organización tiene **lista de IP permitidas** de GitHub, comprobar que no bloquea a la
  App ni a las Actions **(verificar)**.
- Proxies con inspección TLS: configurar los certificados en el runner.

## 11. Auditoría, logs y monitorización

- **Retención de logs de Actions**: los logs contienen salida de los agentes (código y razones).
  Definir cuánto tiempo se conservan y quién puede leerlos.
- **Registro de auditoría** de GitHub: seguimiento de cambios en secrets, workflows, instalaciones
  de Apps y etiquetas.
- **Métricas recomendadas:** ejecuciones por PR, rondas consumidas (¿pasa en la 1 o agota 3?),
  porcentaje de PR de Claude aceptadas, coste por ejecución, y fallos por causa.
- **Alertas** de gasto en la API y de fallos repetidos en los workflows.

## 12. Plan de adopción sugerido

1. Aprobación de seguridad/legal y decisión de proveedor (API directa o Bedrock/Vertex/Foundry).
2. Crear workspace y API key con límite de gasto; guardarla en un environment.
3. Crear la GitHub App propia y aprobar la App de Claude en repos seleccionados.
4. Configurar rulesets, CODEOWNERS y la política de acciones permitidas (con SHA).
5. Piloto en 1–2 repos privados no críticos, con solo los revisores (solo lectura) durante unas
   semanas.
6. Activar el pipeline de tests y la documentación con etiquetas, revisando todas las PR.
7. Medir coste y calidad; endurecer prompts; ampliar a más repos.

## 13. Qué cambiaría en este repositorio al migrarlo

| Archivo | Cambio |
|---|---|
| Todos los workflows | Fijar acciones por SHA; añadir `environment: claude-ci` si se usa |
| `claude-test-pipeline.yml`, `claude-docs.yml` | Token de GitHub App en lugar de `GITHUB_TOKEN` |
| `claude-*.yml` | `--max-turns` y límites de coste; validar el actor que pone la etiqueta |
| `.github/CODEOWNERS` (nuevo) | Propiedad de `.github/**` y `docs/` |
| Ajustes del repo | Rulesets, checks requeridos y política de Actions |
| Dependencias | Versión fija de `@anthropic-ai/claude-code` y de `ruff` |
