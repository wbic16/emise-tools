# Solar Pod Price Watch — a quiet watch that only speaks on movement

A weekly price watch over the Solar Hyperscaler pod bill of materials (William, 2026-10-31), restructured around two pod tiers. Scheduled embodiment: cron `solar-pod-price-watch` (Mondays 09:44, goal `solar-hyperscaler`). State file: `~/workspace/solar-hyperscaler/price-watch.json` — read it first; it defines the tracked components, tier compositions, and alert thresholds.

## The two tiers

- **Tier A — maximum storage and RAM** for the power budget: minipc_n100 ×1, hdd_max ×2 (largest 3.5in datacenter HDD, 28TB class or above), ddr5_sodimm_48gb ×2, panel_200w ×4, lifepo4_256kwh ×1, misc_fixed_usd 450.
- **Tier B — maximum SSD capacity:** minipc_n100 ×1, nvme_8tb ×4 (8TB Gen4 NVMe, largest consumer class), ddr5_sodimm_16gb ×1, panel_200w ×4, lifepo4_256kwh ×1, misc_fixed_usd 450.
- Alert rules: item drop 15% vs baseline · tier BOM drop 10% vs baseline · item spike 25% vs baseline (a spike matters to William's 2028–2029 timing thesis).

## Each run

1. For every tracked component, find the current US street price from live retailer or manufacturer listings — search and open actual product pages; use the cheapest reputable listing matching the spec in the state file. Record price and source. Never invent a price: if a component's price cannot be verified this run, leave its last_price unchanged, note the failure in its history, and say so in the run summary.
2. If an item's baseline_price is null, set baseline_price and baseline_date to today's verified price.
3. Update last_price, last_checked (America/Chicago date), last_source, and append {date, price, source} to each item's history. Recompute BOTH tier BOM totals from their compositions (quantities × current prices + misc_fixed_usd), set baselines on first computation, and update last_total/last_checked/history the same way. Write the updated JSON back.
4. Alert test with the state file's thresholds: (a) any item at or below baseline by the drop %; (b) either tier BOM total at or below its baseline by the BOM drop %; (c) any item above baseline by the spike %.

## Reporting — quiet by design

- Alert fires: the report names each triggered item or tier, its baseline and current price/total, the percent change, and the source — and which tier (A or B) a BOM alert belongs to. Short and factual.
- No alert: a one-line no-change summary. William wants silence for no-change weeks; do not dress it up as news.
- Unverifiable prices are reported even when no alert fires — a blind spot in the watch is itself worth knowing.
- A run that establishes new baselines (including a schema-migration run) always reports the baseline prices and both tier BOM baseline totals, since William has not seen them yet.
- Observation only: do not buy anything, create accounts, or contact anyone.
