# Support Priority Matrix

An interactive version of the "Priority = Scope × Criticality" framework for
software support requests. Click a cell (or pick scope + tier + modifiers) to
see the priority and the reasoning behind it, so you can sanity-check whether
a ticket is sitting in the right place.

## Run

```bash
pip install -r requirements.txt
python app.py
```

Then open http://127.0.0.1:5000

## Customise

All content lives at the top of `app.py`:

- `SCOPES` / `TIERS` — the two axes, with examples and explanations
- `GRID` — the priority for each scope × tier combination
- `REASONS` — the explanation shown for each cell
- `MODIFIERS` — context adjustments (capped at one step each)
- `PRIORITIES` — response targets per priority

There is also a JSON endpoint: `/api/score?scope=school&tier=t3&mods=deadline`
