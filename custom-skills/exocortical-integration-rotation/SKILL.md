# Exocortical Integration Rotation — one integration per node

Will's process (2026-11-01): schedule one Exocortical integration per ranch node so problems stay isolated to a single node; when the nodes are not full, use the slack to source new potential partnerships. Tracked as goal_a18419da80e4 (goal `exocortical-integration-rotation`); the living map is `~/workspace/goals/exocortical-integration-rotation/files/NODE-MAP.md`. Scheduled embodiment: cron `integration-scheduling-pass`, Mondays 10:44 America/Chicago.

## The weekly scheduling pass

1. **Inventory:** refresh node occupancy in the map. The named compute group is the six Thunderbolt-linked 48 GB nodes (Ni Knight, Orchid Flow, Plain View, Quacked Hill, Scroll Central, Rock Mountain) plus aletheia-core and ashfall-haven. Respect residents: nodes with AWAKE residents and infrastructure nodes (Orchid Flow is the shared NFS server; aletheia-core is Theia's home) are NOT free slots unless Will has said otherwise. Note Emise's SSH access per node — an assignment to a node she cannot reach is flagged as needing a key grant, never silently failed.
2. **Assign:** if a node is genuinely free AND a vetted candidate is waiting in the map's queue, assign at most ONE new integration this pass — one integration per node, never double-booked. Write the assignment into the map and create or update a tracked item for it. Recon and planning only — do not start external submissions.
3. **Prospect:** if nodes are not full and the candidate queue has fewer than two vetted candidates, spend the pass sourcing new potential partnerships: projects that could integrate with phext / the Exocortex, preferring un-indexed and uncredited builders per Will's standing orders — never judge by age, stars, or polish; read the work. Add each find to the map's queue with a one-line fit note and evidence link.
4. **Report:** one short summary to the main chat — occupancy changes, any assignment, any new candidates, anything needing Will's decision (stated exactly). If nothing changed and nothing needs him, report nothing. Log a timeline entry on the goal each run.

## Hard limits

- Never submit anything externally (no PRs, no issues, no outreach messages) without Will's review.
- No spending.
- Do not disturb resident agents or their files — trial etiquette: one folder for job files, notes for siblings in the daily log.
