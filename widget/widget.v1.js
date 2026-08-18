(function () {
    "use strict";

    const script = document.currentScript;

    if (!script) {
        console.error("EmbedLead: unable to determine widget script.");
        return;
    }

    const scriptUrl = new URL(script.src);
    const publicKey = scriptUrl.searchParams.get("key");

    if (!publicKey) {
        console.error("EmbedLead: missing widget public key.");
        return;
    }

    const apiBase = scriptUrl.origin + "/api/v1";

    const container = document.createElement("div");
    container.id = "embedlead-widget";

    container.innerHTML = `
        <div style="
            max-width: 420px;
            padding: 24px;
            border: 1px solid #ddd;
            border-radius: 12px;
            background: #fff;
            font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            box-sizing: border-box;
        ">
            <div style="margin-bottom: 16px;">
                <h2 id="embedlead-title" style="margin: 0 0 6px;">Contact Us</h2>
                <p style="margin: 0; color: #666; font-size: 14px;">
                    Send us a message and we'll get back to you.
                </p>
            </div>

            <form id="embedlead-form">
                <label style="display:block; margin-bottom:12px;">
                    <span style="display:block; margin-bottom:4px;">Name</span>
                    <input
                        name="name"
                        type="text"
                        maxlength="255"
                        style="width:100%; padding:10px; box-sizing:border-box;"
                    >
                </label>

                <label style="display:block; margin-bottom:12px;">
                    <span style="display:block; margin-bottom:4px;">Email</span>
                    <input
                        name="email"
                        type="email"
                        maxlength="255"
                        required
                        style="width:100%; padding:10px; box-sizing:border-box;"
                    >
                </label>

                <label style="display:block; margin-bottom:12px;">
                    <span style="display:block; margin-bottom:4px;">Message</span>
                    <textarea
                        name="message"
                        maxlength="5000"
                        rows="5"
                        style="width:100%; padding:10px; box-sizing:border-box; resize:vertical;"
                    ></textarea>
                </label>

                <input
                    name="website"
                    type="text"
                    tabindex="-1"
                    autocomplete="off"
                    style="position:absolute; left:-9999px;"
                    aria-hidden="true"
                >

                <button
                    type="submit"
                    style="
                        width:100%;
                        padding:11px 16px;
                        border:0;
                        border-radius:8px;
                        background:#111827;
                        color:#fff;
                        cursor:pointer;
                        font-size:15px;
                    "
                >
                    Submit
                </button>

                <p
                    id="embedlead-status"
                    role="status"
                    style="margin:12px 0 0; font-size:14px;"
                ></p>
            </form>
        </div>
    `;

    script.parentNode.insertBefore(container, script.nextSibling);

    const form = container.querySelector("#embedlead-form");
    const status = container.querySelector("#embedlead-status");
    const title = container.querySelector("#embedlead-title");

    async function loadWidgetConfig() {
        try {
            const response = await fetch(
                `${apiBase}/public/widgets/${encodeURIComponent(publicKey)}/config`
            );

            if (!response.ok) {
                throw new Error("Unable to load widget configuration.");
            }

            const config = await response.json();

            if (config.name) {
                title.textContent = config.name;
            }
        } catch (error) {
            console.error("EmbedLead:", error);
        }
    }

    form.addEventListener("submit", async function (event) {
        event.preventDefault();

        const submitButton = form.querySelector("button[type='submit']");
        const formData = new FormData(form);

        const payload = {
            name: formData.get("name") || null,
            email: formData.get("email"),
            message: formData.get("message") || null,
            website: formData.get("website") || null
        };

        submitButton.disabled = true;
        status.textContent = "Submitting...";

        try {
            const response = await fetch(
                `${apiBase}/public/widgets/${encodeURIComponent(publicKey)}/leads`,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
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
        } finally {
            submitButton.disabled = false;
        }
    });

    loadWidgetConfig();
})();
