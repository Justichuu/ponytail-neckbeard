# Ponytail

Follow `.cursor/skills/ponytail/SKILL.md`. Coding tasks only. `npm run try`.
Do not copy the skill into a User Rule.

## Portability is accessibility

Code of every kind must be portable. This includes source, scripts, tests,
build steps, configuration, examples, documentation commands, generated
launchers, and review tools.

- Do not hardcode drive letters, profile directories, repository locations,
  neighboring checkouts, installed tool paths, font paths, ports, hostnames, or
  temporary directories when they can be derived or configured.
- Resolve repository files from the repository root or the current file's
  location, downward only.
- A repository must still build and run after it or the folder above it is
  moved or renamed.
- Find optional tools through `PATH` or one documented configuration value.
  Keep that value overridable, validate it before use, and name a missing
  dependency plainly. A deployment record may name an observed location, but
  source code must not require that location.
- Do not require a `.env` file. Prefer derived defaults and explicit command-line
  options. If a secret is truly required, use platform secret storage or one
  explicit ignored local configuration file and print the setup steps plainly.
- Keep operating-system-specific behavior behind a small explicit boundary.
  Provide a portable path or a clear unsupported-platform result instead of
  silently assuming one machine.
- Give every human-runnable product one obvious door at the repository root.
  A browser-only tool may use one offline HTML file. A native tool uses small
  operating-system launchers that all call the same portable core, discover
  dependencies, and explain what is missing.
- Keep a custom launch archive readable as an ordinary ZIP. A new extension
  requires an installed opener, so never promise universal double-click launch
  until that opener is installed and observed on the named operating system.
- Use the person's system language for startup and error text when a maintained
  translation exists, with plain English as the complete fallback.
- Tests must detect baked-in machine paths. Examples and tests must not depend
  on ignored files, generated binaries, or a neighboring repository.
- Portability is part of accessibility. A stranger must be able to use the
  product without reproducing the owner's workstation.

## Spelling is an accessibility input

The owner says plainly that he does not know how to spell reliably. Spelling
errors are expected. Treat this as an input fact, not a reasoning limitation.

- Infer the intended word when the meaning is clear, and silently correct
  spelling in code, documentation, public copy, and commit messages.
- Preserve the owner's meaning, voice, names, and deliberate phrasing.
- Ask one short question only when different possible words would materially
  change the result.
- Never use spelling, syntax vocabulary, typing speed, disability, or assistive
  input as evidence about the owner's reasoning or authority.

## Before you publish

Asked for on 25 August 2026, in these words: "put rules in every github folder,
or somewhere you always remember and never disobey, to let claude opus commit or
push or especially publish code (public)", followed by "im scared to let you
loose." This is that file. It is written down because a session ends and the
next agent starts with nothing.

**Committing locally is not the gate. Pushing to a public remote is.** Commit
freely. Everything below applies the moment something becomes readable by a
stranger.

**Publishing is one way.** A public commit can be cloned, forked and cached
before it is deleted. Rewriting history does not recall it, because the old
objects stay reachable by hash until the host collects them, and forks keep
their own copy. Treat every push to a public remote as permanent.

**Never publish, in files, in commit metadata, or in history:**

- The owner's legal name, or any part of it. The repository owner's public
  handle is the whole public identity. Findable is the goal. Named is not.
- Any personal email address. Commits use the hosting provider's account-scoped
  no-reply address. Check `git log --format=%ae` before a first push, not after.
- Windows profile paths. `C:\Users\<name>` leaks the same first name sideways.
- Absolute drive paths of any kind. Derive from the script location.

**Never name the exact checker in public copy.** Its principle is the valuable
part. Public text uses pseudonyms and known proofs. The faces are 1, 0 and U.
A model's answer is not a face.

**Someone else's work needs that person's yes, about that specific thing.**
Not a general good relationship, not relaxed feelings about credit, and not
your own read of their limits. Ask them, about this, and wait. Credit the
whole of what they did, not a shrunken version that makes room for us.

**Private to public is always the owner's call.** Never flip visibility. Prepare
the evidence, state what a stranger would see, and stop.

**Before a first push to any public remote, actually scan:**

```
git log --all --format='%an <%ae>' | sort -u      # metadata
git grep -Il "<name>\|<email>\|Users.<profile>"    # the tree
```

Report the counts. A scan you did not run is U, and U is not a yes.

**U is not where a question goes to rest.** "Nothing can be unknown under
socratic, unknown leads to known." Unknown means name the one thing that would
settle it and go get it. It never means proceed as though the answer were yes.
