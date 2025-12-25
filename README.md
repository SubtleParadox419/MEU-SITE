# Site

Projeto simples com HTML/CSS e CI no GitHub Actions.

## CI e Seguranca

O repositorio inclui:

- Lint automatico para HTML/CSS/JS via GitHub Actions.
- CodeQL para JavaScript, Python, Go e Rust (quando adicionados).
- Auditoria de seguranca para npm, pip, Go e Rust (quando lockfiles existirem).
- Dependabot para atualizacoes de dependencias e Actions.

## Padroes de Dependencias (quando adicionar linguagens)

JavaScript (npm):

- Use `package-lock.json` e prefira `npm ci` em CI.
- Evite `^` e `~` em `package.json` para travar versoes em producao.

Python (pip):

- Fixe versoes em `requirements.txt`.
- Use `pip install -r requirements.txt` com versoes fixas.

Rust:

- Mantenha `Cargo.lock` no repo.

Go:

- Mantenha `go.sum` no repo.

## Comandos basicos

```powershell
# npm (quando houver JS)
npm ci
npm audit

# pip (quando houver Python)
pip install -r requirements.txt
pip audit
```
