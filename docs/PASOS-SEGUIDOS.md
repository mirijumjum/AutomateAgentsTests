# Pasos seguidos: automatización de revisión y generación de tests con Claude

Documento de referencia de cómo se construyó el sistema en este repositorio de prueba
(`AutomateAgentsTests`), qué problemas aparecieron y cómo se resolvieron.

## 1. Punto de partida

- Proyecto Python mínimo con funciones `sumar`, `restar` y `dividir`.
- Rama `main` con los workflows; rama `prueba-agente` con una PR (#1) que añade `media()` y
  `porcentaje()` **sin tests, a propósito**, para que el revisor lo detecte.
- Intento previo con GitHub Agentic Workflows (`gh-aw`) abandonado: Copilot Free no lo soporta.
  No debe quedar ningún `pr-test-reviewer.md` ni `pr-test-reviewer.lock.yml` en ninguna rama.

### Diferencias encontradas entre lo descrito y lo real
- No existían `src/calculadora.py` ni `tests/`: había `main.py` en la raíz (en `main`) y
  `src/main.py` (en `prueba-agente`).
- `requirements.txt` y `claude-review.yml` estaban **vacíos** en `main`.
- `pr-test-reviewer.md` seguía presente en ambas ramas.
- Sin ningún test, `python -m pytest` termina con código 5 («no tests ran») y el job `tests`
  nunca puede quedar en verde.

## 2. Estabilización de `main` (revisión de tests con CI)

1. `requirements.txt` con `pytest`, en UTF-8 sin BOM.
2. `tests.yml`: se ejecuta en `pull_request` y en `push` a `main`, con Python 3.12; instala
   dependencias y ejecuta `python -m pytest -v`.
3. `claude-review.yml`: en `pull_request` (`opened`, `synchronize`, `reopened`) usa
   `anthropics/claude-code-action@v1`, con permisos `contents: read`, `pull-requests: write`,
   `issues: write`, `id-token: write`. El prompt pide revisar el diff centrándose en tests
   (comportamiento sin tests, casos límite, test mínimo que falta) y publicar la revisión con
   `gh pr comment`, en español. Herramientas permitidas: `gh pr comment/diff/view`, `Read`,
   `Glob`, `Grep`.
4. `tests/test_calculadora.py` con tests mínimos de `sumar`, `restar` y `dividir` (nunca de
   `media`/`porcentaje`), para que `pytest` no salga con código 5. El import prueba `src.main` y
   cae a `main`.
5. Se elimina `pr-test-reviewer.md` de `main`.
6. Validación: YAML parseado con PyYAML, archivos no vacíos, `requirements.txt` sin BOM y tests
   ejecutados en local.

## 3. Merge en `prueba-agente`

`git merge main` produjo conflictos en `claude-review.yml` y `requirements.txt` (solo
diferencias de saltos de línea/contenido equivalente) y un conflicto modify/delete en
`pr-test-reviewer.md`. Se resolvieron tomando la versión de `main` y borrando el `.md`. No se
tocó `src/`. Sin force push.

Resultado: `tests` en verde y `claude-review` publicó un comentario que detectó que `media()` y
`porcentaje()` no tenían tests y que `media([])` y `porcentaje(x, 0)` lanzan `ZeroDivisionError`
(inconsistente con `dividir`, que lanza `ValueError`).

## 4. Generación automática de tests (primera versión)

Workflow `claude-write-tests` disparado por la etiqueta `generar-tests`: Claude escribía tests,
los ejecutaba y abría una PR con base en la rama de la PR original.

Problemas y arreglos:
- **Se subieron archivos `.pyc`** a la PR generada porque no había `.gitignore`. Se añadió un
  `.gitignore` de Python y se limpiaron con un commit normal.
- La etiqueta no existía: hubo que crearla.

## 5. Pipeline multiagente de tests (versión actual)

Reemplaza a `claude-write-tests`. Archivos:
- `.github/workflows/claude-test-pipeline.yml` (disparador y entorno).
- `.github/scripts/claude_test_pipeline.sh` (lógica).

Flujo (presupuesto único de **3 rondas**):

```
etiqueta generar-tests
  → Analista (lee diff y descripción de la PR; extrae criterios de aceptación)
      · si no hay criterios: comenta y termina
  → por ronda (máx. 3):
      Escritor (happy paths + edge cases, solo archivos nuevos en tests/)
      → Revisor de tests (solo lectura) → rechaza: vuelve al escritor
      → pytest (determinista)
          · pasa: se crea la PR
          · falla: Triage (solo lectura)
              · fallo en el CÓDIGO: comenta en la PR original y termina, sin PR
              · fallo en los TESTS: vuelve al escritor
  → si se agotan las rondas: comenta el historial y el job termina en rojo
```

Decisiones de diseño:
- El bucle y los límites los cuenta el **script**, no un prompt. Claude solo emite juicios.
- Los veredictos son una línea final `VERDICT: <valor>` (APROBADO/RECHAZADO,
  TEST/CODIGO, OK/SIN_CRITERIOS) que el script parsea.
- Barrera determinista: si el escritor modifica algo que no sea un archivo **nuevo** en
  `tests/`, el pipeline se detiene.
- Los revisores solo tienen herramientas de lectura.
- La descripción de la PR se trata como datos, no como instrucciones.
- Guardas del workflow: solo PR del mismo repo, nunca ramas `claude/*` (evita bucles), y
  `concurrency` por PR.

## 6. Revisor de código

`claude-code-review.yml`, en cada PR:
- Parte determinista: `ruff` y `grep` de TODO/FIXME/XXX/HACK, `print(`, `breakpoint(`, `pdb`
  y código comentado en las líneas añadidas.
- Parte de Claude: confirma o descarta lo anterior y busca code smells (duplicación, nombres,
  validación de entradas, errores inconsistentes). Publica un único comentario.
- `requirements-dev.txt` instala `ruff`.

## 7. Documentación automática

`claude-docs.yml`, con la etiqueta `actualizar-docs`: edita únicamente `README.md` y `docs/`, y
abre una PR aparte con base en la rama de la PR. El prompt exige documentar solo lo que existe en
el código.

## 8. Pruebas realizadas

| Caso | Resultado |
|---|---|
| Revisión de tests en la PR #1 | Detectó la falta de tests y los casos límite |
| Pipeline de tests, camino feliz | Pasó en la ronda 1 y creó la PR #7 |
| Documentación | Creó la PR #8 con un README fiel al código |
| Bug en el código (`maximo` con `min`) | Triage `CODIGO`, comentario, sin PR de tests |
| Reintento (criterio de `==` con flotantes) | Falló en la ronda 1, pasó en la 2 (PR #11) |
| Agotamiento de las 3 rondas | **No probado** |
| Parada por falta de criterios | **No probado** |

## 9. Problemas encontrados y soluciones

| Problema | Causa | Solución |
|---|---|---|
| `pytest` sale con código 5 | No había ningún test | Tests mínimos de funciones existentes |
| `.pyc` en la PR generada | Sin `.gitignore` | `.gitignore` + commit de limpieza |
| `Workflow initiated by non-human actor: claude` | La action no se ejecuta si el actor es un bot | `allowed_bots: "claude"` en los dos revisores (no usar `"*"`) |
| Run con 0 jobs y en rojo | Fallo transitorio de arranque en GitHub Actions | Relanzar con `gh run rerun <id>`; no era del repo |
| Scripts `.sh` con CRLF en Windows | `autocrlf` | `*.sh text eol=lf` en `.gitattributes` |
| Una PR creada con `GITHUB_TOKEN` no dispara otros workflows | Limitación de GitHub | Aceptado en la prueba; en producción usar un token de GitHub App |

## 10. Cambio de autenticación: de OAuth a API key

Antes se usaba `CLAUDE_CODE_OAUTH_TOKEN` (ligado a una suscripción personal). Ahora se usa
`ANTHROPIC_API_KEY`, que da coste medible por uso y no compite con el uso interactivo.

Archivos afectados:
- `claude-review.yml`, `claude-code-review.yml`, `claude-docs.yml`:
  `claude_code_oauth_token` → `anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}`.
- `claude-test-pipeline.yml`: la variable de entorno pasa a `ANTHROPIC_API_KEY`.
- `claude_test_pipeline.sh`: falla con un mensaje claro si falta el secret.

Pasos para activarlo (los hace una persona con permisos, nadie debe pegar la clave en un chat ni
en un archivo):

1. Crear una API key en la Consola de Anthropic, a ser posible en un workspace dedicado y con un
   límite de gasto.
2. Guardarla como secret:
   ```powershell
   gh secret set ANTHROPIC_API_KEY
   ```
   (pide el valor de forma interactiva).
3. Fusionar la PR del cambio.
4. Retirar `CLAUDE_CODE_OAUTH_TOKEN` cuando se confirme que todo funciona.

## 11. Cómo se usa

| Acción | Cómo |
|---|---|
| Revisión de tests y de código | Automática en cada PR |
| Generar tests | Poner la etiqueta `generar-tests` (la PR necesita criterios de aceptación en su descripción) |
| Actualizar documentación | Poner la etiqueta `actualizar-docs` |
| Relanzar | Quitar y volver a poner la etiqueta |

## 12. Mapa de archivos

```
.github/
  scripts/claude_test_pipeline.sh
  workflows/
    tests.yml                 CI de pytest
    claude-review.yml         revisor de tests
    claude-code-review.yml    revisor de código (ruff + smells)
    claude-test-pipeline.yml  pipeline multiagente de tests
    claude-docs.yml           documentación automática
tests/                        tests del proyecto
requirements.txt              pytest
requirements-dev.txt          ruff
.gitignore  .gitattributes
docs/                         esta documentación
```

## 13. Pendientes y límites conocidos

- Probar el agotamiento de las 3 rondas y la parada por falta de criterios.
- El revisor puede aceptar tests debilitados (por ejemplo `xfail` o tolerancias que no vienen de
  los criterios). Conviene endurecer los prompts.
- Falta un tope de coste por ejecución y métricas de éxito por ronda.
- Las PR creadas con `GITHUB_TOKEN` no disparan otros workflows.
- Ver `docs/REQUISITOS-ORGANIZACION.md` para llevarlo a un repositorio privado de una organización.
