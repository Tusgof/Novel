# Agent Browser Policy

Tool-neutral browser rules for Yuehua Kit 4.0.4 onward (K-024). Choose a suitable available tool for the task; the kit requires no browser product and names no vendor default. The previous BrowserOS-specific policy is retired and archived under `Backup_/agent-browser/2026-11-03_agent-browser.md` in the kit repository.

## 1. Choose the surface

- Prefer a purpose-built API, connector, or CLI when it provides the required operation with clearer scope and evidence.
- Use a suitable available browser tool for interactive pages, browser-native behavior, human observation, or an authorized signed-in workflow. The project or work order may choose a tool; availability alone grants no account or action authority.
- Use Playwright or the project's declared hermetic browser tool for local UI tests, CI, clean-clone checks, and synthetic data. Keep persistent signed-in profiles separate from hermetic tests.
- Follow the active tool's instructions and schemas. Discover the actual product, version, connection, and endpoint at runtime; examples, prior ports, and installation paths are not configuration.

## 2. Authority and credentials

- External writes require authority stated in the active work order: posting, sending, submitting, purchasing, booking, deleting, publishing, changing account settings, and accepting terms are separate from reading or drafting.
- Logged-in browser state is credential-class access. Apply `AGENTS.md` resource-registry, provenance, vault, and approval rules before using it. Confirm the permitted unit, account owner, action scope, and any spend cap.
- Technical access is not authority. Full Access, an imported login, an open authenticated tab, or a successful connection does not expand the work order.
- Keep cookies, passwords, tokens, recovery codes, raw browser storage, and secret values out of inspection, exports, logs, prompts, and repositories. Use approved credential handling without extracting those values.
- Record identity, funds, subscriptions, and accounts with true provenance; never present one person's resources as another's.
- Prompt-skipping modes change interaction mechanics only. A signed-in profile or consequential action needs an explicit, bounded project decision before using such a mode; locked gates and final-confirmation requirements still apply.

## 3. Preflight

1. Read the active project rules, work order, and this policy. State why browser interaction is needed rather than an API or CLI.
2. Verify the actual tool, connection, and intended profile without inspecting secret material.
3. Record the allowed sites, accounts, actions, data classes, and forbidden external actions. Confirm resource-registry permission where credentials or paid services are involved.
4. Capture a read-only baseline: page identity, a safe account label, and the relevant external state.
5. Stop if identity, tenant, account, profile, authority, or data boundary is unclear.

## 4. Execute and verify

- Use the minimum tabs, permissions, and account access the task needs. Control and close only task-owned pages.
- Treat navigation, form filling, and submission as separate stages. A filled form is not permission to submit it; keep consequential actions behind any required final confirmation.
- Refresh page observations before acting and inspect the visible result after an action. A timeout is not evidence of failure or success; inspect before retrying to avoid duplicate external writes.
- Keep a single controller per tab or profile. For credentialed work, report a failed tool and follow an approved fallback or ask before changing the browser/profile authority boundary.
- Keep real account data, screenshots, downloads, recordings, replays, and browser history outside working repositories. Route vault-class material by pointer.
- If sensitive data appears in a repository or report, stop, preserve evidence safely, and use the EXPOSURE process.

## 5. Remote browser control

- Exposing a browser to another machine is a separate credential-bearing decision. Require an explicit work order naming the host, remote agent, permitted unit, profile, sites, actions, time window, and shutdown/revocation step.
- Register the browser-access and network/tunnel resources with their owners, permitted units, and any caps. Use a private tunnel or access-controlled private network by default; forward only the necessary active port.
- A public tunnel needs explicit owner approval for the exact task and a reason a private connection is insufficient. Require strong access protection; a public URL alone is not authentication.
- Treat active remote MCP/control URLs as credentials. Keep them out of repositories, logs, reports, prompts, and screenshots; report only the connection class.
- Keep exposure bounded and shut it down when the authorized task ends. If an endpoint leaks or remains reachable outside scope, stop, terminate exposure, preserve non-secret evidence, and report a credential incident.

## 6. OAuth and service integrations

- Register each service/account separately with its owner, permitted units, action scope, revocation path, and any spend cap. A shared browser connection does not merge service permissions.
- Obtain explicit approval for OAuth grants that create persistent access. Request minimum scopes and verify the provider's displayed account and tenant.
- Separate read, draft, and write authority for each service. Reading source control does not authorize merging; reading email does not authorize sending; reading payments does not authorize refunds or transfers.
- Keep returned personal, financial, legal, and account data within its vault boundary. Report granted action classes, actions performed, final state, and whether persistent OAuth access remains; revoke only as authorized.
- Managed OAuth storage is not a waiver of credential, provenance, vault, or approval rules.

## 7. Return evidence

Report the actual product/version, connection class, task scope, safe site/account labels, read actions, each write and its authorization, final observed state, uncertainty, and actions not run. Include fallback use and any sensitive artifacts' vault pointers.

A staged form is not submitted, a click is not a completed transaction, and a timeout is not a confirmed failure.

## 8. Adoption and changes

Record the chosen runtime tool and discovery/connection commands in the project's existing operating documentation without machine-specific paths or secret endpoints. Name the profile/account boundary, vault handling, and hermetic test surface separately.

Keep unit-specific decisions and record reversals as superseding entries. Units pinned to earlier kit versions migrate through their own approved changes; this policy does not edit other repositories, uninstall software, delete profiles, revoke account access, or remove MCP configuration.
