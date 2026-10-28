# Shared lending and trust rules

The executable source of truth is `config/rules.py`. Scores are integers clamped to 0–100. New student accounts start at 85.

## Privileges

| Effective privilege | Open loans + pending requests | Maximum duration | Premium equipment |
|---|---:|---:|---|
| Restricted | 1 | 7 days | No |
| Standard | 3 | 14 days | No |
| Trusted | 5 | 21 days | Yes |

| Trust score | Trust band | Automatic privilege | Sanction |
|---|---|---|---|
| 80–100 | Excellent | Trusted | None |
| 60–79 | Warning | Standard | No premium equipment |
| 40–59 | Demoted | Restricted | One loan at a time |
| 20–39 | Temporary block | Restricted | Borrowing blocked for 14 days after a negative return |
| 0–19 | Blacklist | Restricted | Administrator review required |

The temporary block is active while `today < blocked_until`. On the expiry date, borrowing is allowed at restricted limits, provided there is no overdue loan or permanent block. Expiry does not grant score points. A later negative return below 40 starts a new 14-day block. Existing sanctions are not removed early by a positive return.

An administrator may block a student until review regardless of score. Unblocking requires a reason, clears sanctions, and raises scores below 40 to 40 so the student can restart with restricted borrowing. A privilege override sets a maximum, never a minimum; the effective level is the lower of the score-derived level and the administrator's cap. Selecting Automatic removes the cap. All such decisions store the actor, date, reason, value, and before/after scores in the user's audit history.

## Returns

| Event | Score change | Inventory effect |
|---|---:|---|
| Good condition, on or before due date | +2 | One unit becomes available |
| Late, good condition | -5 per calendar day, maximum -60 | One unit becomes available |
| Damaged | -25 plus any late penalty | One unit enters maintenance |
| Lost | -60 plus any late penalty | One unit enters lost stock |

No on-time reward is added for damaged/lost equipment. The displayed score delta is the actual change after clamping, so returning at score 99 earns +1, and a penalty cannot reduce a score below zero. One repaired maintenance unit can be returned to available stock by a technician or admin. Lost units are retained for accounting; replacing one means increasing the total quantity through the inventory editor.

## Loan lifecycle

`pending → active → returned`, or `pending → rejected/cancelled`.

- Only students can be borrowers; staff can submit requests on their behalf.
- Students may read/cancel only their own requests. Only pending requests may be cancelled or refused. Refusal needs a reason.
- Request and approval both check student role, sanctions, duration, effective privileges, open loan count, overdue loans, premium access and equipment availability.
- Pending requests consume allowance but do not reserve stock.
- Approval begins the loan on the current local date and sets `due_date = approval_date + duration_days`.
- Approval and return are serialized SQLite transactions. A second approval cannot take the last unit, and a second return cannot add stock or score again.
- Equipment remains unavailable while damaged or lost. The invariant is `total = available + active loans + maintenance + lost`.
- Existing loans are never silently removed after demotion. The student must return or cancel enough open records before borrowing again.
- Dates are calendar dates, not hours. Due today is on time. Existing overdue loans prevent further borrowing.

## Data design

Exactly three application tables: `Utilisateurs`, `Equipements`, `Emprunts`. Foreign keys prevent dangling records. CHECK constraints restrict roles, statuses, scores, quantities and valid returned-loan data. Emails are unique without case sensitivity. The user audit history is a JSON column to preserve the three-table requirement; a separate event table would be preferable in a larger system.
