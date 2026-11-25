# DOM Clobbering Lab

An interactive, intentionally vulnerable web application designed to help security researchers and web penetration testers understand and exploit **DOM Clobbering** vulnerabilities through practical, hands-on challenges.

This lab demonstrates how attacker-controlled HTML elements can manipulate JavaScript global variables, interfere with application logic, bypass naive sanitization mechanisms, and potentially lead to Cross-Site Scripting (XSS).

No external dependencies, frameworks, or network access required.

## Overview

DOM Clobbering is a client-side injection technique in which HTML elements with specific `id` or `name` attributes interfere with JavaScript variables and DOM properties.

Instead of injecting JavaScript directly, an attacker manipulates the DOM using HTML elements to influence how the application's JavaScript behaves.

This lab provides a controlled environment to explore these behaviors from an attacker's perspective.

## Features

- 5 practical DOM Clobbering challenges.
- HTML-only payload injection.
- JavaScript global variable clobbering.
- HTMLCollection named property access.
- Form and anchor element manipulation.
- Stored DOM Clobbering scenarios.
- Sanitizer bypass techniques.
- XSS escalation through DOM manipulation.
- Built-in attacker-controlled data collector.
- Challenge verification and flag system.
- No external dependencies.

## Challenges

| # | Challenge | Difficulty | Key Concept |
|---|---|---|---|
| 01 | Debug Mode by Default | Easy | Global variable clobbering |
| 02 | Analytics Beacon | Easy | HTMLCollection and anchor coercion |
| 03 | Checkout Hijack | Medium | Document named properties and form manipulation |
| 04 | Stored Clobber Disables the Sanitizer | Hard | Stored DOM Clobbering and XSS |
| 05 | Unsigned Upload | Hard | Chained DOM Clobbering and security logic bypass |

## Getting Started

### Requirements

- Python 3.7 or higher
- Modern web browser
- No additional Python packages required

### Windows

Run:

```bash
run.bat
```

### Linux / macOS / WSL

```bash
python3 server.py
```

Alternatively:

```bash
./run.sh 8000
```

Open the application:

```text
http://127.0.0.1:8000/
```

## Attacker Inbox

The lab includes a built-in collector for observing attacker-controlled requests and collected data.

```text
http://127.0.0.1:8000/attacker.html
```

Available endpoints:

| Endpoint | Description |
|---|---|
| `POST /collect` | Receives attacker-controlled POST data |
| `GET /collect?...` | Receives GET requests and image beacons |
| `GET /collect.json` | Returns collected data in JSON format |
| `POST /reset` | Clears the collector log |

## Learning Objectives

By completing these challenges, you will understand:

- How HTML elements can create named properties on `window` and `document`.
- How `id` and `name` attributes can interfere with JavaScript globals.
- How HTMLCollection objects can be abused through named access.
- How DOM clobbering can affect application logic and security checks.
- How attacker-controlled DOM elements can influence URL and form properties.
- How stored HTML injection can interact with vulnerable sanitizers.
- How DOM Clobbering can contribute to XSS exploitation.

## Mitigation & Defense

To reduce the risk of DOM Clobbering:

- Avoid relying on implicit global variables.
- Use explicit DOM selectors such as `document.getElementById()`.
- Prefer module-scoped variables and constants.
- Validate expected object types and DOM ownership.
- Avoid inserting untrusted HTML using `innerHTML`.
- Use maintained sanitization libraries with DOM Clobbering protections.
- Apply strict Content Security Policy as an additional security layer.
- Include DOM Clobbering scenarios in security regression testing.

## Project Structure

```text
dom-clobbering-lab/
├── server.py
├── run.sh
├── run.bat
├── solutions.md
├── public/
│   ├── index.html
│   ├── lab1.html
│   ├── lab2.html
│   ├── lab3.html
│   ├── lab4.html
│   ├── lab5.html
│   ├── attacker.html
│   ├── css/
│   │   └── lab.css
│   └── js/
│       └── lab.js
```

## Disclaimer

This project is intentionally vulnerable and developed strictly for educational purposes and authorized security testing.

It is designed to run locally on `127.0.0.1` and should never be deployed to a public-facing environment.

Do not use these techniques against systems without explicit authorization.

## Author

**Mahan**

Web Application Penetration Tester | Application Security Researcher

- GitHub: [MahanXp](https://github.com/MhnXp)
- Medium: [MahanXp](https://medium.com/@MahanXp)

---

**If you find this project useful, consider giving it a ⭐**
