#!/usr/bin/env python3
"""
Script to improve ranking coverage by ensuring proper selection stage tracking
"""

import json
import os
from pathlib import Path


def improve_ranking_coverage():
    """Improve ranking coverage by fixing data structure issues."""
    print("🔧 Improving Ranking Coverage")
    print("=" * 40)

    # Find the most recent quote analysis JSON file
    outputs_dir = Path("Outputs")
    if not outputs_dir.exists():
        print("❌ Outputs directory not found")
        return

    json_files = list(outputs_dir.glob("*.json"))
    if not json_files:
        print("❌ No JSON files found in Outputs directory")
        return

    # Get the most recent file
    latest_file = max(json_files, key=lambda f: f.stat().st_mtime)
    print(f"📁 Processing: {latest_file.name}")

    # Load the data
    try:
        with open(latest_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Error loading file: {e}")
        return

    print(
        f"✅ Loaded data with {data.get('metadata', {}).get('total_quotes', 0)} quotes"
    )

    # Check current structure
    perspectives = data.get("perspectives", {})
    print(f"🎯 Found {len(perspectives)} perspectives")

    # Improve each perspective
    total_ranked_quotes = 0
    selection_stage_breakdown = {}

    for perspective_key, perspective_data in perspectives.items():
        print(
            f"\n🔍 Processing perspective: {perspective_data.get('title', perspective_key)}"
        )

        # Check if ranked_quotes exists
        if "ranked_quotes" not in perspective_data:
            print(f"   ⚠️  Missing ranked_quotes field")

            # Create ranked_quotes from themes
            ranked_quotes = []
            if "themes" in perspective_data:
                for theme in perspective_data["themes"]:
                    if "quotes" in theme:
                        for quote in theme["quotes"]:
                            # Ensure quote has proper selection stage
                            if not quote.get("selection_stage"):
                                if quote.get("openai_rank") or quote.get(
                                    "relevance_score"
                                ):
                                    quote["selection_stage"] = "openai_ranked"
                                else:
                                    quote["selection_stage"] = "theme_selected"

                            # Add to ranked_quotes
                            ranked_quotes.append(quote)

                            # Count for statistics
                            stage = quote.get("selection_stage", "unknown")
                            selection_stage_breakdown[stage] = (
                                selection_stage_breakdown.get(stage, 0) + 1
                            )
                            total_ranked_quotes += 1

            # Add ranked_quotes field
            perspective_data["ranked_quotes"] = ranked_quotes
            print(f"   ✅ Created ranked_quotes with {len(ranked_quotes)} quotes")
        else:
            print(
                f"   ✅ Has ranked_quotes: {len(perspective_data['ranked_quotes'])} quotes"
            )
            # Count existing ranked quotes
            for quote in perspective_data["ranked_quotes"]:
                stage = quote.get("selection_stage", "unknown")
                selection_stage_breakdown[stage] = (
                    selection_stage_breakdown.get(stage, 0) + 1
                )
                total_ranked_quotes += 1

        # Ensure all quotes in themes have selection stages
        if "themes" in perspective_data:
            for theme in perspective_data["themes"]:
                if "quotes" in theme:
                    for quote in theme["quotes"]:
                        if not quote.get("selection_stage"):
                            if quote.get("openai_rank") or quote.get("relevance_score"):
                                quote["selection_stage"] = "openai_ranked"
                            else:
                                quote["selection_stage"] = "theme_selected"

    # Calculate improved ranking coverage
    total_quotes = data.get("metadata", {}).get("total_quotes", 0)
    ranking_coverage = (
        (total_ranked_quotes / total_quotes * 100) if total_quotes > 0 else 0.0
    )

    print(f"\n📊 Improved Ranking Statistics:")
    print(f"   Total Quotes: {total_quotes}")
    print(f"   Total Ranked Quotes: {total_ranked_quotes}")
    print(f"   Ranking Coverage: {ranking_coverage:.1f}%")

    if selection_stage_breakdown:
        print(f"   Selection Stage Breakdown:")
        for stage, count in selection_stage_breakdown.items():
            print(f"     {stage}: {count} quotes")

    # Save improved data
    output_file = latest_file.parent / f"improved_{latest_file.name}"
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Saved improved data to: {output_file.name}")
    except Exception as e:
        print(f"❌ Error saving improved data: {e}")

    return ranking_coverage


if __name__ == "__main__":
    coverage = improve_ranking_coverage()
    if coverage > 0:
        print(f"\n🎉 Ranking coverage improved to {coverage:.1f}%")
    else:
        print(f"\n⚠️  No improvement in ranking coverage")
