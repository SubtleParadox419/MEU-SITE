## Mini fórum estático

Site simples em HTML/CSS/JS puro com lista de tópicos, busca, filtro por tags e página de tópico com respostas locais em `localStorage`.

### Rodar localmente
1. Instale qualquer servidor estático (ex.: já vem com Python).
2. No diretório do projeto, execute um deles:
   - `python -m http.server 8000`
   - `npx serve` (se tiver Node)
3. Abra `http://localhost:8000` no navegador.

> É necessário servir os arquivos, pois `fetch` de `data/*.json` não funciona em `file://`.

### Estrutura
- `index.html`: lista de tópicos com busca (título/resumo/conteúdo) e filtro por tags.
- `topic.html`: exibe um tópico por `?id=` e mostra respostas pré-carregadas e locais.
- `app.js`: carrega `data/topics.json`, renderiza cards, ordena por data desc, busca e tags clicáveis.
- `topic.js`: carrega o tópico, exibe replies de `data/replies.json` e respostas locais em `localStorage`.
- `styles.css`: layout minimalista, responsivo, fonte system.
- `data/topics.json`: tópicos exemplo.
- `data/replies.json`: replies pré-carregadas (opcional).

### Editar ou criar posts
- Edite `data/topics.json` para alterar título, resumo, conteúdo ou tags.
- Inclua novos tópicos seguindo o mesmo formato e incrementando `id`.
- Para respostas pré-carregadas, adicione itens em `data/replies.json` com `topicId` correspondente.

### Demonstração das respostas locais
- Campo nome + mensagem salva em `localStorage` com timestamp e `topicId`.
- Botão “Limpar respostas locais deste tópico” apaga somente o registro daquele tópico.
- Texto é sempre renderizado com `textContent` para evitar XSS.
