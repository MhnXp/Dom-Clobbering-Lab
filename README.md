# DOM Clobbering Lab

A tiny, dependency-free, intentionally vulnerable web app for practicing **DOM clobbering**
end to end: from a single global overwrite to stored clobbering that disables a sanitizer and
yields XSS.

Every challenge is HTML-only — you never get to inject `<script>`. That's the point.

## Quick start

**Windows:** double-click `run.bat` (starts the server in a second window and opens the browser).

**macOS / Linux / WSL:**

```bash
cd dom-clobbering-lab
python3 server.py          # or: ./run.sh 8000
```

Then open <http://127.0.0.1:8000/>.

Requirements: Python 3.7+. No pip packages, no build step, no network access needed.
On Windows, install Python from python.org and enable "Add python.exe to PATH".

## How a challenge works

Each lab page simulates a small "victim app" whose source you can read. You type HTML into the
payload box, it is rendered into the victim page (`#victim`), and the victim's JavaScript runs
against it.

- **Render & run app** — inject your HTML and execute the victim code.
- **Verify exploit** — the lab checks the observable side effect (a leaked value, a request that
  reached `/collect`, or an executed handler) and awards a flag.
- **Reset page** — clear the payload and per-lab state.
- **Attacker inbox** — <http://127.0.0.1:8000/attacker.html> shows everything that arrives at the
  attacker collector (`/collect`).

The server exposes a real collector:

| Endpoint | Purpose |
| --- | --- |
| `POST /collect` | attacker receiver (logs body) |
| `GET /collect?…` | same, for image beacons (logs query) |
| `GET /collect.json` | raw log as JSON |
| `POST /reset` | clear the log |

`solutions.md` contains full walkthroughs — try the labs first.

## Challenges

| # | Lab | Difficulty | Lesson |
| --- | --- | --- | --- |
| 1 | Debug mode by default | easy | a bare `window.X` lookup resolves to an injected element, breaking `===` checks |
| 2 | Analytics beacon | easy | `id` + `name` on a second element ⇒ `HTMLCollection` named access; anchor `toString()` is `href` |
| 3 | Checkout hijack | medium | `document.<name>` lookups and `form.action` let you reroute a POST |
| 4 | Stored clobber disables the sanitizer | hard | persisting a benign tag beats an allowlist sanitizer, then escalates to XSS |
| 5 | Capstone: unsigned upload | hard | chaining two clobbers to skip a signature check and move the destination |

## Layout

```
dom-clobbering-lab/
├── server.py            # static server + /collect collector (stdlib only)
├── run.sh
├── solutions.md
├── collect.log          # created at runtime
└── public/
    ├── index.html
    ├── lab1.html … lab5.html
    ├── attacker.html
    ├── css/lab.css
    └── js/lab.js        # shared logging / injection / verify helpers
```

## The vulnerability in one paragraph

An element with `id="x"` or `name="x"` becomes `window.x` and `document.x`. Multiple elements
with the same name produce an `HTMLCollection`, whose named children are reachable as
properties. Elements are objects, not strings, and their missing properties are `undefined`, so
code that does `window.cfg || {}` followed by `cfg.field` silently consumes attacker-controlled
DOM nodes. `HTMLAnchorElement.toString()` returns its `href`, so `<a>` is a universal
"attacker-controlled string" gadget when a DOM node is coerced. `HTMLFormElement` exposes its
controls by name, so `<form id=cfg><input name=url value=…>` clobbers `cfg.url`.

## Defending against it

1. Never trust bare global lookups. Use `document.getElementById(...)` / `querySelector`, and
   prefer module-scoped `const`/`let` (module scope does not create `window` properties).
2. Validate type and ownership: `Object.hasOwn(window, "cfg")` plus `typeof`/`instanceof`
   checks. Reject anything that is a DOM node when you expect a plain object or a string.
3. Prefer explicit storage (`Map`, closures, namespaced constants) over `window.*` globals.
4. Sanitize untrusted HTML with a maintained library (DOMPurify with its DOM-clobbering
   protections). Don't hand-roll regex sanitizers — this lab's sanitizer is deliberately naive.
5. Avoid `innerHTML` for user content; use `textContent` and DOM APIs.
6. Strict CSP does **not** stop DOM clobbering (no script is injected) — it only limits the
   follow-on escalation. Fix the lookups.
7. Regression test: inject `<a id="yourGlobalName"></a>` on pages that read that global and
   check the app still behaves.

## Disclaimer

This project is intentionally insecure and binds to `127.0.0.1` only. It exists for local,
educational use. Do not deploy it on a public host or reuse its "victim" code as-is.
