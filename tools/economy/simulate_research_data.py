#!/usr/bin/env python3
"""Research Data economy simulation across the planned 100-mission campaign.

Models how much Research Data (RD) three player profiles earn by the end of each chapter and
how much of the upgrade catalogue they could afford, for each price scheme. The model is fully
deterministic: the same inputs always print the same table.

Inputs:
- tools/economy/economy_assumptions.json: campaign shape, unlock schedule, player profiles,
  candidate schemes and target affordability (planning assumptions, not measured play data).
- data/missions/helix_01.json and data/scoring.json: per-mission rewards (assumed for every
  mission unless a scheme scales them per chapter).
- data/weapons.json: upgrade prices for the "current" scheme.

Model:
- RD per first clear = completion + optional_rd * optional_done + efficiency_max * efficiency,
  times (1 + reward_chapter_scale * (chapter - 1)).
- Replays only pay the improvement over the mission's best (anti-farming rule), modelled as a
  share of missions replayed once with a better optional/efficiency result.
- A weapon unlocked in chapter c costs attributes * sum(costs) * (1 + cost_chapter_scale * (c - 1)).
- "Affordable" = RD earned so far / cost of every upgrade unlocked so far (capped at 100%).

    python tools/economy/simulate_research_data.py [--scheme ID]
"""

import argparse
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ASSUMPTIONS = REPO / "tools/economy/economy_assumptions.json"


def read_json(relative):
    return json.loads((REPO / relative).read_text(encoding="utf-8"))


def live_rewards():
    mission = read_json("data/missions/helix_01.json")
    scoring = read_json("data/scoring.json")
    weapons = read_json("data/weapons.json")
    costs = next(iter(weapons["weapons"][0]["upgrades"].values()))["costs"]
    rewards = mission["rewards"]
    return {
        "completion": rewards["completion_research_data"],
        "optional": rewards["optional_research_data"],
        "efficiency_max": scoring["research_data"]["efficiency_max"],
        "costs": costs,
    }


def mission_rd(model, scheme, optional_share, efficiency, chapter):
    factor = 1.0 + scheme.get("reward_chapter_scale", 0.0) * (chapter - 1)
    return factor * (model["completion"] + model["optional"] * model["optional_per_mission"] * optional_share
                     + model["efficiency_max"] * efficiency)


def weapon_cost(model, scheme, unlock_chapter):
    scale = 1.0 + scheme.get("cost_chapter_scale", 0.0) * (unlock_chapter - 1)
    return model["attributes"] * sum(c * scale for c in scheme["costs"])


def simulate(model, scheme, profile):
    rows = []
    earned = 0.0
    available = 0.0
    chapters = model["missions"] // model["per_chapter"]
    for chapter in range(1, chapters + 1):
        available += model["unlocks"].get(chapter, 0) * weapon_cost(model, scheme, chapter)
        for _ in range(model["per_chapter"]):
            first = mission_rd(model, scheme, profile["optional"], profile["efficiency"], chapter)
            earned += first
            if profile["replay"]:
                best = mission_rd(model, scheme, profile["replay_optional"], profile["replay_efficiency"], chapter)
                earned += profile["replay"] * max(0.0, best - first)
        rows.append((chapter, earned, available, min(1.0, earned / available) if available else 1.0))
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--scheme", help="only this scheme id")
    args = parser.parse_args()
    assumptions = json.loads(ASSUMPTIONS.read_text(encoding="utf-8"))
    live = live_rewards()
    model = dict(live, optional_per_mission=assumptions["optional_objectives_per_mission"],
                 missions=assumptions["missions"], per_chapter=assumptions["missions_per_chapter"],
                 unlocks={int(k): v for k, v in assumptions["weapon_unlocks_by_chapter"].items()},
                 attributes=assumptions["attributes_per_weapon"])
    weapons = sum(model["unlocks"].values())
    levels = weapons * model["attributes"] * assumptions["levels_per_attribute"]
    print(f"Rewards per mission: completion {live['completion']}, optional {live['optional']} x {model['optional_per_mission']}, efficiency up to {live['efficiency_max']}")
    print(f"Upgrade catalogue at campaign end: {weapons} weapons x {model['attributes']} attributes x {assumptions['levels_per_attribute']} levels = {levels} levels")
    print(f"Target affordability at campaign end: {assumptions['target_affordability_at_campaign_end']}\n")
    for scheme in assumptions["schemes"]:
        if args.scheme and scheme["id"] != args.scheme:
            continue
        scheme = dict(scheme)
        scheme.setdefault("costs", live["costs"])
        full = sum(model["unlocks"].get(c, 0) * weapon_cost(model, scheme, c) for c in model["unlocks"])
        print(f"== {scheme['id']}: {scheme['label']} (costs {scheme['costs']}; full catalogue {full:.0f} RD)")
        for name, profile in assumptions["profiles"].items():
            rows = simulate(model, scheme, profile)
            cells = "  ".join(f"ch{c}: {e:5.0f} / {a:5.0f} ({100 * share:3.0f}%)" for c, e, a, share in rows)
            print(f"   {name:13s} {cells}")
        print()


if __name__ == "__main__":
    main()
