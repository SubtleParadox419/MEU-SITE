const postForm = (form, buildPayload, successMessage) => {
    const status = form.querySelector(".form-status");
    const button = form.querySelector("button[type='submit']");
    const endpoint = form.dataset.endpoint;

    const setStatus = (message, type) => {
        if (!status) {
            return;
        }
        status.textContent = message;
        status.classList.remove("success", "error");
        if (type) {
            status.classList.add(type);
        }
    };

    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        setStatus("");

        const payload = buildPayload();
        if (!payload) {
            return;
        }

        try {
            if (button) {
                button.disabled = true;
                button.textContent = "Enviando...";
            }

            const response = await fetch(endpoint, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                throw new Error("Falha ao enviar.");
            }

            form.reset();
            setStatus(successMessage, "success");
        } catch (error) {
            setStatus("Nao foi possivel enviar agora. Tenta de novo depois.", "error");
        } finally {
            if (button) {
                button.disabled = false;
                button.textContent = "Enviar mensagem";
            }
        }
    });
};

(() => {
    const form = document.getElementById("message-form");
    if (!form) {
        return;
    }

    postForm(
        form,
        () => {
            const data = {
                nome: form.nome.value.trim(),
                email: form.email.value.trim(),
                mensagem: form.mensagem.value.trim()
            };
            if (!data.nome || !data.email || !data.mensagem) {
                const status = form.querySelector(".form-status");
                if (status) {
                    status.textContent = "Preenche tudo, por favor.";
                    status.classList.add("error");
                }
                return null;
            }
            return data;
        },
        "Mensagem enviada! Valeu por chegar junto."
    );
})();

(() => {
    const form = document.getElementById("newsletter-form");
    if (!form) {
        return;
    }

    postForm(
        form,
        () => {
            const data = {
                nome: form.nome.value.trim(),
                email: form.email.value.trim()
            };
            if (!data.email) {
                const status = form.querySelector(".form-status");
                if (status) {
                    status.textContent = "Coloca um email valido.";
                    status.classList.add("error");
                }
                return null;
            }
            return data;
        },
        "Fechado! Email cadastrado."
    );
})();

(() => {
    const list = document.getElementById("projects-list");
    if (!list) {
        return;
    }

    fetch("projects.json")
        .then((response) => {
            if (!response.ok) {
                throw new Error("Falha ao carregar projetos.");
            }
            return response.json();
        })
        .then((projects) => {
            list.innerHTML = "";
            projects.forEach((project) => {
                const card = document.createElement("article");
                card.className = "card";
                card.innerHTML = `
                    <h3>${project.title}</h3>
                    <p>${project.description}</p>
                    <div class="tags">
                        ${project.tags.map((tag) => `<span class="tag">${tag}</span>`).join("")}
                    </div>
                    ${project.link ? `<a class="link" href="${project.link}" target="_blank" rel="noreferrer">Ver projeto</a>` : ""}
                `;
                list.appendChild(card);
            });
        })
        .catch(() => {
            list.innerHTML = "<article class=\"card\"><p>Projetos em breve.</p></article>";
        });
})();

(() => {
    const list = document.getElementById("blog-list");
    if (!list) {
        return;
    }

    fetch("blog.json")
        .then((response) => {
            if (!response.ok) {
                throw new Error("Falha ao carregar posts.");
            }
            return response.json();
        })
        .then((posts) => {
            list.innerHTML = "";
            posts.forEach((post) => {
                const card = document.createElement("article");
                card.className = "card blog-card";
                card.innerHTML = `
                    <h3>${post.title}</h3>
                    <p class="blog-meta">${post.date} · ${post.read_time}</p>
                    <p>${post.excerpt}</p>
                    ${post.link ? `<a class="link" href="${post.link}" target="_blank" rel="noreferrer">Ler mais</a>` : ""}
                `;
                list.appendChild(card);
            });
        })
        .catch(() => {
            list.innerHTML = "<article class=\"card\"><p>Posts chegando em breve.</p></article>";
        });
})();

(() => {
    const list = document.getElementById("news-list");
    if (!list) {
        return;
    }

    fetch("news.json")
        .then((response) => {
            if (!response.ok) {
                throw new Error("Falha ao carregar noticias.");
            }
            return response.json();
        })
        .then((items) => {
            list.innerHTML = "";
            items.forEach((item) => {
                const card = document.createElement("article");
                card.className = "card blog-card";
                card.innerHTML = `
                    <h3>${item.title}</h3>
                    <p class="blog-meta">${item.date} · ${item.category}</p>
                    <p>${item.summary}</p>
                    ${item.link ? `<a class="link" href="${item.link}" target="_blank" rel="noreferrer">Ler mais</a>` : ""}
                `;
                list.appendChild(card);
            });
        })
        .catch(() => {
            list.innerHTML = "<article class=\"card\"><p>Noticias chegando em breve.</p></article>";
        });
})();

(() => {
    const list = document.getElementById("forum-list");
    if (!list) {
        return;
    }

    fetch("/api/forum/topics")
        .then((response) => {
            if (!response.ok) {
                throw new Error("Falha ao carregar topicos.");
            }
            return response.json();
        })
        .then((topics) => {
            if (!Array.isArray(topics) || topics.length === 0) {
                list.innerHTML = "<article class=\"card\"><p>Nenhum topico ainda.</p></article>";
                return;
            }
            list.innerHTML = "";
            topics.forEach((topic) => {
                const card = document.createElement("article");
                card.className = "card blog-card";
                card.innerHTML = `
                    <h3>${topic.title}</h3>
                    <p class="blog-meta">${topic.created_at} · ${topic.author}</p>
                    <p>${topic.message}</p>
                `;
                list.appendChild(card);
            });
        })
        .catch(() => {
            list.innerHTML = "<article class=\"card\"><p>Topicos em breve.</p></article>";
        });
})();

(() => {
    const form = document.getElementById("forum-form");
    if (!form) {
        return;
    }

    postForm(
        form,
        () => {
            const data = {
                title: form.titulo.value.trim(),
                author: form.autor.value.trim(),
                message: form.mensagem.value.trim()
            };
            if (!data.title || !data.author || !data.message) {
                const status = form.querySelector(".form-status");
                if (status) {
                    status.textContent = "Preenche tudo, por favor.";
                    status.classList.add("error");
                }
                return null;
            }
            return data;
        },
        "Topico criado! Valeu por compartilhar."
    );
})();
