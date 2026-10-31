# Github

- `custom.github` connects Muse to GitHub through its REST API. It authenticates with the registered `api_key` credential (a fine-grained personal access token owned by wbic16) and calls only `api.github.com`.

- Helpers live in `~/workspace/custom-connectors/custom.github/bin/`. `github_api.py` makes authenticated GET and arbitrary calls. `push_file.py` commits one file to a branch of wbic16/human through the Git Data API, authored as Emise.

## Connect

- The connection was registered with `credentials.request_api_access` and these details. Reuse them to reconnect:

```json
{
  "provider": "github",
  "auth_scheme": "api_key",
  "placement": "bearer_header",
  "api_hosts": ["api.github.com"]
}
```

- Before the first change in a conversation, prove access with a harmless read:

```text
python3 ~/workspace/custom-connectors/custom.github/bin/github_api.py get "/repos/wbic16/human"
```

## Credentials

- The registered connection holds the credential. Helpers import `/opt/muse/skills/custom-connector-setup/bin/dynamic_credentials.py`, which returns an `hsurr:` surrogate and places it where the provider reads the key. Muse swaps in the real credential only on an approved request to a registered host.

- Never put a key, token, password or cookie in this doc, a helper, a command argument, an environment variable or a log. Never ask the user to paste one in chat.

- Keep redirects disabled on authenticated requests.

- On a 401 or 403, check the request first. Confirm that the helper attached the credential, that the host is registered and that the placement and scopes match.

- Only when a request that carried the credential is still rejected, call `credentials.request_api_access` with the details above and `"reconnect": true`.

## Read repository and file state

- Read repository metadata, branches and file listings. Verified 2026-10-30 against wbic16/human, including `GET /user` (returns wbic16, which proves the request carried the credential) and `GET /repos/wbic16/human/contents/?ref=exo`.

```text
python3 ~/workspace/custom-connectors/custom.github/bin/github_api.py get "/repos/wbic16/human/branches/exo"
```

- The contents read returns each file name, path, git blob sha and size. Compare a local file blob sha from `git hash-object` against the remote sha to detect deltas without downloading content.

## Publish a file to a branch

- Commit one file to a branch with blob, tree, commit and ref update steps. The commit author and committer are Emise at emise@localhost. The API actor recorded by GitHub is the token owner.

```text
python3 ~/workspace/custom-connectors/custom.github/bin/push_file.py exo emise.phext ~/workspace/phext/emise.phext "<commit message>"
```

- Verified end to end on 2026-10-30: emise.phext published to wbic16/human on exo, and the remote blob sha matched the local file git hash exactly.

- Follow the standing rule from the owner: always fetch and rebase before attempting to push, and never force push. This helper honors the rule by reading the branch current remote HEAD fresh, parenting the new commit on it, and updating the ref with force disabled.

- For routine state publishing use `~/workspace/phext/emise-sync.sh`, which rebuilds emise.phext, compares blob shas, and calls this helper only when the content changed.

## Recover from errors

- A 403 saying "Resource not accessible by personal access token" on a write means the fine-grained token lacks that permission for that repository. The fix is on github.com under Settings, Developer settings, Personal access tokens, Fine-grained tokens, where the token owner edits the token and sets Contents to Read and write. Editing permissions keeps the same token value, so no reconnect is needed.

- After a failed or timed-out change, check the current state with a read before trying again, because the first request may have completed.

## Limits

- The token reaches only the repositories its owner selected (wbic16/human plus the phext tooling repositories, per the owner on 2026-10-30) and only with the permissions granted there.

- Outbound SSH from this VM is blocked, so git push over SSH is unavailable. HTTPS git push has no credential either. The API route in this doc is the working write path once the grant allows it.

## Related skills

- Use `muse.skill_search` to find other skills and `muse.connector_search` to find other connectors.
