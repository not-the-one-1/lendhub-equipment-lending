# LendHub

A complete local campus equipment lending app, built with **Python, Tkinter and SQLite**. The dark navy interface follows the supplied reference, with a blue accent, equipment cards, trust badges, dashboards, and a light theme.

## Start the app

Requires **Python 3.10 or newer with Tkinter**. No pip packages are needed.

On Windows, extract the entire project and double-click **Start LendHub.cmd**. Or run:

```console
python main.py
```

If Windows cannot find `py`, run `python main.py` in the project folder. On Debian/Ubuntu, install `python3-tk` if Tkinter is missing.

The first launch creates `data/lendhub.db` and fictional demo data: **20 accounts (18 students, one technician, one admin), 40 equipment types, 192 physical units, and 60 loans**. Existing data is preserved on subsequent launches. Initial figures are 12 active loans, 4 overdue, 6 pending, 40 returned and 2 refused. One damaged unit is in maintenance and one is lost.

### Demo sign-ins

| Role | Email | Password |
|---|---|---|
| Administrator | admin@lendhub.local | LendHub123! |
| Technician | tech@lendhub.local | LendHub123! |
| Student (Ahmed Benali) | student@lendhub.local | LendHub123! |

Other students use `stu002@lendhub.local` through `stu018@lendhub.local` with the same demo password. All records are fictional. The login screen's demo buttons fill the credentials; press **Sign in** to enter.

## What works

- Role-based login and navigation; PBKDF2-HMAC-SHA256 salted passwords; password change and sign-out.
- Dashboard with real inventory counts, overdue totals, risk totals, monthly borrowing, top equipment and recent returns.
- Responsive catalogue cards, live text search, category and availability filters, and premium-access indicators.
- Student home with trust gauge, lending allowance, blocked/overdue/due-soon guidance; loan history, cancellation of pending requests and PDF slips.
- Technician/admin approval queue, refusal reasons, return desk, score preview and collection/return tracking.
- Automatic promotions/demotions, late/damage/loss penalties, expiring temporary blocks and administrator review for blacklisted accounts.
- Student creation/editing and administrator block/unblock/privilege decisions with required reasons and a stored audit trail.
- Equipment creation/editing, stock checks, repair processing, atomic CSV import and CSV reports.
- Printable QR labels. Scan with a keyboard-style QR scanner into the return desk search box, or paste the decoded `lendhub:equipment:ID` value. No camera scanner is included.
- Persistent dark/light preference, reusable dialogs, confirmations, empty states, scrollable pages and toast notifications. Exports/imports run in a background worker.

## Demonstrate the full flow

1. Sign in as the student. Open **Borrow Equipment**, select the Scientific Calculator and request 7 days.
2. Sign out and sign in as the technician. Open **Approvals**, select the request and approve it. The due date starts on approval and stock decreases by one.
3. In **Returns**, select the loan. Compare good/damaged/lost conditions; the score change is shown before confirmation. A good, on-time return earns +2.
4. Return one of the seeded overdue loans to demonstrate late penalties. Sara (`STU008`) and Ines (`STU015`) demonstrate temporary-block and blacklist states.
5. Sign in as the admin, open **Risky Users**, then a profile. Unblock or cap privileges with a reason; the review appears in the profile audit history.
6. Export a loan slip, report or QR label. Switch the theme from **Settings**.

Exact rules and boundary behavior are in [docs/rules.md](docs/rules.md). Seeded historical scores are illustrative snapshots; live returns calculate scores transactionally.

## Run the checks

```console
python -m unittest discover -s tests -v
python tests/ui_smoke.py
```

The automated suite covers authentication, role restrictions, trust boundaries, block expiry, on-time/late/damage/loss returns, double returns, pending limits, concurrent approvals, stock invariants, CSV rollback and export permissions. The GUI smoke test renders every permitted page and dialog across all roles and both themes in a separate temporary database. It opens and closes windows and does not modify your app database.

## Reset / separate databases

Back up the database before resetting a demo. Reset deletes its current records:

```console
python -m database.seed --reset --confirm-reset
```

Use a separate database without touching the default:

```console
python main.py --db data/another-demo.db
```

To back up real work, close the app and copy `data/lendhub.db`. The database and theme preferences are ignored by Git.

## CSV format

Required columns: `code,name,category,total`. Optional: `premium,description`.

```csv
code,name,category,total,premium,description
E100,Tripod,Accessory,4,0,Tripod with carry bag
E101,Sony Camera,Camera,2,1,Premium camera kit
```

Import adds new codes. Duplicate or invalid rows roll back the entire file. Use **Edit selected** for updates. Exported text that could be interpreted as a spreadsheet formula is escaped.

## Architecture

```text
main.py                     Entry point and safe demo initialization
config/                     Paths, palette defaults and centralized policy
database/schema.sql         Exactly three tables and integrity constraints
database/repositories/      SQL queries for users, equipment and loans
services/                   Authentication, loans, trust, inventory, stats, exports
ui/app.py                   Window, navigation and service composition
ui/components/              Cards, tables, charts, gauges, dialogs and toasts
ui/pages/                   The role-specific screens
tests/                      Service/integration tests and GUI smoke checks
docs/                       Rules, ER diagram, screenshots and handover notes
assets/qr/                  Generated labels may be stored here; ignored by Git
data/                       Local database and preferences; ignored by Git
```

The UI calls services, services call repositories, and repositories contain SQL. All stock-changing operations run under `BEGIN IMMEDIATE`, so checking stock and reserving/returning it is atomic. Damaged and lost units remain part of total inventory but are not available to lend.

## Design choices and limits

- This is an offline, single-computer academic project, not a hosted multi-user service. App role checks do not prevent the computer's owner from editing the SQLite file directly.
- Every request requires technician/admin approval. Pending requests count toward a student's limit but do not reserve inventory. Approval rechecks current stock and rules.
- Records are kept for loan history. There is no destructive delete-account or delete-equipment operation.
- Privilege overrides are caps; administrators cannot use them to bypass a low score or active block.
- PDF slips use a built-in Latin font for English/French names. QR labels encode an equipment ID, not a public web URL.
- Dates use the computer's local date. Keep the computer clock correct. No notification service, camera scanning, email delivery or cloud sync is included.
- The tiny built-in QR encoder uses version 2-L, mask 0 and a 32-byte ASCII limit; the generated equipment IDs stay within it.
- `database/maindb.py` and `ui/pages/borrow_equippment.py` are compatibility entry points from the original prototype. Active implementation lives in the organized modules above.

The supplied schedule and teamwork suggestions are planning context. This delivery does not fabricate team contributions, Git history, repository settings, or a submission to your professor.
