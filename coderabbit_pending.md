<summary>­ƒñû Prompt for all review comments with AI agents</summary>

```
Verify each finding against current code. Fix only still-valid issues, skip the
rest with a brief reason, keep changes minimal, and validate.

Inline comments:
In `@backend/app/api/metrics.py`:
- Around line 265-278: Add an explicit return type annotation "-> None" to the
inner function validate_version_ownership to satisfy strict typing; locate the
async def validate_version_ownership(version_id: UUID) that uses PromptVersion,
Prompt, user, db and raises HTTPException and change its signature to include
the return type (async def validate_version_ownership(version_id: UUID) ->
None:), leaving the body and logic (select of PromptVersion join Prompt,
db.execute, scalar_one_or_none check and HTTPException raise) unchanged.

In `@backend/app/api/prompts.py`:
- Around line 214-217: In the except block handling errors during prompt
duplication (where db.rollback() is awaited), change the current plain re-raise
of HTTPException to chain the original exception (variable e) so the original
traceback is preserved; specifically, raise the HTTPException used there with
"from e" (keep the same status_code and detail) to maintain exception context
for debugging.

In `@backend/app/api/tests.py`:
- Around line 179-181: The except block that catches Exception in
backend/app/api/tests.py currently re-raises an HTTPException without preserving
the original exception chain; update the re-raise to preserve or suppress
context explicitly (use "raise HTTPException(status_code=500, detail='Failed to
queue bulk tests') from e" to keep the original traceback, or "from None" if you
want to hide it) so the original error is preserved for debugging while keeping
the existing await db.rollback() behavior in that except branch.

In `@backend/app/api/versions.py`:
- Around line 222-224: The exception handler in backend/app/api/versions.py
currently does a rollback then raises a new HTTPException losing the original
traceback; update the except block that catches Exception as e (the code
referencing db.rollback and HTTPException) to re-raise the HTTPException using
"raise HTTPException(... ) from e" so the original exception e is chained and
the original traceback is preserved.

In `@backend/app/core/security.py`:
- Around line 16-17: Normalize the ENVIRONMENT variable before comparing by
reading env = os.environ.get("ENVIRONMENT", "") then applying .strip().lower()
and compare against accepted production values like "production" and "prod";
only if it matches production values and JWT secret is missing
(os.environ.get("JWT_SECRET") is falsy) raise the RuntimeError("JWT_SECRET is
required in production environment."); update the check in the module-level code
in security.py where ENVIRONMENT and JWT_SECRET are referenced.

In `@backend/entrypoint.sh`:
- Around line 19-20: A checagem de disponibilidade do Postgres est├í usando
vari├íveis POSTGRES_* em vez dos aliases DB_* definidos nos defaults; atualize a
exporta├º├úo e o comando psql para usar DB_PASSWORD, DB_HOST, DB_PORT, DB_USER e
DB_NAME (substituir PGPASSWORD="$POSTGRES_PASSWORD" por
PGPASSWORD="$DB_PASSWORD" e trocar os flags -h, -p, -U, -d para usar $DB_HOST,
$DB_PORT, $DB_USER, $DB_NAME) para respeitar os defaults j├í calculados e evitar
inconsist├¬ncias com as vari├íveis padr├úo.

In `@backend/seed_database.py`:
- Around line 59-62: In the except block that catches Exception as e in
backend/seed_database.py (the block that prints the seed failure, calls await
session.rollback()), replace the explicit re-raise "raise e" with a bare "raise"
so the original traceback is preserved (per Ruff TRY201); keep the print and
await session.rollback() calls intact and only change the final re-raise.

In `@coderabbit.md`:
- Around line 205-213: Remove the plaintext credential found in
.validation_user.txt (referenced from coderabbit.md), replace that line with a
non-sensitive fixture like user@example.test|Password1! or delete the file if
unused, then purge the secret from the Git history using git filter-repo or BFG
and force-push the branch; if the exposed credential was ever used, rotate it
immediately; finally add the sensitive filename pattern (.validation_user.txt or
similar) to .gitignore and update contributor docs to prevent re-commit.

In `@frontend/src/index.css`:
- Around line 60-61: As cores est├úo hardcoded nas classes .override-badge-inline
e .override-badge-lg; substitua os valores hex (`#ffc107` e `#000`) por vari├íveis
CSS globais de tema (por exemplo --color-warning-bg e --color-on-warning) e
mantenha os outros estilos; atualize ambas as classes (.override-badge-inline e
.override-badge-lg) para usar essas vari├íveis para background-color e color,
garantindo consist├¬ncia com o sistema de theming do projeto.

---

Outside diff comments:
In `@backend/app/api/playground.py`:
- Around line 118-128: The code calls json.loads and references
json.JSONDecodeError in the playprompt handling (see json.loads and
json.JSONDecodeError usage in the block around final_prompt/template.render),
but the json module is not imported; add "import json" at the top of the module
so json.loads and json.JSONDecodeError resolve at runtime.

In `@backend/scripts/sandboxai_cli.py`:
- Around line 73-83: O loop de polling infinito em torno de status_url (bloco
starting with "while True" que faz urllib.request.urlopen e checa
data["status"]) precisa de um deadline para n├úo travar o CI; adicione antes do
loop um timestamp de in├¡cio e uma configura├º├úo de timeout m├íximo (por exemplo
max_wait_seconds ou deadline_timestamp), e dentro do loop, a cada itera├º├úo
verifique se o tempo decorrido excedeu esse limite e ent├úo registre um
erro/levante exce├º├úo ou retorne com c├│digo de erro, em vez de continuar
indefinidamente; mantenha o comportamento atual de sleep(5) para RUNNING, mas
garanta que o loop termine quando o deadline for atingido.
- Around line 42-43: The code builds run_url from SANDBOXAI_API_URL (base_url)
and then uses it without validating the URL scheme, enabling SSRF via file:// or
other schemes; before using base_url (and before calling urlopen), parse it
(e.g., with urllib.parse.urlparse) and ensure the scheme is either "http" or
"https" and netloc is present, otherwise reject/log the value and fall back to
the safe default ("http://localhost:8000") or raise/exit; update any code that
references base_url or run_url to use the validated/sanitized value so urlopen
only ever receives an http(s) URL.

In `@frontend/src/components/BulkResults.tsx`:
- Around line 23-25: No componente BulkResults, a extra├º├úo direta de batch_id
com results[0].batch_id pode ser undefined/vazio e causar falha em
apiClient.exportTests; antes de chamar exportTests verifique que results existe
e tem pelo menos um item com um batch_id v├ílido (n├úo vazio), preferencialmente
procurando o primeiro resultado com batch_id n├úo vazio (ex.: iterar results at├®
encontrar um batch_id v├ílido), e se n├úo encontrar mostre um feedback claro ao
usu├írio (erro/toast) e impe├ºa a chamada; referencie as vari├íveis/functions
batchId, results e apiClient.exportTests ao aplicar esta valida├º├úo.

---

Duplicate comments:
In `@backend/app/api/auth.py`:
- Around line 133-136: The get_current_user endpoint is reading a Header named
"token" so it doesn't receive the standard "Authorization: Bearer ..." header;
replace the header extraction with a proper OAuth2 bearer extractor (or set
Header(..., alias="Authorization") and strip the "Bearer " prefix) to obtain the
raw token. Specifically, update the token parameter in get_current_user to use
OAuth2PasswordBearer via a shared oauth2_scheme dependency (or use
Header(alias="Authorization")) and ensure you normalize the value by removing
the "Bearer " prefix before validation.

In `@backend/tests/test_e2e_models.py`:
- Around line 60-62: O teste usa corretamente with pytest.raises(IntegrityError)
ao chamar await db_session.commit(), mas n├úo limpa o estado da sess├úo; ap├│s o
bloco que espera a IntegrityError voc├¬ deve chamar await db_session.rollback()
para reverter a transa├º├úo e evitar efeitos colaterais em testes seguintes;
localize o trecho que usa db_session.commit() dentro do contexto
pytest.raises(IntegrityError) e acrescente uma chamada a db_session.rollback()
(await db_session.rollback()) logo ap├│s esse bloco.

In `@MISSION.md`:
- Line 3: Atualize o marcador de status no arquivo MISSION.md: substitua a
string "**Status:** Done" pela indica├º├úo correta do estado do PR (por exemplo
"**Status:** In Progress" ou "**Status:** Open") para refletir que o PR ainda
est├í aberto; procure pela ocorr├¬ncia literal "**Status:** Done" no conte├║do e
altere apenas esse token mantendo o restante do arquivo inalterado.
```

</details>
