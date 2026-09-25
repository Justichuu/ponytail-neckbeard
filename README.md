# Ponytail, with spectacles

*He opens the page. He deletes 202 lines. It still works.*

You know the senior engineer. Long ponytail. Oval glasses. Has been at the
company longer than version control. You show him a date-picker library. He
points at the date picker already in the browser.

[Ponytail](https://github.com/DietrichGebert/ponytail) puts that engineer inside
your coding agent. This project keeps Ponytail's whole ladder and adds one rule
to the native-platform rung:

> Reading the source is not seeing the product.

If the work ends up in a browser, desktop app, game engine, or hardware, the
agent has to look on that same surface before it says the simple answer works.
Blind means stop. A glance at the top means stop. See the relevant path, then
ship the smallest thing that held.

This is not a second ladder and not a companion skill. It is Ponytail with the
spectacles on. Do not install both.

## Before and after

Someone asks for a date picker. The usual answer in
[`examples/overbuilt-picker.jsx`](examples/overbuilt-picker.jsx) is 202 lines:
a provider, a dependency, a wrapper, a second calendar, and range selection
"for later."

The browser's answer in [`examples/date.html`](examples/date.html) is four:

```html
<label>Date <input type="date" name="date"></label>
```

The original Ponytail ladder finds the native control. The spectacles stop the
agent from treating that discovery as proof. It opens the real surface, checks
the whole relevant path, and only then throws the other 202 lines away.

```text
request -> smallest answer -> real surface -> seen -> ship
                                      |-> blind -> stop
```

## The ladder

The first rung that holds wins:

1. Does this need to exist?
2. Is it already in the codebase?
3. Does the standard library do it?
4. Does the native platform do it? Put the spectacles on.
5. Does an installed dependency already do it?
6. Can it be one line?
7. Only then, write the minimum code that works.

The ladder runs after the agent understands the flow. Lazy about the solution,
never about reading. Validation, data-loss handling, security, accessibility,
and explicitly requested behavior stay.

## Try it

The walkthrough requires Node.js 18 or newer. There are no packages to install.

```sh
npm run try
```

On PowerShell systems that block `npm.ps1`, run `npm.cmd run try`.

The command walks through the date-picker decision and exercises each refusal.
It is not a browser report. Open [`examples/date.html`](examples/date.html) and
use the control to check the actual browser surface.

The canonical skill is
[`.cursor/skills/ponytail/SKILL.md`](.cursor/skills/ponytail/SKILL.md). Do not
paste a rewritten copy into a User Rule. The repository's Cursor rule points at
the skill so there is one source of truth.

## Check the repository

```sh
npm test
npm run verify
```

`npm test` checks this repository. `npm run verify` also checks alignment with
the original Ponytail. It reuses `PONYTAIL_DIR` or a sibling `../ponytail`
checkout; if neither exists, it makes a shallow network clone of the public
repository. That extra check needs Git, network access, and space for the
checkout. It does not install dependencies.

The moving parts are deliberately small:

| Path | Job |
| --- | --- |
| `.cursor/skills/ponytail/SKILL.md` | The rules the agent follows |
| `src/` | The refusal and observation state machines |
| `scripts/try.js` | The readable walkthrough |
| `examples/` | The 202-line trap and four-line survivor |
| `tests/` | The runnable checks |

## What it does not claim

It does not prove that every native control is good enough. That is why the
spectacles exist. It does not inherit Ponytail's benchmark numbers. It does not
apply to non-coding requests. It does not make an agent's confidence into
evidence.

[MIT](LICENSE). The shortest license that works.
