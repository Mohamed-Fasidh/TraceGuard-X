# Security

TraceGuard executes candidate code and therefore treats it as untrusted.

The Docker runner requests:
- `--network none`
- `--read-only`
- `--cap-drop ALL`
- `--security-opt no-new-privileges`
- memory/CPU/PID limits
- timeout
- disposable workspace

This is appropriate for a competition prototype, not a hardened multi-tenant production sandbox.

Do not add secrets, API keys, private source code, or personal data.

TraceGuard never deploys candidate code and never automatically makes consequential human decisions.
