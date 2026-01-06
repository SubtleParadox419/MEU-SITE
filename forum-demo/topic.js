const params = new URLSearchParams(window.location.search);
const topicId = Number(params.get('id'));

const titleEl = document.getElementById('topic-title');
const summaryEl = document.getElementById('topic-summary');
const dateEl = document.getElementById('topic-date');
const authorEl = document.getElementById('topic-author');
const tagsEl = document.getElementById('topic-tags');
const contentEl = document.getElementById('topic-content');
const repliesContainer = document.getElementById('replies-container');
const localRepliesContainer = document.getElementById('local-replies');
const replyForm = document.getElementById('reply-form');
const clearButton = document.getElementById('clear-replies');
const nameInput = document.getElementById('reply-name');
const messageInput = document.getElementById('reply-message');

let topic = null;

init();

async function init() {
  if (!topicId) {
    titleEl.textContent = 'Tópico não encontrado';
    return;
  }
  await loadTopic();
  await loadReplies();
  loadLocalReplies();
  replyForm?.addEventListener('submit', handleSubmit);
  clearButton?.addEventListener('click', clearLocalReplies);
}

async function loadTopic() {
  try {
    const res = await fetch('data/topics.json');
    if (!res.ok) throw new Error('Falha ao carregar tópicos');
    const data = await res.json();
    topic = data.find(item => Number(item.id) === topicId);
    if (!topic) {
      titleEl.textContent = 'Tópico não encontrado';
      return;
    }
    renderTopic(topic);
  } catch (err) {
    titleEl.textContent = 'Erro ao carregar tópico (abra via servidor local).';
    console.error(err);
  }
}

function renderTopic(item) {
  titleEl.textContent = item.title;
  summaryEl.textContent = item.summary;
  dateEl.textContent = formatDate(item.date);
  authorEl.textContent = item.author;
  contentEl.textContent = item.content;
  tagsEl.innerHTML = '';
  item.tags.forEach(tag => {
    const pill = document.createElement('span');
    pill.className = 'pill ghost';
    pill.textContent = tag;
    tagsEl.appendChild(pill);
  });
}

async function loadReplies() {
  try {
    const res = await fetch('data/replies.json');
    if (!res.ok) throw new Error('Falha ao carregar respostas');
    const replies = await res.json();
    const filtered = replies.filter(r => Number(r.topicId) === topicId);
    renderReplies(filtered, repliesContainer);
  } catch (err) {
    repliesContainer.textContent = 'Erro ao carregar respostas pré-carregadas.';
    console.error(err);
  }
}

function handleSubmit(event) {
  event.preventDefault();
  if (!topic) return;

  const name = nameInput.value.trim();
  const message = messageInput.value.trim();
  if (!name || !message) return;

  const entry = {
    topicId,
    author: name,
    date: new Date().toISOString(),
    message
  };

  const existing = getStoredReplies();
  const updated = [...existing, entry];
  localStorage.setItem(storageKey(), JSON.stringify(updated));

  renderReplies(updated, localRepliesContainer, true);
  replyForm.reset();
}

function clearLocalReplies() {
  localStorage.removeItem(storageKey());
  localRepliesContainer.innerHTML = '<p>Nenhuma resposta local ainda.</p>';
}

function loadLocalReplies() {
  const stored = getStoredReplies();
  if (!stored.length) {
    localRepliesContainer.innerHTML = '<p>Nenhuma resposta local ainda.</p>';
    return;
  }
  renderReplies(stored, localRepliesContainer, true);
}

function renderReplies(list, container, sortDesc = false) {
  container.innerHTML = '';
  const replies = sortDesc ? [...list].sort((a, b) => new Date(b.date) - new Date(a.date)) : list;
  if (!replies.length) {
    container.textContent = 'Nenhuma resposta para este tópico ainda.';
    return;
  }

  const template = document.getElementById('reply-template');
  const fragment = document.createDocumentFragment();
  replies.forEach(reply => {
    const node = template.content.cloneNode(true);
    node.querySelector('.author').textContent = reply.author;
    node.querySelector('.date').textContent = formatDate(reply.date);
    node.querySelector('.message').textContent = reply.message;
    fragment.appendChild(node);
  });
  container.appendChild(fragment);
}

function storageKey() {
  return `forum-demo-replies-${topicId}`;
}

function getStoredReplies() {
  try {
    const raw = localStorage.getItem(storageKey());
    if (!raw) return [];
    return JSON.parse(raw);
  } catch (err) {
    console.error('Erro ao ler respostas locais', err);
    return [];
  }
}

function formatDate(iso) {
  return new Intl.DateTimeFormat('pt-BR', { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(iso));
}
