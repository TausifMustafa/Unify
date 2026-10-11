# UNIFY 2.0 — FINAL MASTER DEVELOPMENT HANDOFF

**Verified source baseline:** `Unify.zip` uploaded 2026-10-11. **Document revision:** 2026-10-11 (F1.1 implementation commit verified; documentation commit pending). **Canonical saved name:** `HANDOFF.md`. This document is intentionally self-contained: six feature-oriented stages, source audit, engineering standards, exact next action, and a living state ledger. No `AGENTS.md` or autonomous agents are part of this workflow.

> **Purpose:** Preserve everything a future developer/ChatGPT development conversation needs to continue transforming Unify from a university group project into a secure, tested, reliable, publicly deployed, interview-defensible portfolio application. Read this entire document once; subsequently use the quick-start, current-state ledger, and next-action section. This is both a **handoff** and a **feature-oriented execution guide**, not evidence that proposed work has already happened.
>
> **Audit status (2026-10-11):** The **new** `Unify.zip` is the authoritative reviewed snapshot and **does include a `.git` directory**. Its archived local branch is `main`, HEAD is `7411d451dec5c33413c1bbebb26b2b361863037d`, and its archived `origin/main` ref points at the same commit. The archive contains **one commit** (message: `moved from university GitLab to personal GitHub`), **72 Git-tracked files**, and no substantive changes from that commit: 67 text files differ solely by LF-versus-CRLF endings; 5 files match exactly. It also matches the earlier `Unify-main.zip` **file-for-file after newline normalization**. **This is archived Git metadata, not a fresh fetch of today's GitHub remote and not confirmation of the user's current working-directory status.** Application feature implementation in this planning process: **none**. Backend Python syntax check passed; application runtime and integration tests were not executed. Do not invent a deployed URL or test results. **No `AGENTS.md`; no agents.**

> **LIVE DEVELOPMENT UPDATE — 2026-10-11 (supersedes archived-only/current-state claims below):** The user verified their Windows clone `C:\Users\tausi\Projects\Unify` on a clean `main`, fetched `origin`, and confirmed both point at `7411d45` (`git rev-list --left-right --count main...origin/main` returned `0 0`). They created `fix/registration-role-escalation` at the same commit. **F1.1 was regression-tested and committed locally as `9239fda` (`fix(auth): prevent public registration of privileged roles`) on `fix/registration-role-escalation`. It has NOT yet been pushed, PR-reviewed, or merged.** Both forged `admin` and `organizer` registration were source-confirmed and API-reproduced as HTTP 201 before the fix; the revised code returns HTTP 422 for each in the running isolated test API. Four Pytest/PostgreSQL integration cases pass; valid student registration + login + `/api/auth/me` also passed manually. Frontend `npx.cmd tsc --noEmit` and `npm.cmd run build` passed; ESLint has 12 pre-existing errors and 2 warnings, and npm audit reported 26 dependency vulnerabilities (1 critical, 21 high, 3 moderate, 1 low). **The master handoff now exists as an untracked `HANDOFF.md` in the user's local repository (`?? HANDOFF.md`). The document needs this commit-state update, review, and its own documentation commit before pushing.** See Sections 8–9 for precise evidence, commands and next actions. The 2026-10-11 ZIP-audit notes below remain historical statements about the original snapshot, not current implementation claims.

---

## 0. READ THIS FIRST — 60-second successor briefing

**The product:** Unify is a campus event discovery and management application. Students discover events and RSVP; organizers create/manage events and notify attendees; administrators are intended to oversee privileged functions. The current source uses **Next.js 16 / React 19 / TypeScript / Tailwind CSS / Radix-style components**, **Python 3.11 / FastAPI / SQLAlchemy / Pydantic**, **PostgreSQL 16**, and **Docker Compose**.

**The mission:** Do not merely add features. Make the software **secure, transaction-safe, maintainable, tested, operationally observable, deployable, and demonstrable**. Preserve the good parts of the university application. Prioritize engineering evidence that would withstand technical interviews for full-stack, backend, security, testing, and DevOps internships.

**Highest-risk source findings (fix before broad feature work):**

1. `backend/app/routers/auth.py`: registration accepts client-controlled `role` and persists it; an attacker can submit `"role": "admin"` to self-assign privilege.
2. `backend/app/routers/events.py`: `GET /api/events/{event_id}` does not enforce `is_public`; private event details can be fetched by ID.
3. `backend/app/routers/rsvps.py`: ordinary users can submit `checked_in`; attendance must be organizer/admin controlled. RSVP access to private events also requires scrutiny.
4. Database SQL/ORM disagreement: `event_tags.id` UUID in SQL vs integer in ORM; `organizations.owner_user_id` vs `owner_id`; organization description only in ORM; `user_settings` only in ORM; `rsvps.note` only in SQL; timestamp and type differences. The backend additionally runs `Base.metadata.create_all()` at import/startup. **Do not trust `create_all()` to migrate an existing database.**
5. RSVP capacity counts `waitlisted` users as occupied seats and uses unprotected count-then-write logic; the SQL trigger has different status semantics. Concurrency correctness is not established.
6. No committed automated tests, GitHub Actions or Alembic migrations found in the uploaded ZIP. Python source **syntax compilation passed** on the current extracted snapshot, but no end-to-end runtime, clean Docker startup, frontend build, PostgreSQL integration test, or public deployment was verified.
7. **Newly emphasized in this audit:** public `GET /api/rsvps/event/{event_id}/count` has **no authentication or `is_public` check**; organizer event creation/update accepts `organization_id` without demonstrated organization-ownership/membership authorization; event creation **commits the event before its tags**, permitting partial persistence if a later tag write fails.
8. **SQL trigger-specific flaw:** `prevent_over_capacity()` adds one to the count only on INSERT, but a status UPDATE from `waitlisted` or `cancelled` to `rsvped`/`checked_in` also consumes a new seat. On UPDATE it counts the old, non-confirmed row without adding the pending confirmed seat; together with no shared event-row lock, the database trigger does **not** establish the no-overbooking invariant. The SQL attendance view also wrongly counts waitlisted users as booked.

**Immediate next work (updated 2026-10-11):** The **F1.1 security commit `9239fda` is complete locally** on `fix/registration-role-escalation`. Update the existing untracked repository-root `HANDOFF.md` to this revision, stage/review it and make a **separate documentation commit**; then push the branch, prepare a focused PR, and review available checks/manual verification before merge. The security regression tests and real HTTP requests have passed on the feature branch; this is **not yet a merged fix**. Then tackle private-event visibility and unauthorized check-in as separate features; do **not** bundle them into F1.1.

**Source-of-truth order:** (1) live repository and observed test/runtime behavior (after checking working-tree status and remote), (2) current `HANDOFF.md` and committed documentation, (3) `docs/ROADMAP.md` / `Unify_2_0_Master_Engineering_Roadmap.md` as strategy, (4) 11-page `Unify Project Improvements.pdf` as an additional source, (5) prior conversational suggestions. If sources conflict, investigate; don't silently assume a feature exists because this document proposes it.

---

## 1. Decisions already made, things deliberately NOT decided

### Agreed direction

- **Keep the current full-stack technology family.** Evolve Next.js/React/TypeScript, FastAPI/SQLAlchemy/Pydantic, PostgreSQL, and Docker instead of rewriting them to Java/Node or introducing unrelated technology for résumé keywords.
- Use a **modular monolith**, with clear backend API/router, schema/validation, service/business-rule, and persistence responsibilities. Do not add microservices or Kubernetes without a demonstrated need.
- Prefer security, correctness, clarity, testability, and product value over maximal feature count.
- Work **one small behavior or bug fix at a time**. Explain design/purpose/trade-offs *before* major code changes. Preserve working behavior and avoid unapproved refactors.
- Use **`main` as the stable integration branch** once repository state verifies it, and **one short-lived feature/fix branch per change**, typically merged through a documented PR after relevant tests pass. No heavy GitFlow or permanent `develop` branch.
- Build tests as defects are addressed, **even though the formal test/CI stage appears third**. Likewise, write documentation and collect portfolio evidence throughout, not just at the end.
- Maintain **honest attribution**: the app originated as a university group project. Clearly distinguish the team's original work from personally completed Unify 2.0 improvements.
- Use a real event/waitlist product story to justify infrastructure; don't add Redis, Celery, a cloud service, Power BI, or AI simply for a tool list.
- The user explicitly wants **feature-oriented stages**, not day-by-day schedules. Do not reorganize this handoff into “day 1/day 2.”
- The user wants mentorship: explain transaction isolation, RBAC vs resource ownership, migrations, CSRF, testing, idempotency, observability, and alternative designs in a way they could explain in interviews.
- **No AGENTS-based workflow**. This handoff, the roadmap, actual code, PRs, and direct mentorship are sufficient.

### Architectural decisions that are still PROPOSALS, not commitments

Each must be evaluated against the real code and recorded as a short ADR/decision note **before implementation**:

| Question | Recommended starting position | Why / caveat |
|---|---|---|
| Authentication/session | Short-lived access token plus revocable/rotating refresh token, ideally refresh cookie `Secure` + `HttpOnly` with same-origin routing; or secure server-managed sessions | Avoid persistent privileged tokens in `localStorage`; cookies introduce CSRF and deployment implications. Decide via threat model. |
| Organizer onboarding | New public registrations are **student-only**; organizers require admin approval or invitation | Close privilege escalation first; safely bootstrap initial admin without public admin sign-up. |
| Authorization | Centralized FastAPI dependencies + server-side event ownership/organization scope | Frontend guards improve UX but are not security boundaries. |
| Private event policy | Not publicly listable/readable/RSVP-able; organizer/admin and explicitly authorized attendees/invitees as later defined | Choose 404 vs 403 consistently to avoid information disclosure. Don't accidentally break legitimate private-event access. |
| Database schema | SQLAlchemy models + explicit Alembic migrations for all real structural changes, with disciplined PostgreSQL-specific code where necessary | Autogenerated migrations must be reviewed; preserve existing data. |
| Capacity locking | PostgreSQL transaction with `SELECT ... FOR UPDATE` on the **event row**, consistent lock ordering, unique RSVP constraints, and explicit state transitions | Counting alone is not concurrency-safe. Race conditions must be tested on PostgreSQL. |
| Waitlist order | FIFO by stable queued timestamp + ID tie-breaker, unless product rules justify priority | Deterministic promotion under cancellation; enforce in transaction. |
| Background work | Start with in-app notifications; add durable worker/outbox/queue when scheduled and external delivery require retries | An in-process FastAPI task is not a substitute for durable scheduling/retries. |
| Analytics | Database-driven organizer/admin dashboards inside Unify | Power BI remains optional since another project focuses on analytics. |
| Applied AI | At most one optional natural-language-to-authorized-event-search feature after core correctness | No hallucinated results or private data leakage; cost/fallback controls. |
| Public hosting | One manageable HTTPS deployment stack with persistent managed PostgreSQL | Prefer learning a credible deployment/runbook over premature infrastructure complexity. |

---

## 2. Current baseline: what the uploaded source actually contains

### 2.1 Baseline provenance and verification boundaries

- **New canonical frozen source:** `Unify.zip`, archive root `Unify/`, which **does contain `.git` metadata**. Its `main` points at commit `7411d451dec5c33413c1bbebb26b2b361863037d`; archived `origin/main` points to the same commit. This snapshot contains one commit, 72 tracked source files, and the remote configuration references the personal GitHub repository. It does **not** establish live GitHub state at handoff time; confirm with `git fetch` in the user's actual clone when permitted and appropriate.
- **Cross-snapshot verification:** The previous `Unify-main.zip` (archive root `Unify-main/`, no `.git`) and new `Unify.zip` have the **same 72 non-`.git` files** with **zero content differences after CRLF normalization**. Thus source-code findings from the previous audit are still applicable to this new baseline.
- **Important Git/line-ending anomaly in the NEW ZIP:** `git status --short --branch` reports `main...origin/main` and **67 modified tracked text files** in this extracted snapshot. A byte-for-byte comparison of each file to the corresponding `HEAD` Git blob finds **67 CRLF-only differences, 5 exact matches and 0 substantive differences**; `git diff -w --exit-code` also succeeds. **Do not run `git add .` or commit these 67 mass line-ending changes as a feature.** Verify `.gitattributes`, editor settings and `core.autocrlf` in the real clone; if real semantic changes exist there, preserve them. Avoid blindly running `git reset --hard` to fix the export artifact. If desired, agree on a focused normalization policy in a separate reviewed change.
- Prior strategy: `Unify_2_0_Master_Engineering_Roadmap.md`, prepared in this planning conversation; place a reviewed copy under `docs/ROADMAP.md` in Git.
- Additional source: `Unify Project Improvements.pdf` (11 pages), which includes employer-focused priorities, code audit, concurrency diagram, test recommendations, deployment advice, AI caveats, and contribution/measurement cautions.
- Backend Python syntax compilation (`python -m compileall -q backend/app`) **passed on the newly extracted `Unify.zip` snapshot during this final audit**. This establishes only parse/compile validity, not server startup, imports, DB compatibility, security, or runtime correctness.
- No application runtime, Docker Compose stack startup, migration upgrade, frontend dependency installation/build, automated API test, UI end-to-end test, performance claim, or live URL was validated in this audit. Docker CLI was unavailable in the audit environment; critical Python runtime modules `psycopg`, `jose` and `passlib` were not installed here, so a FastAPI/PostgreSQL launch was not attempted. The frontend package has no installed `node_modules` in this ZIP. **Environment limitations are not proof the repository is broken.**
- The new snapshot contains **no committed automated test files, no `.github/workflows`**, and no Alembic migration tree. Verified package root is `frontend/513-app` with Next `16.0.1`, React `19.2.0`, Tailwind `4` and TypeScript `^5`; backend runs Python `3.11` in its Dockerfile with FastAPI/SQLAlchemy/PostgreSQL driver dependencies (most unpinned). No CI build was run.
- **Scope of audit:** inspected complete repository file inventory, git/tree comparison, FastAPI routers/config/models/schemas, SQL schema/seed/trigger, frontend authentication, event/organizer/RSVP/notifications/settings flows and components, Docker and package setup. This is an end-to-end **source** review, not a claim that user-facing behavior passes at runtime.

### 2.2 Current architecture and repository map

```text
Unify/
├── .git/                               # PRESENT in new ZIP; one-commit Git snapshot
├── .gitignore
├── README.md                           # Currently one-line product description in ZIP
├── docker-compose.yml                  # db, backend, frontend; dev-oriented
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── database_schema1.sql            # Handwritten SQL with schema, triggers, view
│   ├── database_seed2.sql              # Demo SQL seed
│   └── app/
│       ├── main.py                     # FastAPI app, CORS, routers, create_all()
│       ├── config.py                   # DATABASE_URL settings
│       ├── database.py                 # Engine, SessionLocal, Base, get_db
│       ├── models.py                   # ORM models/enums
│       ├── schemas.py                  # Pydantic API schemas
│       ├── events.py                   # Older/stale events logic; inspect before removing
│       └── routers/
│           ├── auth.py                 # Register, login, JWT, current_user
│           ├── events.py               # Public event list/detail
│           ├── organizer.py            # Organizer CRUD + 'send-push' mock
│           ├── rsvps.py                # RSVP create/update/delete/list/count
│           ├── notifications.py        # Notification read/mark read
│           └── users.py                # Profile, settings, password change
└── frontend/
    ├── package-lock.json              # Check if stale/redundant
    └── 513-app/
        ├── package.json                # Actual npm package root
        ├── package-lock.json
        ├── Dockerfile
        ├── next.config.ts
        ├── app/
        │   ├── (public)/auth/page.tsx  # Login/register UI
        │   ├── (auth)/events/           # Student discovery/details
        │   ├── (auth)/organizer/        # Organizer dashboard/create/edit
        │   ├── (auth)/notifications/
        │   ├── (auth)/settings/
        │   ├── (auth)/calendar/page.tsx # Placeholder
        │   ├── (auth)/rsvp/page.tsx     # Placeholder
        │   └── ...                     # Landing, layouts, errors
        ├── lib/apiClient.ts            # Fetch wrapper, localStorage bearer token
        ├── components/                 # Navbar, theme, UI components
        └── public/                     # Static assets
```

**Current request path:** Browser Next.js page -> `lib/apiClient.ts` -> HTTP REST endpoint + bearer JWT -> FastAPI router + `get_current_user` dependency where used -> SQLAlchemy Session -> PostgreSQL -> Pydantic response -> React UI. `apiClient.ts` persists `unify_token` in `localStorage` and falls back to `http://localhost:8000` if `NEXT_PUBLIC_API_BASE_URL` is unset.

**Current Compose services:** `postgres:16-alpine`, backend Uvicorn on host port 8000, Next.js on 3000, DB host port 5433 -> container 5432; Postgres persistent named volume `db_data`. SQL schema/seed mounts execute on the **first initialization of a fresh volume**, not every startup. Compose has development DB credentials and `JWT_SECRET=dev-secret-change-me`; do not deploy this configuration as-is. Backend currently uses a hard-coded localhost CORS allowlist. `NEXT_PUBLIC_*` frontend environment configuration requires special care because public variables are typically bundled at **build time**, not safely changed by runtime Compose environment alone.

### 2.3 Current domain model (as modeled, not guaranteed consistent with SQL)

- `User`: UUID, email, names, username, bio/avatar, role (`student` / `organizer` / `admin`), password hash, timestamps; owns events, RSVP records, notifications, settings, and organizations.
- `UserSettings`: one per user; theme, email/push preferences, timestamps. **ORM table not present in handwritten SQL schema.**
- `Organization`: UUID, name, description, owner FK, events. **Owner field mismatch with SQL**; description exists in ORM but not original SQL.
- `Event`: UUID, organizer and optional organization, title/description/location, start/end, optional capacity, `is_public`, timestamps, tags and RSVPs. Draft/published/cancelled lifecycle is **not yet modeled**.
- `EventTag`: links event and tag string; **ORM declares integer PK with inconsistent UUID typing, while SQL declares UUID PK**. SQL additionally has a `tags` table not represented by the ORM's event-tag association pattern.
- `RSVP`: UUID, user+event unique constraint, status (`rsvped`, `waitlisted`, `cancelled`, `checked_in`), timestamps. `note` appears only in SQL.
- `Notification`: persisted in-app record; type (`reminder`, `update`, `rsvp`, `system`), user, optional event, read state, timestamps.
- SQL also defines timestamp triggers, an `event_attendance` view, and a capacity trigger; review carefully before replacing, altering, or relying on them.

### 2.4 Existing API endpoints in the uploaded snapshot

```text
GET    /health
POST   /api/auth/register
POST   /api/auth/login
GET    /api/auth/me
GET    /api/events/
GET    /api/events/{event_id}
GET    /api/organizer/events
GET    /api/organizer/events/{event_id}
POST   /api/organizer/events
PUT    /api/organizer/events/{event_id}
POST   /api/organizer/events/{event_id}/send-push  # in-app record creation only
GET    /api/rsvps/me
GET    /api/rsvps/me/map
GET    /api/rsvps/me/{event_id}
POST   /api/rsvps
PUT    /api/rsvps/me/{event_id}
DELETE /api/rsvps/me/{event_id}
GET    /api/rsvps/event/{event_id}/count
GET    /api/notifications/me
POST   /api/notifications/me/mark-all-read
PATCH  /api/notifications/{notification_id}
GET    /api/users/me
PATCH  /api/users/me/settings
PATCH  /api/users/me
POST   /api/users/me/change-password
```

**Do not assume** current API behavior matches its endpoint name. In particular, “send-push” creates in-app notifications, not browser push or email. Some public event responses manually omit optional fields, including `capacity` on event detail, despite Pydantic's schema listing them; UI can consequently show “Unlimited” for a capacity-limited event.

### 2.5 Known gaps and defects to revisit

| Area | Last-reviewed finding | Severity / appropriate stage |
|---|---|---|
| Registration role | Request-controlled role is saved; admin self-registration possible | **Critical — First** |
| Private event detail | Public detail route ignores `is_public` | **Critical — First** |
| RSVP privilege | Student can request `checked_in`; no proper RSVP state authorization | **Critical — First/Second** |
| RSVP capacity/concurrency | `waitlisted` treated as booked in Python; SQL trigger differs; count/write races; UPDATE transition undercount in trigger | **Critical correctness — Second** |
| Schema drift | EventTag UUID/integer; org ownership/description; UserSettings, RSVP.note; timestamps | **High — First** |
| Private RSVP-count disclosure | Unauthenticated event-level count discloses counts/capacity even for private events | **High privacy — First** |
| Organization association authorization | Organizer create/update accepts arbitrary organization ID without membership/ownership validation | **High authorization — First/Fourth** |
| Partial event creation | Event INSERT commits before tag insert; later tag failure can leave a half-created event | **High integrity — First/Fourth** |
| `create_all` | Executed on app import, no controlled migrations | **High — First** |
| Event response | Public detail omits `capacity` and `organization_id` | Fourth (possibly earlier small fix) |
| Access-control UI | Organizer frontend guard excludes admin whereas backend sometimes allows admin | First/Fourth |
| Organizer registration | Self-service organizer selected in UI and accepted in API | First |
| Token storage | 24-hour access JWT in `localStorage`, no refresh/revocation | First security-hardening work |
| Auth hardening | No verification/reset, server-side password policy, login throttling | First / selected P2 |
| Event state | Draft actions represented in UI without matching backend lifecycle | Fourth |
| Calendar / RSVP pages | Literal placeholders | Fourth |
| Organizer analytics | Dashboard includes field assumptions not backed by actual fetched counts | Fourth/Sixth |
| Notifications | In-app records, not true push/email, no reliable scheduling/retries | Fourth/Fifth |
| Settings | Some theme/preferences/profile fields disconnected or disabled | Fourth |
| API typing/error handling | Handwritten TypeScript interfaces and response-shape drift | Fourth |
| Docker | Hardcoded development credentials/secret, published DB port, missing health/readiness checks | Fifth (secrets immediately before remote sharing) |
| CI/test suite | Absent in uploaded snapshot | Third, with P0 regression tests immediately |
| Git archive false modifications | Archived checkout reports 67 modified text files caused ONLY by LF→CRLF export conversion; no code differences from HEAD | **First baseline hygiene** |
| Git history provenance | Archived personal-GitHub migration snapshot contains one commit, not the university GitLab history | **First/Sixth attribution & provenance** |
| Docs | Root README essentially one sentence; frontend README default | Ongoing/Sixth |
| Stale files | `backend/app/events.py`, empty/stale outer lockfiles, repeated dependencies | Cleanup only with test/review and no unrelated refactor |

### 2.6 Additional source-confirmed findings and corrections from the new ZIP

| Area and exact source | What source proves | Follow-up verification/action |
|---|---|---|
| **Authentication** — `backend/app/routers/auth.py`: `RegisterRequest.role` and `role=payload.role` | Public caller can request `admin` or `organizer`; 24-hour bearer JWT uses a development fallback secret when unset | Test direct malicious requests, enforce student-only public signup, fail safely in deployment when secret missing |
| **Frontend registration** — `frontend/513-app/app/(public)/auth/page.tsx` | Student/organizer selector is sent to public registration API; UI alone cannot restrict privileges | Update UX to student signup and separate organizer request/approval path when designed |
| **Private event** — `backend/app/routers/events.py` | Public listing checks `is_public`; detail by ID does not | Add visibility/ownership policy and negative API tests |
| **Private count** — `backend/app/routers/rsvps.py` | `GET /api/rsvps/event/{event_id}/count` has no `get_current_user` dependency and no visibility restriction | Decide public safe aggregate policy vs private denial; test information disclosure |
| **RSVP write** — `backend/app/routers/rsvps.py`, `backend/app/schemas.py` | `RSVPCreate`/`RSVPUpdate` allow arbitrary status, including `checked_in`; neither RSVP write checks event visibility or end-time | Remove client authority over state; enforce lifecycle and permission tests |
| **Database trigger** — `backend/database_schema1.sql` | INSERT adds pending seat in `prevent_over_capacity()`, UPDATE of non-confirmed→confirmed does not; no per-event locking | Fix or replace in migration coordinated with transaction-safe RSVP service; test transition and parallel requests |
| **SQL attendance view** — `backend/database_schema1.sql` | `event_attendance.total_booked` includes `waitlisted` | Align with confirmed-seat semantics; make analytics denominators explicit |
| **Organizer association** — `backend/app/routers/organizer.py` | `organization_id` from organizer payload is stored without checking that user can represent the organization | Reject unauthorized org IDs or define organization membership policy; test cross-organization abuse |
| **Non-atomic event+tags** — `backend/app/routers/organizer.py` | `create_event()` commits event before creating/committing tags | One transaction; roll back both on invalid/duplicate tags; add tests |
| **Misleading demo accounts** — `backend/database_seed2.sql` | Seeded student/organizer/admin all have NULL password hashes, so these are not usable password-login accounts | Document as data-only fixtures; create safe seeded demo login accounts only after explicit policy, no default public admin credentials |
| **Stale event module** — `backend/app/events.py` | Not registered by `app/main.py`; references `from ..database` despite living at `app/events.py` (a problematic import if loaded as `app.events`) | Confirm unused, then remove/fix in separate cleanup PR with checks |
| **Frontend/API contract** — `backend/app/routers/events.py` and `frontend/513-app/app/(auth)/events/[id]/page.tsx` | Public event detail manually omits capacity and organization; UI displays `Unlimited` for omitted capacity | Add response-contract regression test and render verified capacity |
| **Role guard** — `frontend/513-app/app/(auth)/organizer/layout.tsx` | Client layout redirects `admin` despite some backend organizer routes permitting admin | Align a documented admin policy with backend and UX |
| **Configuration** — `docker-compose.yml`, `frontend/513-app/lib/apiClient.ts`, frontend Dockerfile | Docker passes `NEXT_PUBLIC_API_BASE_URL` at runtime but static client bundle defaults to localhost if not set when built | Design build-time or same-origin configuration before deployment; test in deployed browser |
| **Dependencies and documentation** — `backend/requirements.txt`, READMEs, package-lock hierarchy | Duplicate `email-validator`; many unpinned Python dependencies; root README minimal, frontend README template, backend README refers to stale `db/init` path | Focused dependency/docs cleanup; do not bundle with security fixes |

**Additional nuance:** `UserSettings` is absent from handwritten SQL **but could be created by SQLAlchemy `create_all()` at app startup**; that does **not** make the bootstrap/migration arrangement safe. Likewise, the SQL/ORM mismatch alone does not prove any specific endpoint currently crashes: reproduce runtime failures before describing them as observed. No evidence in this ZIP establishes a public deployment or CI execution.

**Security triage ordering:** Fix role escalation, private-event visibility and unauthorized RSVP state changes in focused changes; include unauthorized private counts and cross-organization association in the Stage 1 authorization review. The RSVP trigger and atomic organizer writes get dedicated regression tests as the database workflow is repaired.

**Additional SQL pitfall to inspect:** `backend/database_schema1.sql` contains `DROP TABLE IF EXISTS event_tags`, and the seed's event inserts use generated IDs, so do not assume re-running the original SQL scripts is idempotent or safe on valuable data. The RSVP trigger must be reviewed for insert/update counting and concurrent transaction correctness. Never run destructive reset commands against a valuable volume.

---

## 3. The six feature-oriented stages — canonical execution order

**Do not interpret a stage as one branch, one PR, or a fixed number of days.** Each stage contains smaller, independently reviewable features. Urgent tests, security fixes, and documentation cross boundaries. **Stages 1–5 form the primary portfolio release**; Stage 6 enhances it and packages the final demonstration. If application deadlines arrive sooner, ship an honestly labeled, working subset rather than unfinished stretch work.

### FIRST — SECURITY AND DATABASE CORRECTNESS

**Outcome:** The existing app no longer has obvious privilege/access-control failures, its schemas align, authentication is defensible, and a fresh or existing database can be managed predictably.

#### F1.0 — Establish the real baseline and safe Git workflow

**Why:** The new ZIP contains `.git` and matches its archived HEAD semantically, but a ZIP is not a fresh checkout or confirmation of live GitHub state. We need a verified starting point before changing or declaring anything complete.

**Steps**

1. Ask user to open the *actual* local Git clone (or help create one). **Known ZIP evidence:** `main` at `7411d45` with archived `origin/main` at the same commit; `.git` exists in the new ZIP; no additional commit history was preserved. Run `git status --short --branch`, `git branch --show-current`, `git log -1 --oneline`, `git remote -v`, and inspect local/remote branches; `git fetch origin` only when remote access is configured/appropriate. Record live state separately from archived Git metadata.
2. Check whether `main` is actually stable, whether there are uncommitted changes, and whether the source matches this snapshot. **Critical:** extracted `Unify.zip` shows 67 files modified solely because of CRLF conversion. Confirm whether any `git diff` changes are semantic *before* staging or cleaning; set a consistent line-ending policy deliberately. **Never** `git reset --hard` or bulk-commit 67 false changes without user's explicit approval. Do not overwrite user work, force-push, or assume a clean worktree.
3. Preserve baseline and original university contributions: the archived Git history contains a single migration commit (`moved from university GitLab to personal GitHub`). **Do not claim this one-commit personal repository proves who authored the earlier group work.** Consider preserving original university provenance separately if available/appropriate. Use a short-lived branch only after confirming stable `main` and remote tracking.
4. Capture dependency/runtime versions; validate `docker compose config` without exposing secrets. Use a disposable development DB/volume for initial experiments; back up valuable data.
5. Record actual results of `python -m compileall -q backend/app`, frontend `npm ci`, `npm run lint`, `npx tsc --noEmit`, `npm run build`, and Docker/API smoke checks **as attempted**. If a step is blocked, record the exact blocker; do not infer it passed.
6. Bring the roadmap and this handoff into the repository; add `.env.example` with **placeholders only**, a minimal setup guide, and `docs/decisions/` when decisions arise. Do not create `AGENTS.md`.

**Done when:** A successor knows what commit/branch is active, which baseline commands passed/failed, which DB is safe to use, and how to reproduce the environment. Documentation changes are focused and reviewed.

#### F1.1 — Eliminate role self-escalation (the FIRST actual code feature)

**Observed issue:** `RegisterRequest.role` accepts a `UserRole`; `register_user` saves `role=payload.role`. A caller can send `admin` or `organizer` regardless of the frontend choice.

**Implementation sequence**

1. Decide and document the API behavior for privileged `role` input: preferably **reject elevated role requests with 422/400** (or ignore and always assign `student`, if clearly documented). In either case, **server-created role must be student**. Do not rely on hiding the dropdown.
2. Write a failing API regression test that submits `role=admin` and `role=organizer` and checks no privileged user is created; also test normal student registration. Use a disposable/test DB and properly isolated fixtures.
3. Make the smallest server-side change in `backend/app/routers/auth.py` and, if necessary, `backend/app/schemas.py` and relevant UI (`app/(public)/auth/page.tsx`). Keep backward-compatibility and error messaging in mind.
4. Consider duplicate email conflict, normalized email, password policy boundaries, and race-safe uniqueness; do not silently create privileged seed/demo credentials.
5. Re-run focused tests and verify `GET /api/auth/me` confirms student role for a valid registered user. Review and PR independently.

**Done when:** Direct API requests cannot create organizer/admin accounts, and tests prove both the attempted exploit is blocked and ordinary signup still works.

#### F1.2 — Protect private-event information and RSVP access

1. Define the visibility matrix: public event lists/details; private-event owner/admin access; later an explicit invitation/participant policy if needed. Do not invent invite semantics without approval.
2. Enforce access in **every applicable backend endpoint**, not only page redirects. Inspect `/api/events/{id}`, `/api/rsvps`, `/api/rsvps/event/{id}/count`, organizer detail, notification/event association, and any future attendee endpoint for existence or data leaks.
3. Choose 404 vs 403 deliberately; test anonymous, student, event owner, other organizer, and admin behavior. **Explicitly test the currently unauthenticated `/api/rsvps/event/{event_id}/count` route** for private-event leaks.
4. Add privacy regression tests for known and guessed IDs; verify authorized owners can still access their events.

**Done when:** No unauthorized user can read private-event details or learn protected data through adjacent RSVP/count endpoints, while legitimate access works.

#### F1.3 — Remove self-check-in / make role ownership checks consistent

1. Restrict public RSVP requests to student-allowed actions (register, join waitlist automatically, cancel as applicable). Ordinary users must not set arbitrary server-controlled statuses.
2. Create or plan a separate organizer-authorized check-in endpoint (full check-in workflow is completed in Stage 2); enforce event ownership or explicit admin authority.
3. Normalize organizer/admin UI guards with **actual server policy** rather than duplicating inconsistent rules.
4. Test student self-check-in denial, cross-organizer check-in denial, valid organizer check-in (when implemented), and admin exceptions if policy allows. **Disallow arbitrary `checked_in`, `waitlisted`, and privileged state transitions through direct client-supplied `status`.**

**Done when:** A student cannot become `checked_in` by manipulating API payloads and server permission checks cover each write path.

#### F1.4 — Reconcile every database table, enum, trigger, view, and ORM model

1. Make a **side-by-side schema inventory** of `database_schema1.sql` and `app/models.py`, including data types, nullability, defaults, indexes, FK cascade behavior, constraints, enums, triggers, views, and ORM relationships.
2. Explicitly decide UUID vs integer `EventTag.id` (UUID is a natural choice if preserving existing SQL data), `owner_user_id` vs `owner_id`, organization description, user settings, RSVP note, `tags` relation, and timezone-aware timestamps.
3. Review PostgreSQL `CITEXT` vs ORM `String`, case-insensitive identities, server/Python defaults, enum evolution, `updated_at` triggers, existing PK/FK data, and the legacy `event_attendance` view.
4. Add constraints for `starts_at < ends_at`, nonnegative or positive capacity as product semantics require, unique user-event RSVP, valid transitions where appropriate, and helpful indexes. **Review/repair the existing trigger UPDATE-count defect** and the `event_attendance` view's inclusion of waitlisted users. Don't optimize speculatively.
5. Document the chosen canonical schema and risks in an ADR; don't rely blindly on Alembic autogeneration.

**Done when:** Every discrepancy has a documented resolution and an explicit migration strategy. No silent data loss.

#### F1.5 — Add Alembic with fresh-db AND existing-db upgrade paths

1. Introduce Alembic configuration and versioned migration scripts. Define one canonical initialization path and remove unsafe overlap between SQL init scripts and `Base.metadata.create_all()`.
2. Treat **fresh bootstrap** and **legacy upgrade** separately: an empty database must migrate from zero; a test copy of legacy SQL data must migrate without destroying records. Inspect and decide how to baseline/stamp existing DBs safely; never casually stamp a mismatched schema.
3. Separate idempotent **development demo seeding** from schema migrations. Fix original seed behavior to avoid ambiguous duplicate demo data; keep production seeds/privileged accounts restricted.
4. Verify repeated startup, upgrade/downgrade where feasible, intentional constraint failures, data preservation, and integrity before/after. Back up DB before any nontrivial migration.
5. Remove `Base.metadata.create_all()` from app startup **only after** controlled migrations are ready. Provide copy-paste documented migration commands.

**Done when:** A fresh developer can follow the runbook to start Unify; a legacy test DB upgrades; schema changes are reproducible, versioned, and reviewed.

#### F1.6 — Strengthen identity, RBAC, and application security

Treat this as multiple small features, not one huge auth rewrite:

1. **Permission model:** Write `docs/security.md` with students, organizers, admins, ownership, organization scope, and sensitive endpoints; centralize FastAPI authorization dependencies and test negative cases.
2. **Privilege management:** Public signup grants student only. Organizer approval/invitation and admin role changes require authorized admin workflows. Bootstrap first admin through a secure one-time mechanism, never public registration or predictable default credentials.
3. **Sessions:** Threat-model current 24-hour JWT in `localStorage` (and its unsafe fallback signing secret when not configured); compare secure server sessions vs short-lived access + rotating refresh. Prefer revocable server-side session/refresh state; if using cookies, implement CSRF/Origin controls and secure cookie flags, logout, refresh race handling, expiry/revocation, and role-change invalidation.
4. **Account safety:** Server-enforced password validation (reasonable length, breach/common-password consideration if practical), one-time expiring email verification and password-reset tokens stored hashed, safe login errors, login/account throttling, and email enumeration protections.
5. **Input/output security:** Validate per field; don't indiscriminately strip text. Escape plain content by default; if rich text is introduced, sanitize on a defined trust boundary. Set request size limits, safe security headers, proper CORS configuration, and dependency/secret scanning. Validate image/avatar uploads if implemented.
6. **Audit trail:** Record actor, action, target ID, outcome, timestamp, and safe metadata for role changes, sensitive organizer/admin actions, and notable security events. Never log passwords, raw JWTs/refresh tokens, reset tokens, secrets, or unnecessarily personal information.
7. **Threat model:** Cover escalation, IDOR/BOLA, CSRF, XSS, token theft, brute force, event privacy, organizer cross-ownership, and denial-of-service risks. Mark controls implemented vs planned.

**Done when:** Permission tests enforce least privilege across sensitive routes, session lifecycle behaves as documented, authentication controls are tested, and audit data is safe to inspect. Feature scope may be staged without blocking urgent patches.

**Stage 1 exit gate:** The P0 authorization exploits are blocked with regression tests; database initialization/migration is deterministic on fresh and legacy test data; privileged account lifecycle is not client-controlled; sensitive routes have documented policies. **Do not proceed to major product features on top of unresolved critical correctness failures.**

---

### SECOND — TRANSACTION-SAFE RSVP AND WAITLISTING

**Outcome:** The hallmark backend feature. Seat allocation remains correct under simultaneous requests; statuses and queue ordering are explicit; cancellations fairly promote waitlisted users; attendance check-in is permission-controlled.

#### F2.1 — Define a reservation state machine and API contracts

Before touching code, settle these rules in `docs/requirements.md` / `docs/rsvp-design.md`:

- Only a **confirmed registration** occupies a seat: usually `rsvped` and `checked_in`; **`waitlisted` does not occupy a confirmed seat**. Define what happens with an unlimited-capacity event.
- Client actions: request RSVP/join waitlist; cancel. Server chooses confirmed vs waitlisted. Organizer/admin action: check in eligible confirmed user, with event ownership checks.
- State transitions: absent -> confirmed or waitlisted; confirmed -> cancelled/checked-in; waitlisted -> confirmed via promotion or cancelled; checked-in -> no casual self-cancel (decide policy); cancelled -> new request subject to capacity. Invalid transitions return a documented error.
- Decide whether cancellations **soft-delete** (retain audit/history) or remove records. Prefer explicit cancelled state if historical metrics, idempotency, and troubleshooting matter.
- Define event end/cancellation rules, visibility/invitation eligibility, organizer self-RSVP if relevant, duplicate clicks, and over-capacity capacity edits. Add a policy for unauthorized public RSVP-count disclosure and for private events.
- Decide FIFO queue stability: `waitlisted_at` timestamp + UUID as deterministic tie-breaker. Avoid relying solely on a mutable `updated_at`.
- Define HTTP responses (`201` vs `200`, `409` for business conflict, `403`/`404` for access) and user-facing UI copy; ensure accurate remaining-seat counts.

#### F2.2 — Implement atomic capacity allocation with PostgreSQL

**Core algorithm (design sketch, not a ready-to-paste implementation):**

```text
Begin DB transaction
  Validate authenticated user and event eligibility
  SELECT target event ... FOR UPDATE      # serialize seat decisions for one event
  Re-read existing RSVP for this user + event under transaction
  Resolve duplicate/idempotent request or validated transition
  Count ONLY confirmed statuses (rsvped, checked_in)
  If capacity is NULL or confirmed < capacity:
      insert/update confirmed RSVP
  Else:
      insert/update waitlisted RSVP with deterministic queue position
  Persist notification/outbox intent, if transition warrants it
Commit
Respond with authoritative status and availability
```

Use unique `(user_id,event_id)` constraints and an explicit consistent lock order in cancellation, promotion, capacity edit, and check-in operations. Consider isolation semantics and deadlocks; row locking on a shared event record is simplest for moderate event volume. Review/reconcile/remove legacy SQL trigger behavior as appropriate, ensuring the DB does not maintain contradictory capacity logic.

#### F2.3 — Cancellation and waitlist promotion

1. Lock event and relevant rows transactionally.
2. Mark the cancelling attendee `cancelled`, freeing a **confirmed** seat only when applicable.
3. If event is eligible and has a finite capacity, find the earliest **eligible** waitlisted RSVP and promote it **in the same serialized transaction**. Repeat only when multiple seats are actually free (e.g., capacity increase).
4. Commit DB state and promotion notification intent atomically. Notify after commit through in-app records/outbox; external email delivery failures must not roll back registration correctness.
5. Decide queue preservation, duplicate cancellation behavior, and what happens if the promoted user becomes ineligible.

#### F2.4 — Organizer attendance/check-in

1. Add restricted attendee-list and check-in endpoints with event owner/admin policy. Do not leak attendee identities publicly.
2. Validate event/time eligibility and current confirmed RSVP state; repeated check-in is idempotent or returns a consistent safe response.
3. Track checked-in timestamps if analytically useful; avoid using RSVP creation timestamp as check-in time.
4. Later optional signed, short-lived QR-based check-in; QR token must not be trivially forgeable or reusable outside permitted rules.

#### F2.5 — Prove the invariant with real concurrency tests

**Use PostgreSQL, not SQLite/mock-only tests.**

- Test capacity=5 with 100 parallel distinct users -> **exactly five confirmed and 95 waitlisted**, assuming all 100 requests are valid and succeed; no duplicates; no confirmed count above capacity.
- Test capacity=1 with competing requests and multiple repetitions. **Include cancelled/waitlisted → confirmed status UPDATE at capacity**, which the existing SQL trigger mishandles.
- Test same user submitting simultaneous duplicate RSVP requests -> at most one RSVP row.
- Test concurrent cancel/register/promote interactions, including multiple waitlisted users, deterministic ordering, transaction errors/retries, and no double promotion.
- Test `capacity=NULL`, `capacity=0`, full events, event cancellation/expiration, privacy enforcement, and checked-in count behavior.
- Test manual capacity reduction, if allowed: define whether reject reductions below already confirmed count or an explicit administrator policy.
- Capture database isolation/locking technique and repeatable test results. Do not invent throughput, race-free guarantees, or benchmark numbers without actual runs.

**Stage 2 exit gate:** Invariant **confirmed_count <= capacity for capacity-limited events** holds across automated PostgreSQL stress tests; waitlist promotion is deterministic; cross-user and cross-organizer writes are denied; UI receives authoritative reservation states.

---

### THIRD — AUTOMATED TESTING AND CI/CD

**Outcome:** Automated checks make regressions difficult to merge and let anyone reproduce verification. This stage **formalizes and extends** tests written in Stages 1–2; it is not permission to defer security and concurrency tests.

#### F3.1 — Backend unit and API integration tests

- Adopt **Pytest** with HTTPX/FastAPI test client strategy compatible with installed versions; deterministic fixtures; safe test DB isolated from development/prod.
- Use real PostgreSQL for schema/integrity, authorization, RSVP concurrency and migration tests. Mock only external integrations, not the database behavior whose correctness is being claimed.
- Unit-test service-level validation, state transitions, time logic, and error mapping. Integration-test request -> auth -> DB commit -> response -> persisted state.
- Required negative test matrix: forged admin/organizer signup, student organizer endpoints, other organizer's event update, **cross-organization event association**, private event read/RSVP/**unauthenticated count**, self-check-in, expired/revoked token, cross-user notification access, malformed inputs, overcapacity, repeat actions, **failed tag insert must not persist event**, flawed trigger UPDATE transition.
- Test transaction rollback (including organizer event+tags atomic create), unique constraint conflicts, database migration bootstrap, and email-worker failures as those features arrive.
- Report coverage, but prioritize behavior-risk coverage rather than an arbitrary 100% target.

#### F3.2 — Frontend quality gate

- Add **Vitest + React Testing Library** (or a coherent alternative only if justified).
- Validate login/register forms; event listing/cards; filtering, loading/empty/error states; RSVP/waitlist visual transitions; organizer forms; protected-page UX; accessible controls and keyboard interactions.
- Centralize API/error handling and mock requests deterministically. Consider generated types from FastAPI OpenAPI to reduce frontend/backend drift.
- Enforce `npm run lint`, `npx tsc --noEmit`, frontend unit tests, and `npm run build` in reproducible dependency environment. Note current npm package is `frontend/513-app`, **not** root.

#### F3.3 — Playwright end-to-end flows

- Build a small, high-value smoke suite against ephemeral demo/test data: student signup/login, event browsing, register/cancel, waitlist promotion, organizer event creation/edit/check-in, admin approval where implemented, negative access.
- Use stable selectors and isolated test users; avoid relying on shared seed ordering or external email availability.
- Include mobile viewport and accessibility smoke checks. E2E may run in a dedicated CI job when runtime cost warrants it.

#### F3.4 — GitHub Actions and branch hygiene

- On PRs to `main` (and chosen pushes), run backend lint/type/static checks as configured, backend unit/integration tests with PostgreSQL service, frontend lint/TypeScript/unit/build, migration bootstrap check, and affordable dependency/secret scans.
- Add branch protection after checks are stable. Keep workflow permissions minimal, avoid leaking CI secrets into untrusted PRs, pin actions/dependencies sensibly.
- Publish test/coverage reports if useful, and give failing tests actionable names.
- Require each PR to explain **problem, affected behavior, design/trade-offs, tests executed, risks, screenshots if UI**, and docs/handoff updates.
- Reproduce CI commands locally when practical; don't silently skip failures.

#### F3.5 — Quality review beyond automation

- Manual code review for security, ownership, migration safety, error handling, logging privacy, keyboard access, and API contracts.
- Add meaningful test cases for every bug found (especially regressions) rather than patching symptoms.
- Define WCAG **2.2 AA as a target**, not an unverified claim; combine automated tools (e.g. axe) with keyboard and screen-reader/manual testing.

**Stage 3 exit gate:** A deliberately broken security or RSVP invariant causes CI failure; CI passes on the real intended branch; documented local commands match CI; no build/test claims are made without logs/results.

---

### FOURTH — COMPLETE AND POLISH THE APPLICATION

**Outcome:** The core student and organizer workflows are functionally complete, consistent, accessible, responsive, and honest about what they do. No more placeholder pages masquerading as features.

#### F4.1 — Complete event lifecycle and organizer CRUD

- Introduce explicit `draft`, `published`, `cancelled` (possibly `completed`) event lifecycle only after defining permission/state rules. Separate `is_public` **visibility** from publication **status**.
- Implement draft save/publish, edit, cancel, and delete/archive policy through backend API and migrations. Avoid deleting historical attendance/audit data casually.
- Ensure ownership/**organization membership/association** checks, date/capacity validation, transactional **event creation AND event+tag updates** (the current create path commits in two stages), and affected-attendee notifications as needed.
- Fix frontend dashboard draft branch/delete/preview scaffolding to match actual endpoints. Ensure admin frontend routing matches backend permissions.
- Fix event-detail API response to include accurate capacity, tags, organization/organizer metadata as intended; do not represent full events as unlimited.

#### F4.2 — Student discovery, search, and calendar

- Replace `app/(auth)/calendar/page.tsx` and `app/(auth)/rsvp/page.tsx` placeholders with useful, tested experiences (or remove misleading nav links until ready).
- Server-side paginated search with keywords, tags/categories, upcoming/date range, sort, visibility/status filters; avoid fetching all events into browser indefinitely.
- Monthly/list calendar views, timezone-consistent event dates, saved/bookmarked events (only if value justifies added tables), RSVP/history page, accurate capacity/waitlist indicators.
- Responsive/mobile behavior and clean loading, empty, 401/403/404, and retry states. Support deep links and browser back navigation.

#### F4.3 — Organizer attendance and communication UI

- Attendee table with appropriate privacy controls, confirmed/waitlist/cancelled filters, check-in status and safe CSV export (spreadsheet formula injection defense); optionally signed QR check-in later.
- Accurate real-time-enough counts via server endpoints; no fake analytics or frontend-only invented capacity percentages.
- Send reminders/update notices through real in-app notification semantics. Rename the misleading “send push” if no push is implemented; avoid promising web push/email before they're delivered.

#### F4.4 — Profile, settings, forms, and API consistency

- Make currently disabled/editable profile fields coherent. Align theme UI and stored settings intentionally; handle email/push preferences only for real delivery channels.
- Consolidate request/error handling; define typed response DTOs and generated OpenAPI TypeScript contracts where worthwhile. Standardize API validation/errors and predictable empty responses; `204` must not be parsed as JSON.
- Audit labels, keyboard focus, color contrast, form validation, date picker locale/time zone, toasts, accessibility targets, and small-screen navigation. Prefer finishing the existing design system over a complete redesign.
- Remove stale files/redundant lockfiles only after confirming they are unused; keep cleanup in small separate PRs rather than bundling with security fixes.

#### F4.5 — Product acceptance scenarios

- Student: create account -> log in -> search published public event -> see exact time and availability -> RSVP/waitlist -> cancel -> view notifications/profile.
- Organizer: get approved -> create draft -> publish -> edit -> inspect attendees -> communicate -> check in eligible students -> observe correct counts.
- Admin: bootstrap securely -> grant/revoke organizer -> inspect audit and moderate as implemented.
- Each scenario has both happy paths and failure paths, browser E2E verification, and a documented ownership/permissions rule.

**Stage 4 exit gate:** All links prominently offered in the UI lead to functioning routes; no mock functionality is mislabeled as production; critical student/organizer scenarios pass E2E tests on desktop and mobile; accessibility problems are tracked and high-impact ones resolved.

---

### FIFTH — DEPLOYMENT, OBSERVABILITY, AND PERFORMANCE

**Outcome:** Unify is a genuinely usable HTTPS demo with repeatable delivery, safe configuration, actionable operational telemetry, recoverable data, and *measured* performance.

#### F5.1 — Reliable local infrastructure

- Review `docker-compose.yml` for environment-specific secrets (no hardcoded deployable JWT/DB values), services, persistent DB volume, isolated networks, unnecessary host-published database port, restart/readiness behavior, and correct startup dependencies.
- Use `.env.example` and ignored local `.env`; secrets live in deployment secret store. Ensure image/build reproducibility (lockfile, Python dependency pinning), sensible non-root execution, multi-stage builds if useful.
- Add `/health` liveness and separate readiness that checks required dependencies. A trivial `{"status":"ok"}` is **not** proof of DB readiness.
- Validate database migration ordering as a deployment step; do not rely on importing FastAPI to create schema. Document safe resets for **disposable test/dev data only**. Do not run `docker compose down -v` on valuable data.
- Decide same-origin `/api` reverse proxy/BFF vs cross-origin architecture; review cookie flags, CSRF/Origin validation, CORS, HTTPS and Next.js build-time environment injection.

#### F5.2 — Choose and execute a practical public deployment

- Compare a few manageable options by cost, HTTPS support, persistent managed PostgreSQL, secrets, Python worker support, logging, backup and operational simplicity. Do not choose Kubernetes just for buzzwords.
- Deploy staging/demo environment, run migrations against a backed-up persistent DB, verify frontend/API version compatibility, establish a controlled deploy from protected `main` after CI passes.
- Provide safe synthetic/demo data and accounts; never publish admin credentials or user records; avoid public role escalation from seeds. Rate-limit abusive endpoints and consider demo reset strategy.
- Validate signup/auth flows, email/reset depending on implementation, RSVP/waitlist, organizer tooling, and mobile UX on the **deployed system**, not just localhost.
- Configure HTTPS, domain/cert handling, CORS/Origin/cookies, secrets, automated backups, tested restore, and a basic incident/recovery runbook.

#### F5.3 — Reliable notifications and background operations

- Distinguish **notification record creation** (DB) from **actual delivery** (email/push). The existing `/send-push` is not real push.
- Add a mail provider abstraction and templates for account verification, password reset, RSVP/waitlist promotion, event updates and reminders only as product requirements justify.
- For retryable/scheduled work use a durable job queue or transactional outbox + worker, selecting Redis/RQ/Celery or a simpler appropriate alternative deliberately. Keep delivery state, retry count, exponential backoff, dead-letter/failure inspection, deduplication/idempotency.
- Confirm failure of mail provider cannot undo committed seat allocation; preferences/opt-outs honored where appropriate; avoid emailing unverified/private information.
- Test worker downtime/restart, duplicate jobs, provider errors, schedule clock/time zones, and no duplicate email for retried jobs.

#### F5.4 — Observability and operations

- Use structured logs with request/correlation ID, route, severity, latency, status, and safe identifiers. Redact or omit secrets, authentication headers, tokens, PII and sensitive event details.
- Record key application metrics: 5xx errors, slow API endpoints, DB connection health, job failures/queue age, sign-in throttling, RSVP conflicts, confirmed capacity invariant violations (if detectable).
- Add basic exception/error tracking and availability alerting, with cost/retention guardrails. Document how to investigate common incidents and how to restart/redeploy safely.
- Implement an audit trail for security/business-sensitive actions without confusing it with infrastructure logging; authorization applies to who can read audit records.

#### F5.5 — Real performance and load testing

- Use **k6 or Locust** against staging/isolated data. Capture hardware/hosting tier, seed size, ramp pattern, total/concurrent users, endpoint mix, request duration, throughput, 4xx/5xx rates, p50 and p95 latency, DB bottlenecks, and cost if relevant.
- Especially test RSVP race conditions separately from ordinary browsing throughput; a fast but overbooking endpoint is not a successful result.
- Use SQL query analysis (`EXPLAIN [ANALYZE]` in safe environments), indexes, N+1 detection, pagination, and query tuning only after measuring an issue; rerun equivalent workload after improvements.
- Store dated reproducible commands and raw summaries in `docs/performance.md`. **Never invent or reuse unverified résumé statistics** (requests/sec, “X% faster,” load users, coverage, uptime).

**Stage 5 exit gate:** Public HTTPS deployment works with persistent data, health/logs/alerts are useful, secrets are protected, the migration/restore runbook was exercised, key product flows work online, and a dated reproducible performance report exists. Document any operational limitations honestly.

---

### FINALLY — ANALYTICS, ADVANCED FEATURES, AND PORTFOLIO PRESENTATION

**Outcome:** Grounded analytics and selective differentiators strengthen the existing product; a recruiter can understand, try, inspect, and discuss the project quickly.

#### F6.1 — Meaningful organizer analytics (inside the app first)

- Real data from PostgreSQL: confirmed registrations, checked-in count, show-up rate, capacity utilization, cancellations, waitlist size, registration trend, popularity by event/category.
- **Define formulas**; for example:
  - `confirmed = count(status in ('rsvped','checked_in'))` (unless historical snapshot semantics change);
  - `checked_in = count(status='checked_in')`;
  - `capacity_utilization = confirmed / capacity * 100` only for a meaningful positive finite capacity (handle NULL/0);
  - `attendance_rate = checked_in / eligible_or_confirmed_population * 100` with a documented denominator and time snapshot; don't conflate it with utilization.
- Consider keeping attendance/history records so rates remain meaningful after event end and cancellations. Test exact SQL results using fixtures and edge cases.
- Scope metrics by organizer ownership (and approved organization membership, if implemented); validate exports/queries for PII leaks. Use sensible aggregation and pagination.

#### F6.2 — Admin oversight and operational analytics

- Admin-only account/organizer approval queue; limited moderation; platform event counts, aggregate attendance trends, organization activity, and sensitive-action audit explorer.
- Define privacy boundaries and role checks; administrative views must not become public data endpoints.
- Provide graphs/tables with truthful data, understandable labels, date filters, and downloadable reports where useful.

#### F6.3 — Optional, strictly gated differentiators

**Only after mandatory functionality works:**

- **AI-assisted event discovery:** natural-language query -> validated structured query parameters -> authorized event search -> return only existing, visible events and their real links. Cost budget, privacy filtering, failure fallback, hallucination prevention and evaluation tests are mandatory. **Not** a generic chatbot.
- **QR-based event check-in:** signed/expiring credential, organizer-authenticated scanner, replay policy and attendance audit trail.
- **Multi-organizer/organization teams:** membership model and granular ownership authorization, only if actual product needs warrant complexity.
- **Calendar import/export** and accessible progressive enhancement where useful.
- **Power BI:** optional read-only aggregate analytics showcase *outside the core application*; the PDF notes analytics is being developed as a separate portfolio project. Don't let a BI integration dominate Unify.
- More complex cloud/microservice architecture is **not a default stretch**. Only add when justified by measured requirements.

#### F6.4 — Final portfolio deliverables (build these throughout, polish here)

**Repository artifacts**

```text
README.md                 Product summary, live demo, screenshots, quick start,
                          working features, stack, architecture, honest limits
HANDOFF.md                Current state, latest branch, next task, test results
 docs/ROADMAP.md          This feature-oriented strategic plan / source roadmap
 docs/requirements.md     Personas, use cases, user stories, acceptance criteria
 docs/architecture.md     System diagram, modules, data flow, deployment diagram
 docs/database.md         ERD, schema decisions, migrations and rollback hazards
 docs/security.md         Permission matrix, threat model, session flow
 docs/rsvp-design.md      State machine, locking, ordering, idempotency
 docs/decisions/          Short architecture decision records (ADRs)
 docs/testing.md          Test strategy and exact local/CI commands
 docs/performance.md      Dated honest benchmarks, environment and methodology
 docs/runbook.md          Local/dev/prod operations, migrate, backup, restore
 docs/contributions.md    Original team work vs personally implemented revamp
```

**Public project story**

1. A recruiter should understand the problem, stack, and live demo link within ~30 seconds.
2. An engineer should be able to follow quick-start/migrations/test instructions without private tribal knowledge.
3. Show before/after defects, architecture trade-offs, secure RBAC, real SQL transactions, concurrency tests, CI screenshots, deployment runbook and honest measurements.
4. Present a **90–120-second demo**: student signup (cannot forge admin), event discovery/privacy, RSVP, full event waitlist, cancellation/promotion notification, organizer attendee check-in, admin approval/overview; optionally show passing concurrent tests and CI.
5. Describe Unify accurately on résumé/portfolio **only after evidence**. Avoid fictional metrics, “production-grade” if controls are incomplete, or claims that the university team's original functionality was all personally built.
6. Prepare interview explanations: why FastAPI/PostgreSQL, why modular monolith, why event-row lock, why not count-then-insert, why waitlisted users don't use capacity, why auth cookies need CSRF control, how migration preserved data, how CI prevents regressions, how logs avoid PII, what failed and how it was fixed.

**Stage 6 exit gate:** Analytics values match known DB fixtures, optional additions have justified impact and tests, README/demo accurately reflect reality, and contributions/measurements can be independently inspected.

---

## 4. Priority tiers and non-negotiable rules

| Priority | Deliverables | Policy |
|---|---|---|
| **P0 — immediate security** | Client role escalation, private detail/RSVP exposure **including unauthenticated count**, user-controlled `checked_in`, regression tests | Fix before feature expansion; may start before migration work. |
| **P1 — strong portfolio core** | Coherent Alembic schema **including the capacity trigger defect**, transaction-safe RSVP/waitlist, organization-scope RBAC, atomic organizer writes, automated test/CI baseline, complete main user journeys, reproducible Docker, HTTPS demo, README | Essential before declaring portfolio release complete. |
| **P2 — production-oriented maturity** | Secure session lifecycle, password reset/verification, controlled organizer approvals, useful audits, email/retry worker, logging/monitoring, attendance analytics, measured performance, WCAG-focused accessibility | Introduce incrementally; prioritize based on risk, product utility, and time. |
| **P3 — optional differentiators** | AI event search, signed QR, Power BI, org teams, advanced infra | Do not build while important P0/P1 invariants fail. |

**Engineering safety rules**

- **No mass Git/EOL “fixes” by default.** The archived ZIP falsely reports 67 modified tracked files due solely to CRLF conversion. Verify meaningful diffs and commit only intended files; never blindly add everything.
- **No destructive database “fixes” by default.** Do not remove volumes, drop tables, reset Git, force-push, or change production secrets without explicit user permission and a verified backup/rollback plan.
- **No architecture astronautics.** Avoid premature repositories/microservices/Redis/Kubernetes and unrelated large refactors. Refactor only what supports an actual change.
- **No invented proof.** Separate “present in source,” “test passed locally,” “passed in CI,” “verified in deployed environment,” and “planned.” A passing `compileall` proves syntax only.
- **Server-side rules are authoritative.** React routing, disabled buttons and visual hiding are not authorization.
- **Least privilege and privacy by design.** Treat event ownership and attendee records as protected. Every new API endpoint needs explicit auth/ownership review.
- **Reliability over optimistic UI.** UI must show confirmed server outcomes, handle failures/retry without duplicate side effects, and reflect accurate availability.
- **Testing is part of a feature.** Regression tests for bugs; migrations for DB changes; API integration tests for permission changes; UI tests for new visible behavior.
- **Avoid scope inflation.** Prefer a complete, deployed P1 to an unfinished collection of P1–P3 features. Continue applying for opportunities while improving project.
- **Attribution matters.** Never claim group-created components as original solo work; clarify new contributions through PRs and documentation.

---

## 5. Standard development and Git workflow — use for EVERY feature

### 5.1 Before changing code

1. Read this handoff's **Current-state ledger** and **Next action**, then the relevant stage, last PR/issue, and actual source files.
2. Inspect `git status --short --branch`, branch/HEAD, recent commits, and CI status. If this file disagrees with Git/runtime, **Git and observed behavior win**; update the handoff with the correction.
3. State the **specific user-visible or security behavior**, acceptance criteria, affected files/data, possible migration risk, and which tests are needed.
4. Explain architecture options and trade-offs to the user *before* major changes. Ask approval before unrelated refactors, destructive operations, or significant architecture pivots.
5. Create an issue (or clear feature note) and a branch from the **latest stable** `main` after confirming a clean working tree.

**Illustrative commands (only after verifying remote and branch existence):**

```bash
git status --short --branch
git switch main
git pull --ff-only origin main
git switch -c fix/registration-role-escalation
# develop one focused change; review, test, and commit
```

`git pull --ff-only` avoids surprise merge commits. If the working directory has uncommitted changes or remote names differ, investigate first—do not blindly run commands.

### 5.2 Implement and verify

1. Write a minimal repro/failing regression test or acceptance test.
2. Implement the smallest coherent solution; keep authorization and transactions on backend; update DTOs and UI as needed.
3. Run focused tests first, then relevant integration tests, lint, type check, build, and targeted manual flows. Capture **actual** commands and results.
4. Review staged diff (`git diff`, `git diff --check`, `git status`) for unrelated files, hard-coded credentials, accidental generated files, missing migrations, ownership bypass, and privacy leaks.
5. Update documentation/ADR and handoff, and ensure the handoff itself does **not prematurely claim** a pending PR is merged.
6. Commit with meaningful message; push feature branch; open PR describing problem/design/tests/risks. Review CI and only merge to stable `main` when criteria are verified.

**Example commit/PR:**

```text
Branch: fix/registration-role-escalation
Commit: fix(auth): prevent public registration of privileged roles
PR: Security: block organizer/admin self-registration
PR body: Problem | Design | API behavior | Tests run | Risk | Docs
```

### 5.3 After merge / end of chat

- Switch/sync local `main` only after merge; verify merge commit and working tree.
- Update the **Current-state ledger**: exact merged PR/commit, verification results, still-open bugs, and next single task. If handoff was updated only on a feature branch, ensure that update is included in the merge or record a follow-up.
- Keep one concise handoff per active project state; the Git/PR history preserves the detailed journal.
- If the chat ends mid-feature, record branch, uncommitted/committed status, files touched, last command/output, known failures, next immediate step, and **do not claim finished**.

---

## 6. Verification commands and test evidence rubric

**These are proposed or source-supported commands, not proof they currently succeed. Execute from the correct path in a configured environment.**

```bash
# Repository investigation (run in actual Git clone)
# Archive-only Git fact: main/archived origin-main @ 7411d45; live remote may differ.
# NOTE: The extracted ZIP has 67 false modified text files from CRLF conversion.
git status --short --branch
git branch --show-current
git log -1 --oneline
git remote -v
git diff --stat
git diff -w --exit-code  # ONLY a diagnostic for the archived CRLF anomaly; not a substitute for reviewing real changes

# Docker Compose file validation (from repo root)
docker compose config

# Initial Docker startup in a SAFE, DISPOSABLE environment
# Check volumes/secrets/ports first; don't destroy existing data.
docker compose up --build -d
docker compose ps
docker compose logs --tail=100 backend
curl -i http://localhost:8000/health

# Source syntax check (from repo root; NOT a runtime test)
python -m compileall -q backend/app

# Frontend dependency and quality checks (from frontend/513-app)
npm ci
npm run lint
npx tsc --noEmit
npm run build

# Proposed tests after harness is implemented (from repo root or backend)
# python -m pytest -q                   # command/location must be documented
# npm run test                           # script needs to be added
# npx playwright test                    # only after configuration exists

# After Alembic is added: document project-specific invocation/environment
# alembic upgrade head                   # not currently configured
```

**Verification status vocabulary**

- **Source-observed:** Code shows a behavior/risk; no runtime claim.
- **Reproduced:** A failing test or manual request actually demonstrated a defect; record command/status/output.
- **Fixed, locally verified:** Changed behavior passed named tests in the working branch; note tests not run.
- **CI verified:** Specific workflow URL/commit passed; not equivalent to prod verification.
- **Deployed verified:** Exact live URL, version, user journey, date, logs/metrics verified.
- **Not verified / blocked:** State why, including unavailable Docker/Node/dependencies/network/secrets.

**Core test/evidence matrix**

| Invariant / claim | Minimum evidence |
|---|---|
| No public admin or organizer signup | Negative API tests + DB role assertion |
| Private event privacy | Anonymous/other-user/owner/admin matrix across related endpoints |
| No student-controlled check-in | Forged payload denied + organizer-authenticated check-in test |
| Schema integrity | New empty PostgreSQL migration + legacy-copy upgrade + constraints |
| No overbooking | Concurrent PostgreSQL requests with confirmed <= capacity assertion |
| Fair waitlist | Multiple queue positions + cancellation/promotion deterministic fixture |
| User-facing RSVP accuracy | Frontend integration + Playwright scenario |
| Session security | Refresh, logout, expiry, rotation/replay, CSRF/Origin tests as applicable |
| CI guard | Workflow run tied to commit + intentional regression shown as failure |
| Deployability | HTTPS smoke test + real DB persistence + migration/restore test |
| Performance | Timestamped load-run config, dataset, percentiles, error rate, no invented numbers |
| Accessibility | Automated scan plus keyboard/manual verification with issues tracked |
| Contribution attribution | Small PRs, ADRs, group-team baseline vs personal changes |

---

## 7. Documentation, employer relevance, and portfolio story

### 7.1 Recommendations integrated from the 11-page PDF

- **Pages 1–2:** Employers across software engineering, cybersecurity, infrastructure, and product roles repeatedly value Python/React/SQL, testing/debugging, access control, automation, Docker/DevOps, documentation, and product thinking. The PDF favors broad **engineering quality** over turning Unify into a second analytics project.
- **Page 3:** SQLAlchemy/SQL schema drift and absence of migrations are primary reliability issues. Fresh clone + migration + seed without manual repair is an explicit target.
- **Pages 4–5:** Concrete role self-escalation, private-event disclosure, RSVP waitlist/counting/authorization issues. Page 5's flow diagram motivates event-row locking, waitlisting, and automatic promotion.
- **Page 6:** Pytest, HTTPX, PostgreSQL integration/concurrency tests, Vitest/React Testing Library, Playwright, and GitHub Actions; verify concrete malicious/edge cases.
- **Page 7:** Docker secrets/network/readiness, public HTTPS deployment, and measured reliability without needless Kubernetes.
- **Page 8:** Organizer attendance/check-in, real calendar/search, true notifications; optional natural-language event discovery grounded in actual authorized DB results; accessibility and mobile UX.
- **Page 9:** README, architecture diagrams, requirements/user stories, Git issue/PR history, and explicit distinction between original group contributions and personal revamp.
- **Page 10:** Role-specific portfolio framing; existing résumé performance and concurrency figures must be independently verified before repetition. Never substitute impressive numbers for evidence.
- **Page 11:** Prioritize security + transaction-safe RSVP + tests/CI, then deployment/product polish; avoid kitchen-sink complexity.

### 7.2 Earlier discussions deliberately retained

- Original audit: UI and API completeness, incorrect capacity display, organizer role-guard mismatch, broken draft concept, mock push, stale backend event code, incomplete settings and missing calendar/RSVP pages.
- Production-oriented recommendations: refresh/revocation, password reset, email verification, RBAC ownership checks, audit logging, rate limiting, controlled organizer onboarding, safer session storage, background reminders/retries, structured logs, CI, load testing, deployment, dashboards, strong README.
- Later refinements: WCAG 2.2 AA target, dependency checks/XSS-safe rendering, early deployable portfolio checkpoints, short-lived Git branches, self-contained handoff for continuity, and mentorship-first development.

### 7.3 Realistic demo narrative

1. Attempt forged admin registration via API -> rejected or student-only.
2. Register/login as student, search valid published event, and demonstrate private-event access denial.
3. RSVP for remaining seat; a second student joins waitlist when full.
4. Cancel confirmed seat; oldest eligible waitlisted user is promoted, sees in-app notification (and email only if actually implemented).
5. Organizer views attendees and checks someone in; student cannot forge check-in.
6. Admin approves organizer/inspects audit activity where implemented.
7. Show real test suite and CI result, concurrency test proof, architecture/ER diagram, live HTTPS deployment, and measured results.

### 7.4 Interview explanations to prepare, with evidence

- **Why a modular monolith?** Less deployment/test friction and clear modules for this scale; microservices increase distributed failure modes.
- **Why PostgreSQL?** Real relational integrity and row-level locks allow correct capacity allocation.
- **Why not `COUNT(*)` then insert?** Concurrent requests can observe same count before committing; serialize decisions on a common row/transaction.
- **Why migrations?** `create_all()` cannot safely express versioned changes to existing tables; upgrade paths and data preservation matter.
- **RBAC vs resource ownership?** Organizer role permits a category of action; event ownership limits which specific records that person may act upon.
- **Why not long-lived localStorage JWT?** JavaScript-exposed tokens risk theft under XSS and are difficult to revoke; secure sessions/refresh rotation have their own CSRF trade-offs.
- **Why reliable queue/outbox?** A DB commit and an external email request cannot be treated as one atomic event; retries need idempotency and durable intent.
- **How are performance claims honest?** Reproducible workload, environment, measured p50/p95/errors, and before/after comparison; no fabricated figures.
- **What did you personally build?** PRs and contribution doc answer precisely.

---

## 8. CURRENT-STATE LEDGER — update at every meaningful stopping point

> **Live evidence update: 2026-10-11, after F1.1 security commit `9239fda`.** This ledger records user-provided terminal output from the real Windows clone. It supersedes archived-only status statements elsewhere in this handoff. The security commit is locally verified; documentation, push, PR, CI and merge are not yet verified.

| Field | Last known verified value |
|---|---|
| Date | **2026-10-11** (F1.1 post-security-commit update) |
| Project / stage | Unify 2.0 / **FIRST — Security and database correctness** |
| Current task | **F1.1 code committed; update/commit handoff, push, open and review PR** |
| Local working directory | `C:\Users\tausi\Projects\Unify` (user terminal output) |
| Active local branch | **`fix/registration-role-escalation`**, created from `main` at `7411d45`; currently at **`9239fda`** |
| Local `main` / fetched `origin/main` | Both `7411d45`; `git rev-list --left-right --count main...origin/main` returned **`0 0`** after `git fetch origin` |
| Last verified Git state | Security commit **`9239fda`** created successfully (`fix(auth): prevent public registration of privileged roles`); commit contains four intended files, **99 insertions and 19 deletions**. The last `git status --short` shows only **`?? HANDOFF.md`**. |
| Files in `9239fda` | `backend/app/routers/auth.py` (M), `backend/requirements-test.txt` (A), `backend/tests/test_registration.py` (A), `frontend/513-app/app/(public)/auth/page.tsx` (M) |
| Handoff on real local disk | `HANDOFF.md` is present in repository root and **untracked** (`?? HANDOFF.md` after security commit). Replace/update it with this revision, review, stage, and commit separately. |
| Security exploit reproduction | Pre-fix manual POST `role=admin`: **HTTP 201**, response `admin`, PostgreSQL `users.role=admin`. Pre-fix automated negative cases for `admin` and `organizer` both failed (`201` instead of expected `422`). |
| F1.1 implementation | `RegisterRequest.role` constrained to `Literal[models.UserRole.student]`, server constructor assigns `role=models.UserRole.student`; public frontend registration payload omits role and role dropdown is login-only. |
| Post-fix automated test | **4 passed, 2 dependency warnings in 1.24s**, with Pytest+FastAPI TestClient+isolated PostgreSQL (`unify_auth_pytest`). Cases: malicious admin and organizer rejected/no user persisted; student omitted/explicit accepted and stored student. |
| Post-fix manual API check | Both malicious role requests returned **HTTP 422** via updated running API on `127.0.0.1:8001`; student registration **HTTP 201**, login returned token, `/api/auth/me` returned role `student` and matching email. |
| Backend runtime | Python 3.11 Docker image built; isolated PostgreSQL 16 responded `accepting connections`; FastAPI startup and `/health` succeeded. Local host Python is 3.13.16; native Python 3.11 not installed. |
| Test isolation | Docker network `unify-auth-test-net`, ephemeral container `unify-auth-test-db` with tmpfs; databases `unify_auth_test` (manual) and `unify_auth_pytest` (automated). API container `unify-auth-test-api` uses `/app` read-only bind mount and `DATABASE_URL` host `unify-auth-test-db`; **existing persistent `unify_db_data` volume preserved**. |
| Frontend tooling | Node 24.21.0, npm 11.19.0 via `npm.cmd`; `npm.cmd ci` installed 438 packages. |
| Frontend TypeScript / build | `npx.cmd tsc --noEmit` **passed**. `npm.cmd run build` **passed** Next.js 16.0.1 production build, 12 routes; warnings about browser mapping freshness and multiple package lockfiles. |
| Frontend ESLint | `npm.cmd run lint` **failed**, **12 errors + 2 warnings**; reviewed as present in archived baseline (React state-in-effect, explicit any, hook dependency, unused import). Do not claim a green lint gate. |
| Dependency audit | npm reported **26 vulnerabilities (1 low, 3 moderate, 21 high, 1 critical)** after `npm.cmd ci`; affected advisories/packages not yet triaged. `sharp`/`unrs-resolver` install-script warnings also observed. |
| Commit/push/PR/merge | **Security commit `9239fda` created locally.** No push, PR, CI pass or merge reported. Documentation commit pending. |
| CI/deployment | No committed CI in original snapshot; no public deployment verified. |
| Remaining P0 risks | Private event detail and unauthenticated count; client-controlled RSVP checked-in; cross-organization authorization; other security findings from original audit. Original manual test-created admin exists only in disposable test DB until cleanup. |
| Roadmap | Original 6-stage feature roadmap remains authoritative. Placement of reviewed roadmap in `docs/ROADMAP.md` pending. |

### Evidence-backed work completed in this development session

- [x] **F1.0 Git:** Confirmed actual local working tree initially clean; live GitHub `origin/main` synchronized after fetch. Archived ZIP's 67 CRLF-only apparent changes were **not present** in real working checkout.
- [x] **F1.0 environment:** Docker 29.8.1 engine and Compose 5.5.1 available; `docker compose config --quiet` passed; no Compose project containers initially; existing `unify_db_data` volume identified and preserved. Node/npm installed, local Python 3.13.16, Docker backend Python 3.11.
- [x] Created short-lived branch `fix/registration-role-escalation` at `7411d45`.
- [x] Reproduced admin role escalation with real HTTP 201 and database role assertion in **disposable** Postgres.
- [x] Created test requirements and four API/DB regression cases; first run **2 failed (expected security cases), 2 passed** before fix.
- [x] Changed registration validation and server-side student assignment; updated frontend signup and dropdown policy.
- [x] Re-ran all four tests after final backend change: **4 passed, 2 warnings in 1.24 seconds**.
- [x] Confirmed live API rejects `admin` and `organizer` with HTTP 422 and valid student can register, login, and use `/api/auth/me`.
- [x] Frontend TypeScript check and production build passed; lint and npm audit findings recorded without broad refactors.
- [x] Reviewed existing-file Git diffs and untracked test files; staged exactly four intended feature files and passed `git diff --cached --check`.
- [x] Created the focused local security commit **`9239fda`** (`fix(auth): prevent public registration of privileged roles`) with four files and no handoff bundled into that code commit.
- [x] Placed `HANDOFF.md` in the repository root; confirmed it is untracked after the security commit.
- [ ] Replace/update local `HANDOFF.md` with this post-commit revision, review and make a separate documentation commit.
- [ ] Push branch, open PR, inspect checks/diff, and merge after review and approval.

### Known limitations and deferred work

- Registration tests explicitly validate `DATABASE_URL` before importing `app.main` (which runs `create_all()`). They verify the ORM-created test schema, **not** legacy SQL migration compatibility.
- Test email cleanup is fixture-based; the disposable manual reproduction DB may contain test-created accounts until the ephemeral container is stopped. No valuable database volume was modified through the described test flow.
- Manual login and `/api/auth/me` were verified, but those actions are **not yet automated** in the four-test suite.
- No browser end-to-end UI test has been executed. Successful Next.js build does not prove browser behavior.
- The test dependency versions are ranges, not fully locked. Dependency stabilization can be addressed separately.
- Pytest surfaced Starlette `httpx`/TestClient deprecation guidance and Passlib Python `crypt` deprecation. Document, don't automatically upgrade inside this fix.
- Fixing public role creation does **not** revoke any unauthorized privileged accounts already present in valuable databases. Review legacy accounts before public deployment.
- The logged ESLint failures, npm vulnerabilities, duplicate lockfiles, stale browser mapping data, and Docker warnings are separate follow-up issues unless they block release/security.

### Open decision register

1. **F1.1 already decided:** Reject elevated role input with HTTP 422 and make the server assign `student`; existing privileged users keep access to login. Organizer promotion and admin bootstrap need a later authorized workflow.
2. How will initial admin accounts be bootstrapped securely, and how will organizer privileges be approved/revoked?
3. What privacy/authorization rules apply to private-event viewing, RSVP and count endpoints?
4. What canonical SQL/ORM types, triggers, views, and Alembic migration paths preserve legacy data?
5. What session lifecycle (cookies or access+rotating refresh) best fits threat model and deployment?
6. What RSVP state transition, cancellation, waitlist, and capacity policies are required?
7. What operational/hosting setup, notifications, accessibility and optional features fit product needs?
8. How should original university group contributions be documented relative to new Unify 2.0 changes?

---

## 9. EXACT NEXT-CHAT / NEXT-SESSION PLAYBOOK (updated 2026-10-11)

**Immediate goal: finish documenting and opening the already-committed F1.1 fix as one focused PR, not the entire security stage.**

1. **Current Git:** user's last output shows `fix/registration-role-escalation` at **`9239fda`** (local security commit), while `main` and previously fetched `origin/main` remain at `7411d45`. Four intended code/test files are committed. `git status --short` shows **`?? HANDOFF.md`**. Recheck actual Git state before further action.
2. **Update handoff in repository:** `HANDOFF.md` now exists but is **untracked**. Replace/update that local file with this post-commit revision, keeping its full roadmap. Verify contents (especially current ledger), then `git add -- HANDOFF.md`, `git diff --cached --check`, and `git diff --cached --stat`; make a separate documentation commit. Do not overwrite a newer on-disk handoff without review.
3. **Final code review:** committed feature files in `9239fda`: `backend/app/routers/auth.py`, `backend/requirements-test.txt`, `backend/tests/test_registration.py`, and `frontend/513-app/app/(public)/auth/page.tsx`. Inspect `git show --stat 9239fda` if needed; avoid staging unrelated files. If further code edits occur, rerun relevant checks.
4. **Known good testing evidence:** final Pytest **4 passed, 2 warnings (1.24s)**; manual API rejected both elevated roles with HTTP 422; student registration, login, `/me` passed; `npx.cmd tsc --noEmit` and `npm.cmd run build` passed. Lint failed **12 errors/2 warnings** that were pre-existing; don't state lint passed. npm audit had **26 reported vulnerabilities**, untriaged.
5. **Docker test infra:** `unify-auth-test-net`, `unify-auth-test-db` and `unify-auth-test-api` are user-local resources; verify their state rather than assuming they're still running. API uses localhost port **8001**, bind-mounts updated `backend` at `/app` read-only and connects to `unify_auth_test`. Pytest uses separate database `unify_auth_pytest` in the same ephemeral Postgres container. Persistent volume `unify_db_data` must not be removed.
6. **Commit documentation and prepare PR:** security commit `9239fda` already exists. Stage only `HANDOFF.md`, review and commit with `git commit -m "docs: add Unify 2.0 engineering handoff"`. Then push `git push -u origin fix/registration-role-escalation`; open PR describing exploit, policy, tests, warnings and follow-ups. Do not claim push or PR completion until verified.
7. **Review and merge deliberately:** inspect PR diff and checks, recognize that pre-existing ESLint errors currently block a green lint gate, and decide how to track/fix baseline lint appropriately without concealing the failure. On merge, verify `main` and update this ledger with commit/PR details.
8. **Clean up only disposable resources after no longer needed:** stopping/removing `unify-auth-test-api` and `unify-auth-test-db` is acceptable when explicitly no longer needed; do **not** run `docker compose down -v`, `docker volume rm unify_db_data`, drop production/dev schemas, or destructive Git commands.
9. **Next separate bug:** F1.2 private event visibility and unauthenticated RSVP-count leakage, with an explicit role/ownership matrix and regression tests. Then F1.3 unauthorized RSVP `checked_in` status, followed by SQL/ORM/Alembic work. No agents or `AGENTS.md`.

**Quick continuation request:** "We are on `fix/registration-role-escalation`, with local F1.1 security commit `9239fda` based on `main` at `7411d45`. F1.1 is implemented, tested, and committed locally, but documentation commit, push and PR remain. Read `HANDOFF.md` Sections 8–9 and verify current Git state. Finish handoff review/commit and PR; preserve `unify_db_data`; do not claim lint passed. Then tackle F1.2 in a separate branch."

---

## 10. HOW A FUTURE ASSISTANT/DEVELOPER SHOULD HANDLE AMBIGUITY AND FAILURES

- **If this handoff and repository disagree:** Treat current source/DB/Git/test output as authoritative. Record discrepancy, determine whether code changed after snapshot, and update handoff. Never overwrite a newer implementation using an older plan.
- **If setup fails:** Capture environment, exact command, error, and minimal reproducible fix. Investigate Compose networking, startup readiness, SQL/ORM mismatch, dependency versions, then continue. Don't mark the stage completed just because the syntax compiles.
- **If a security fix changes UX:** Explain impact; adjust error messages/routes as an intentional, tested part of the same feature; avoid hiding server errors.
- **If migration threatens data:** Stop and request approval; back up and test on a clone. Do not use `drop_all`, `DROP TABLE`, `down -v`, force resets, or casual Alembic stamp in valuable environments.
- **If concurrency test is flaky:** Investigate locks/isolation/fixtures and reproducibility; don't weaken the assertion to make CI green. Verify using PostgreSQL not SQLite.
- **If tests are unavailable:** Explicitly state unverified; implement only appropriately bounded work, and prioritize building the necessary fixture/test environment.
- **If a tool/framework seems attractive:** Ask what concrete failure it solves and what complexity it adds; defer optional infrastructure.
- **If deadlines arrive:** Prioritize a secure, coherent, working deployed release, and label unfinished future work plainly.
- **If conversation ends mid-change:** Record active branch, last modified files, commands/tests, uncommitted work, blockers, and single next action in the ledger. Never claim a commit or merge occurred unless verified.
- **Mentorship expectation:** For each major change, explain what the user is learning, what alternatives exist, which concept is interview-relevant, and how the tests demonstrate actual behavior.

---

## 11. Reference inventory and attribution

1. **`Unify.zip` — canonical newly re-audited baseline (2026-10-11):** Includes Git metadata; archived `main` and `origin/main` at `7411d451dec5c33413c1bbebb26b2b361863037d`, one imported/migration commit; 72 tracked files. Archive extraction yields false `M` changes for 67 files due solely to CRLF. **Do not misreport as 67 code changes.** Live remote/current checkout still require verification.
2. **`Unify-main.zip` — earlier source archive:** 72 files, no `.git`; **all 72 identical to current snapshot after CRLF normalization**. Earlier code audit and PDF findings remain applicable.
3. **`Unify Project Improvements.pdf`** — 11-page strategic audit and internship-focused feature recommendations; used extensively in this handoff. Its images include a source architecture diagram, RSVP concurrency flow, development roadmap, and design references; illustrative UI images are **not existing Unify screenshots**.
4. **`Unify_2_0_Master_Engineering_Roadmap.md`** — previous consolidated planning document. Recommended committed location `docs/ROADMAP.md`; its older phases have been reorganized here into the user's six feature-oriented stages without discarding their requirements.
5. **Planning conversations** — original end-to-end code audit; production-grade upgrades; branching strategy; testing/security/portfolio principles; decision to use an ongoing `HANDOFF.md` and **not** rely on an agents file.

**Authenticity warning:** The PDF references internship companies, role expectations, and pre-existing résumé figures; those references inform portfolio priorities but do **not** verify those companies' current postings, your current résumé, actual application outcomes, or numerical performance claims. Preserve the PDF's warning: measure before you claim.

---

### Final operational instruction

**The plan is ambitious; the implementation must be disciplined.** **Never confuse an archived Git snapshot with a verified live remote; never commit CRLF-only changes caused by exporting the ZIP.** Finish the next smallest verified security fix, preserve data, keep the stable branch healthy, write down the evidence, and update this handoff. Build toward a product that is not only impressive in screenshots, but demonstrably secure, transaction-safe, tested, deployed, and explainable in an interview.
