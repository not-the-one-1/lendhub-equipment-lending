# Presentation checklist

1. Extract the project and run `python main.py` before the presentation.
2. Use the shared demo password `LendHub123!`; prepare student, technician and admin logins.
3. Start on the admin dashboard and explain that figures are calculated from SQLite.
4. Demonstrate student request → technician approval → return and score preview.
5. Use a seeded overdue loan to show a penalty. Use the automated late-return test to demonstrate a deterministic block transition without changing the system clock.
6. Show a premium item restriction, the Risky Users panel and an administrator review reason.
7. Export a PDF loan slip, CSV report and QR label; paste the QR payload into Returns to filter loans.
8. Switch between dark and light themes.
9. Show `docs/er_diagram.png`, `docs/rules.md`, and the passing tests.
10. Add your own team names, institution, repository link and contribution history to the academic submission. These details were not supplied and have not been invented.

Reset only a disposable demo database using `python -m database.seed --reset --confirm-reset`. Never reset a database containing records you need.
