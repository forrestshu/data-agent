# SQLite snapshots

Place local SQLite snapshots in this directory. Database files are intentionally excluded from Git because the current snapshots exceed common repository file-size limits.

The default development and Docker snapshot is:

```text
data-agent-2026-7-15.sqlite
```

Use `DATA_AGENT_DATABASE` to select another absolute database path.
