# Verification record

Verified on 28 October 2026 with Python 3.13 / Tk 8.6 on Windows.

| Check | Outcome |
|---|---|
| `python -m unittest discover -s tests -v` | 40 tests passed |
| `python tests/ui_smoke.py` | 56 page/dialog checks passed, all roles, dark and light themes |
| Escape key in dialogs | Included in the GUI smoke checks |
| Simultaneous approvals for one available unit | Exactly one succeeds; inventory remains consistent |
| Independent QR decoding | OpenCV decoded `lendhub:equipment:123` correctly |
| PDF structure | Sample loan slip parsed successfully with pypdf |
| PDF visual review | Sample slip and all 8 handover-report pages rendered and inspected |
| Windows visual review | Dashboard, catalogue, student home, technician returns, login and return-condition previews inspected |
| Layer boundaries | No Tkinter imports in services; no SQL calls in UI |
| Python source syntax | All sources parsed successfully |

The tests use temporary databases. Native screenshots were captured against a separate fictional preview database. They do not represent real students or production transactions.

Dependencies used only for independent verification (OpenCV, pypdf, Pillow, ReportLab and Poppler) are not needed to run the application or its supplied test suite.
