class MonacoModalManager {
    constructor() {
        this._spawnModalCSS();
    }

    _spawnModalCSS() {
        if (document.getElementById("monacoModalCSS")) {
            return;
        }

        let css = document.createElement("style");
        css.id = "monacoModalCSS";
        css.innerHTML = /*css*/ `
            #monacoModal {
                display: none;
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0, 0, 0, 0.5);
                z-index: 100;
            }

            #monacoModal .modal-content {
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                background-color: white;
                padding: 20px;
                border-radius: 5px;
                width: 80%;
                height: 80vh;
                overflow-y: auto;
                background-color: var(--background-color)
            }

            #monacoModal .modal-content .monaco_titlebar {
                display: flex;
                justify-content: space-between;
                align-items: center;
            }

            #monacoModal .modal-content .monaco_titlebar i {
                font-size: 2.5rem;
                margin-right: 1rem;
            }

            #monacoModal .modal-content .monaco_titlebar #monaco_exit:hover {
                color: var(--tertiary-background-color);
                cursor: pointer;
            }

            #monacoModal .modal-content .monaco_titlebar #monaco_save.saved {
                color: var(--success-color);
            }

            #monacoModal .modal-content .monaco_titlebar #monaco_save.saved:hover {
                color: var(--success-color-hover);
                cursor: not-allowed;
            }

            #monacoModal .modal-content .monaco_titlebar #monaco_save:not(.saved) {
                color: var(--error-color);
            }

            #monacoModal .modal-content .monaco_titlebar #monaco_save:not(.saved):hover {
                color: var(--error-color-hover);
                cursor: pointer;
            }

            #monaco_titlebar {
                height: 10%;
            }

            #monaco_filename {
                margin-bottom: 10px;
                font-size: 3rem;
            }

            #monaco-container {
                height: 90%;
                border: 1px solid #000;
            }
        `;
        document.head.appendChild(css);
    }

    _spawnModal() {
        let modal = document.createElement("div");
        modal.id = "monacoModal";
        modal.innerHTML = /*html*/ `
            <div class="modal-content">
                <div class="monaco_titlebar">
                    <h3 id="monaco_filename" contenteditable>unknown_file_name.conf</h3>
                    <div>
                        <i id="monaco_save" class="fa-solid fa-floppy-disk"></i>
                        <i id="monaco_exit" class="fa-solid fa-xmark"></i>
                    </div>
                </div>
                <div id="monaco-container"></div>
            </div>
        `;

        document.body.appendChild(modal);

        document.getElementById("monaco_exit").addEventListener("click", () => {
            this.dismissModal();
        });
    }

    summonModal(filename, content, saveCallback, newfile = false) {
        if (document.getElementById("monacoModal")) {
            this.dismissModal();
        } else {
            this._spawnModal();
        }

        $("#monaco_save").click(() => {
            if ($("#monaco_save").hasClass("saved")) {
                return;
            }

            let filename = $("#monaco_filename").text();
            let value = monaco.editor.getModels()[0].getValue();

            saveCallback(value, filename);
            window.monacoEditorContent = value;
            window.monacoEditorFilename = filename;
            this.checkSaveState();
        });

        document.getElementById("monaco_filename").innerText = filename;
        document.getElementById("monacoModal").style.display = "block";

        monacotheme =
            window.matchMedia &&
            window.matchMedia("(prefers-color-scheme: light)").matches
                ? "nginx-theme"
                : "nginx-theme-dark";

        monaco.editor.create(document.getElementById("monaco-container"), {
            value: content,
            language: "nginx",
            theme: monacotheme,
            scrollBeyondLastLine: false,
            cursorSmoothCaretAnimation: "off",
            fontSize: 16,
            automaticLayout: true,
        });
        if (newfile) {
            window.monacoEditorContent = null;
            window.monacoEditorFilename = null;
        } else {
            window.monacoEditorContent = content;
            window.monacoEditorFilename = filename;
            document.getElementById("monaco_save").classList.add("saved");
        }

        window.monacoKeyUpEvent = monaco.editor.getEditors()[0].onKeyUp(() => {
            this.checkSaveState();
        });

        $("#monaco_filename").on("input", () => {
            this.checkSaveState();
        });

        monaco.editor
            .getEditors()[0]
            .addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS, () => {
                $("#monaco_save").click();
            });
    }

    checkSaveState() {
        if (
            window.monacoEditorContent !==
                monaco.editor.getModels()[0].getValue() ||
            window.monacoEditorFilename !== $("#monaco_filename").text()
        ) {
            document.getElementById("monaco_save").classList.remove("saved");
        } else {
            document.getElementById("monaco_save").classList.add("saved");
        }
    }

    dismissModal() {
        window.monacoKeyUpEvent.dispose();
        document.getElementById("monacoModal").remove();
        monaco.editor.getEditors()[0].dispose();
    }
}
