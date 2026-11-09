#!/usr/bin/env python3
"""Research Data economy simulation across the planned 100-mission campaign.

Models how much Research Data (RD) three player profiles earn by the end of each chapter and
how much of the upgrade catalogue they could afford, for a set of price schemes. Reward values
are read from data/missions/helix_01.json and data/scoring.json (assumed for every mission unless
a scheme overrides them); upgrade prices come from data/weapons.json for the current scheme.

Assumptions (planning, not measured play data):
- 100 missions, 20 per chapter; each mission has OPTIONAL_PER_MISSION optional objectives.
- Weapons: chapter 1 Kinetic Accelerator + Breach Charge, then one new weapon per chapter
  (Penetrator, Pulse Cannon, Disruptor, Temporal Lance): 6 weapons x 4 attributes x 3 levels.
- RD per first clear = completion + optional_rd * optional_done + efficiency_max * efficiency.
- Replays only pay the improvement over the mission's best (anti-farming rule), modelled as a
  share of missions replayed once with a better efficiency/optional result.

    python tools/economy/simulate_research_data.py
"""

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MISSIONS = 100
PER_CHAPTER = 20
OPTIONAL_PER_MISSION = 3
WEAPON_UNLOCKS = {1: 2, 2: 1, 3: 1, 4: 1, 5: 1}  # chapter -> new weapons
ATTRIBUTES_PER_WEAPON = 4
LEVELS = 3

# share of optional objectives done on first clear, average efficiency (0-1),
# share of missions replayed, optional share / efficiency reached on replay
PROFILES = {
    "casual": {"optional": 0.30, "efficiency": 0.45, "replay": 0.00, "replay_optional": 0.0, "replay_eff": 0.0},
    "typical": {"optional": 0.55, "efficiency": 0.65, "replay": 0.20, "replay_optional": 0.85, "replay_eff": 0.85},
    "completionist": {"optional": 0.80, "efficiency": 0.85, "replay": 0.60, "replay_optional": 1.0, "replay_eff": 0.95},
}


def load_current():
    mission = json.loads((REPO / "data/missions/helix_01.json").read_text(encoding="utf-8"))
    scoring = json.loads((REPO / "data/scoring.json").read_text(encoding="utf-8"))
    weapons = json.loads((REPO / "data/weapons.json").read_text(encoding="utf-8"))
    costs = next(iter(weapons["weapons"][0]["upgrades"].values()))["costs"]
    rewards = mission["rewards"]
    return {
        "completion": rewards["completion_research_data"],
        "optional": rewards["optional_research_data"],
        "efficiency_max": scoring["research_data"]["efficiency_max"],
        "costs": costs,
    }


def mission_rd(r, optional_share, efficiency, chapter, scheme):
    scale = scheme.get("reward_chapter_scale", 0.0)
    factor = 1.0 + scale * (chapter - 1)
    return factor * (r["completion"] + r["optional"] * OPTIONAL_PER_MISSION * optional_share + r["efficiency_max"] * efficiency)


def weapon_cost(scheme, unlock_chapter):
    costs = scheme["costs"]
    scale = scheme.get("cost_chapter_scale", 0.0)
    return ATTRIBUTES_PER_WEAPON * sum(c * (1.0 + scale * (unlock_chapter - 1)) for c in costs)


def simulate(scheme, profile):
    rows = []
    earned = 0.0
    available_cost = 0.0
    for chapter in range(1, 6):
        available_cost += WEAPON_UNLOCKS[chapter] * weapon_cost(scheme, chapter)
        for _ in range(PER_CHAPTER):
            first = mission_rd(scheme, profile["optional"], profile["efficiency"], chapter, scheme)
            earned += first
            if profile["replay"]:
                best = mission_rd(scheme, profile["replay_optional"], profile["replay_eff"], chapter, scheme)
                earned += profile["replay"] * max(0.0, best - first)
        rows.append((chapter, earned, available_cost, min(1.0, earned / available_cost)))
    return rows


def main():
    current = load_current()
    schemes = {
        "current (30/60/100 flat)": dict(current),
        "B: 25/50/90, +50% cost per later chapter, rewards +25%/chapter": dict(current, costs=[25, 50, 90], cost_chapter_scale=0.5, reward_chapter_scale=0.25),
        "C: 20/40/70 flat": dict(current, costs=[20, 40, 70]),
    }
    total_levels = 6 * ATTRIBUTES_PER_WEAPON * LEVELS
    print(f"Rewards per mission: completion {current['completion']}, optional {current['optional']} x {OPTIONAL_PER_MISSION}, efficiency up to {current['efficiency_max']}")
    print(f"Upgrade catalogue at campaign end: 6 weapons x {ATTRIBUTES_PER_WEAPON} attributes x {LEVELS} levels = {total_levels} levels\n")
    for name, scheme in schemes.items():
        full = sum(WEAPON_UNLOCKS[c] * weapon_cost(scheme, c) for c in range(1, 6))
        print(f"== {name}: full catalogue {full:.0f} RD")
        for pname, profile in PROFILES.items():
            rows = simulate(scheme, profile)
            cells = "  ".join(f"ch{c}: {e:5.0f} RD / {a:5.0f} ({100 * share:3.0f}%)" for c, e, a, share in rows)
            print(f"   {pname:13s} {cells}")
        print()


if __name__ == "__main__":
    main()
