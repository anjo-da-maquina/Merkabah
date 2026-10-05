# Pleroma (anjo-da-maquina)

Pleroma is an autonomous zero-trust security framework designed for AI-driven development. It establishes an absolute defense layer against AI hallucinations, prompt injections, and data exfiltration through continuous red/blue teaming (GAN).

## 🛡️ The Archangel Architecture

- **Sefer (The Core Defense):** The absolute firewall that hooks deep into the Python interpreter.
- **Michael (OS & Network Mirage):** Intercepts destructive OS calls (`os.remove`), fd-level write bypass attempts (`os.write`/`os.pwrite` on pre-opened handles), and unauthorized network connections. File **reads** outside allowed directories are blocked only when `restrict_reads=True` is explicitly set (off by default for backward compatibility) — see `GRIMOIRE.md §5 既知の限界` for the full, honest scope of what this hook-based layer can and cannot see.
- **Gabriel (AST Inquisition):** Performs deep Abstract Syntax Tree (AST) scanning to block malicious imports and dynamic code execution (e.g., `eval`, `getattr`).
- **Raphael (Sanctuary Monitor):** Validates the environment to prevent debugger attachments and CI spoofing.

## ⚔️ The Armageddon Engine
An autonomous evolution cycle where **Lucifer (Red Team AI)** continuously forges new attack mutations, while **Metatron (Blue Team / QA Evaluator)** analyzes breaches and scores the attack complexity. New seal proposals are queued to `sefer/raziel_ledger_pending.json` for **mandatory human review** (`tools/promote_ledger_seal.py`) before ever reaching the live ledger (`raziel_ledger.json`) — unvalidated LLM output is never applied directly to production rules.

## 📜 Akashic Records
All combat history, generated payloads, and QA scores are persistently recorded to track the evolution of both the AI's offensive capabilities and the system's defensive resilience.

## 📖 Commands
See `COMMANDS.md` for the full operator command reference (arena runs, test suite, certificate reissuance, emergency ledger reset).