# Merkabah: Zero-Trust OS Fortress for Local AI Agents

I was terrified of giving local LLMs and autonomous agents terminal access. Building sandboxes and Docker containers for every small AI script felt like overkill, but leaving `os.system` exposed is a security nightmare.

So I built **Merkabah**. 

It’s a lightweight, zero-dependency Python package that intercepts and physically blocks malicious system calls (like `rm -rf /`) at the OS level using `sys.addaudithook` and AST parsing. 

Just import it, and your environment is sealed.

## 🚀 Quick Start (The Canon)

https://github.com/anjo-da-maquina/Merkabah/raw/main/assets/demo.mp4

Merkabah operates as a parasite. You don't need complex configurations. Just add one line to the top of your AI agent's code:

```python
import merkabah
# Your AI code here...
```

The moment it's imported, the absolute defense hook is deployed deep within the OS. Any attempt by the AI to spawn unauthorized subprograms or shell commands will be instantly blocked with a `RuntimeError`.

## 🏛️️ Architecture: The Archangel Metaphor

To maintain a strict, universally understandable separation of concerns, the defense layers are mapped to the concept of Archangels:

*   **Michael (OS Deep Hook):** Uses Python's native `sys.addaudithook` to physically intercept and block unauthorized `os.system`, `subprocess.Popen`, and `os.exec` calls at runtime.
*   **Gabriel (AST Inquisition):** Parses the Abstract Syntax Tree of AI-generated code *before* execution to detect and reject the summoning of banned modules (e.g., `os`, `shlex`).
*   **Raphael (Environment Seal):** Audits the execution environment upon startup, ensuring the code isn't running in unapproved/polluted external cloud CI/CD pipelines.

## 📜 Extensibility (Local Doctrines)

You can define your own local rules without touching the core code (The Canon).

*   **The Rubrics (`rubric.json`):** A simple configuration file in your root directory where you can define project-specific banned modules (e.g., block `socket` to prevent phone-home attacks).
*   **The Homilies (`homilies/`):** A directory for custom Python plugins (MODs). Drop your custom validation logic here, and Merkabah will dynamically load them at startup.

## License
MIT