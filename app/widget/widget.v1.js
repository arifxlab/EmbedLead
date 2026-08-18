(function () {
    "use strict";

    const script = document.currentScript;

    if (!script) {
        console.error("EmbedLead: unable to determine the widget script.");
        return;
    }

    const scriptUrl = new URL(script.src);
    const publicKey = scriptUrl.searchParams.get("key");

    if (!publicKey) {
        console.error("EmbedLead: missing widget public key.");
        return;
    }

    const apiBaseUrl = scriptUrl.origin + scriptUrl.pathname.replace(/\/widget\.v1\.js$/, "");

    async function loadConfig() {
        const response = await fetch(
            `${apiBaseUrl}/public/widgets/${encodeURIComponent(publicKey)}/config`,
            {
                method: "GET",
                headers: {
                    "Accept": "application/json"
                }
            }
        );

        if (!response.ok) {
            throw new Error("Unable to load widget configuration.");
        }

        return response.json();
    }

    function createWidget(config) {
        const container = document.createElement("div");

        container.id = `embedlead-widget-${config.id}`;

        container.innerHTML = `
            <form style="max-width: 420px; display: grid; gap: 12px;">
                <h3>${escapeHtml(config.name)}</h3>

                <label>
                    Name
                    <input
                        type="text"
                        name="name"
                        maxlength="255"
                    />
                </label>

                <label>
                    Email
                    <input
                        type="email"
                        name="email"
                        maxlength="320"
                        required
                    />
                </label>

                <label>
                    Message
                    <textarea
                        name="message"
                        maxlength="5000"
                    ></textarea>
                </label>

                <button type="submit">
                    Submit
                </button>

                <div
                    data-embedlead-status
                    role="status"
                    aria-live="polite"
                ></div>
            </form>
        `;

        document.body.appendChild(container);

        const form = container.querySelector("form");
        const status = container.querySelector("[data-embedlead-status]");

        if (!form || !status) {
            return;
        }

        form.addEventListener("submit", async function (event) {
            event.preventDefault();

            const formData = new FormData(form);

            const payload = {
                name: formData.get("name") || null,
                email: formData.get("email"),
                message: formData.get("message") || null
            };

            status.textContent = "Submitting...";

            try {
                const response = await fetch(
                    `${apiBaseUrl}/public/widgets/${encodeURIComponent(publicKey)}/leads`,
                    {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                            "Accept": "application/json"
                        },
                        body: JSON.stringify(payload)
                    }
                );

                const result = await response.json();

                if (!response.ok) {
                    throw new Error(
                        result.detail || "Unable to submit your message."
                    );
                }

                form.reset();
                status.textContent = result.message || "Lead submitted successfully.";
            } catch (error) {
                status.textContent =
                    error instanceof Error
                        ? error.message
                        : "Unable to submit your message.";
            }
        });
    }

    function escapeHtml(value) {
        return String(value)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    loadConfig()
        .then(createWidget)
        .catch(function (error) {
            console.error("EmbedLead:", error);
        });
})();

