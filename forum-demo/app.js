const topicsContainer = document.getElementById('topics');
const searchInput = document.getElementById('search');
const tagFilter = document.getElementById('tag-filter');

let topics = [];
let activeTag = null;

init();

async function init() {
  await loadTopics();
  renderTags();
  renderTopics();
  searchInput?.addEventListener('input', handleFilter);
}

async function loadTopics() {
  try {
    const res = await fetch('data/topics.json');
    if (!res.ok) {
      throw new Error(`Erro ao carregar tópicos: ${res.status}`);
    }
    topics = await res.json();
    topics.sort((a, b) => new Date(b.date) - new Date(a.date));
  } catch (err) {
    topicsContainer.textContent = 'Não foi possível carregar os tópicos. Abra por um servidor local.';
    console.error(err);
  }
}

function renderTags() {
  const uniqueTags = Array.from(new Set(topics.flatMap(t => t.tags))).sort();
  tagFilter.innerHTML = '';

  const allButton = document.createElement('button');
  allButton.textContent = 'Todas as tags';
  allButton.className = activeTag ? 'pill ghost' : 'pill active';
  allButton.addEventListener('click', () => {
    activeTag = null;
    renderTags();
    renderTopics();
  });
  tagFilter.appendChild(allButton);

  uniqueTags.forEach(tag => {
    const button = document.createElement('button');
    button.textContent = tag;
    button.className = `pill ${activeTag === tag ? 'active' : 'ghost'}`;
    button.addEventListener('click', () => {
      activeTag = tag === activeTag ? null : tag;
      renderTags();
      renderTopics();
    });
    tagFilter.appendChild(button);
  });
}

function handleFilter() {
  renderTopics();
}

function matchesFilters(topic) {
  const query = searchInput.value.trim().toLowerCase();
  const matchesSearch = !query || [topic.title, topic.summary, topic.content].some(text =>
    text.toLowerCase().includes(query)
  );
  const matchesTag = !activeTag || topic.tags.includes(activeTag);
  return matchesSearch && matchesTag;
}

function renderTopics() {
  topicsContainer.innerHTML = '';
  const template = document.getElementById('topic-card-template');
  const fragment = document.createDocumentFragment();

  topics.filter(matchesFilters).forEach(topic => {
    const node = template.content.cloneNode(true);
    node.querySelector('.title').textContent = topic.title;
    node.querySelector('.summary').textContent = topic.summary;
    node.querySelector('.date').textContent = formatDate(topic.date);
    node.querySelector('.author').textContent = topic.author;
    node.querySelector('.open-topic').href = `topic.html?id=${topic.id}`;

    const tagList = node.querySelector('.tag-list');
    topic.tags.forEach(tag => {
      const pill = document.createElement('span');
      pill.className = 'pill ghost';
      pill.textContent = tag;
      pill.addEventListener('click', evt => {
        evt.preventDefault();
        activeTag = tag;
        renderTags();
        renderTopics();
      });
      tagList.appendChild(pill);
    });

    fragment.appendChild(node);
  });

  if (!fragment.childNodes.length) {
    const empty = document.createElement('p');
    empty.textContent = 'Nenhum tópico encontrado para esse filtro.';
    topicsContainer.appendChild(empty);
    return;
  }

  topicsContainer.appendChild(fragment);
}

function formatDate(iso) {
  return new Intl.DateTimeFormat('pt-BR', { dateStyle: 'medium' }).format(new Date(iso));
}
