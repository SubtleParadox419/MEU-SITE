(() => {
    const form = document.getElementById("message-form");
    if (!form) {
        return;
    }

    const status = form.querySelector(".form-status");
    const button = form.querySelector("button[type='submit']");
    const endpoint = form.dataset.endpoint || "/api/message";

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

        const data = {
            nome: form.nome.value.trim(),
            email: form.email.value.trim(),
            mensagem: form.mensagem.value.trim()
        };

        if (!data.nome || !data.email || !data.mensagem) {
            setStatus("Preenche tudo, por favor.", "error");
            return;
        }

        try {
            button.disabled = true;
            button.textContent = "Enviando...";

            const response = await fetch(endpoint, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(data)
            });

            if (!response.ok) {
                throw new Error("Falha ao enviar.");
            }

            form.reset();
            setStatus("Mensagem enviada! Valeu por chegar junto.", "success");
        } catch (error) {
            setStatus("Nao foi possivel enviar agora. Tenta de novo depois.", "error");
        } finally {
            button.disabled = false;
            button.textContent = "Enviar mensagem";
        }
    });
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
