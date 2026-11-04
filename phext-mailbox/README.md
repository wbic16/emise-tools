# phext-mailbox

`phext_mailbox.py` — archive a `/chat/<name>` file mailbox into a single phext file.

Parametrized copy of Grok Bot's `/chat/grok/phext_mailbox.py` (Will Bickford, 2026-11-04), made by Emise at Will's direction. The original hardcoded its installation: root = the script's directory, fixed archive/lock names, and a shebang pointing at Grok's virtualenv. This copy takes every installation-specific value as a parameter:

| parameter | CLI flag | environment variable | default |
|---|---|---|---|
| mailbox root | `--root DIR` | `PHEXT_MAILBOX_ROOT` | directory of the script |
| mailbox name | `--name NAME` | `PHEXT_MAILBOX_NAME` | basename of root |
| archive file | `--archive FILE` | `PHEXT_MAILBOX_ARCHIVE` | `<root>/mailbox.phext` |
| lock file | `--lock FILE` | `PHEXT_MAILBOX_LOCK` | `<root>/.mailbox.lock` |
| inbox dir | `--inbox NAME` | `PHEXT_MAILBOX_INBOX` | `<root>/inbox` |
| outbox dir | `--outbox NAME` | `PHEXT_MAILBOX_OUTBOX` | `<root>/outbox` |
| libraries | `--inbox-library N` / `--outbox-library N` / `--index-library N` | — | 1 / 2 / 3 |

With no parameters, invoked from its own directory, it behaves exactly like the original — same message naming scheme (`YYYYMMDDTHHMMSSZ-<from>-<topic>.md`), same coordinate scheme (library 1 = inbox, 2 = outbox, 3 = index; shelf = month, series = day, book = nth message that day), same verify-before-delete compact.

Commands: `init`, `compact [--dry-run]`, `list`, `show <coordinate>`.

One behaviour fix vs the original: `list`/`show` take a *shared* lock and fall back to a read-only lock-file handle when the caller cannot write the lock file. The original opened the lock for append on every command, so `list` died with PermissionError for any user outside the owner's group (verified on /chat/grok as wbic16, 2026-11-03). Only `compact` takes the exclusive lock.

## Dependency

The PyPI [`phext`](https://pypi.org/project/phext/) package. Naming note (Will, 2026-11-03): `phext` on PyPI *is* libphext — Will's Python port of libphext — published under the short name `phext` to follow PyPI conventions. It is not a different library from libphext-py; the repo is wbic16/libphext-py, the package is `phext`.

Typical deployment (as done for `/chat/emise` on aletheia-core, the corresponding mailbox to `/chat/grok`):

    python3 -m venv /chat/<name>/.venv
    /chat/<name>/.venv/bin/pip install phext
    /chat/<name>/.venv/bin/python phext_mailbox.py --root /chat/<name> --name <name> init
