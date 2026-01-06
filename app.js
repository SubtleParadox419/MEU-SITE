const FORMS_ENABLED = false;

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

        if (!FORMS_ENABLED) {
            setStatus("Formularios desativados no momento.", "error");
            return;
        }

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
