"""
Monthly price calculator for Microsoft Voice Live API
for Contact Center scenarios.

Available tiers (based on the chosen generative AI model):
  - Voice Live Pro:      gpt-realtime, gpt-4o, gpt-4.1, gpt-5, gpt-5-chat
  - Voice Live Standard: gpt-realtime-mini, gpt-4o-mini, gpt-4.1-mini, gpt-5-mini
  - Voice Live Lite:     gpt-5-nano, phi4-mm-realtime, phi4-mini
  - Voice Live BYO:      Bring your own model (standard/custom audio only)

Billing per million tokens (M tokens).
Token estimation per second of audio (from official docs):
  - Azure OpenAI models: ~10 tokens/sec input, ~20 tokens/sec output
  - Phi models:           ~12.5 tokens/sec input, ~20 tokens/sec output

NOTE: Prices shown are public reference prices (Azure OpenAI Realtime).
      Verify updated prices at:
      https://azure.microsoft.com/pricing/details/cognitive-services/speech-services/
      (sign-in required to view Voice Live prices)
"""

# ─────────────────────────────────────────────────────────────
# Prices per million tokens (USD) — Update from Azure portal
# Structure: {category: {input, cached_input, output}}
# ─────────────────────────────────────────────────────────────

PRICING = {
    "Pro": {
        "modelos": [
            "gpt-realtime", "gpt-4o", "gpt-4.1",
            "gpt-5", "gpt-5-chat"
        ],
        "token_ratio": {"input_per_sec": 10, "output_per_sec": 20},
        "text": {"input": 5.00, "cached_input": 2.50, "output": 20.00},
        "audio_standard": {"input": 100.00, "cached_input": 20.00, "output": 200.00},
        "audio_custom": {"input": 120.00, "cached_input": 24.00, "output": 240.00},
        "native_realtime": {"input": 100.00, "cached_input": 20.00, "output": 200.00},
    },
    "Standard": {
        "modelos": [
            "gpt-realtime-mini", "gpt-4o-mini",
            "gpt-4.1-mini", "gpt-5-mini"
        ],
        "token_ratio": {"input_per_sec": 10, "output_per_sec": 20},
        "text": {"input": 0.60, "cached_input": 0.30, "output": 2.40},
        "audio_standard": {"input": 10.00, "cached_input": 2.00, "output": 20.00},
        "audio_custom": {"input": 12.00, "cached_input": 2.40, "output": 24.00},
        "native_realtime": {"input": 10.00, "cached_input": 2.00, "output": 20.00},
    },
    "Lite": {
        "modelos": [
            "gpt-5-nano", "phi4-mm-realtime", "phi4-mini"
        ],
        "token_ratio": {"input_per_sec": 12.5, "output_per_sec": 20},
        "text": {"input": 0.30, "cached_input": 0.15, "output": 1.20},
        "audio_standard": {"input": 4.00, "cached_input": 0.80, "output": 8.00},
        "audio_custom": {"input": 4.80, "cached_input": 0.96, "output": 9.60},
        "native_realtime": {"input": 4.00, "cached_input": 0.80, "output": 8.00},
    },
    "BYO": {
        "modelos": ["Your own model (BYOM)"],
        "token_ratio": {"input_per_sec": 10, "output_per_sec": 20},
        "text": None,  # Not included — uses your own model
        "audio_standard": {"input": 1.00, "cached_input": None, "output": 1.50},
        "audio_custom": {"input": 1.20, "cached_input": None, "output": 2.00},
        "native_realtime": None,
    },
}

# Additional separate prices
AVATAR_PRICE_PER_MINUTE = 0.072  # Interactive avatar (real-time) $/min
CUSTOM_VOICE_HOSTING_PER_HOUR = 4.04  # Custom voice endpoint hosting $/hr
CUSTOM_VOICE_TRAINING_PER_HOUR = 52.00  # Custom voice training $/compute hr
STT_CUSTOM_HOSTING_PER_HOUR = 0.0538  # Custom speech endpoint hosting $/hr


def print_header():
    print("=" * 70)
    print("  COST CALCULATOR — Microsoft Voice Live API")
    print("  Scenario: Contact Center")
    print("=" * 70)
    print()
    print("  NOTE: Prices are for reference only. Verify them at:")
    print("  https://azure.microsoft.com/pricing/details/cognitive-services/speech-services/")
    print()


def select_tier() -> str:
    print("─" * 50)
    print("  Select a Voice Live tier:")
    print("─" * 50)
    tiers = list(PRICING.keys())
    for i, tier in enumerate(tiers, 1):
        modelos = ", ".join(PRICING[tier]["modelos"])
        print(f"  {i}. Voice Live {tier}")
        print(f"     Models: {modelos}")
        print()
    while True:
        try:
            choice = int(input("  Option [1-4]: "))
            if 1 <= choice <= len(tiers):
                return tiers[choice - 1]
        except ValueError:
            pass
        print("  ⚠ Invalid option, try again.")


def select_audio_mode(tier: str) -> str:
    print()
    print("─" * 50)
    print("  Audio input/output mode:")
    print("─" * 50)

    options = []
    if tier == "BYO":
        options = [
            ("audio_standard", "Azure Speech standard (STT + TTS)"),
            ("audio_custom", "Azure Speech custom (custom STT + custom TTS)"),
        ]
    else:
        options = [
            ("audio_standard", "Azure Speech standard (STT + prebuilt TTS)"),
            ("audio_custom", "Azure Speech custom (custom STT + custom TTS voice)"),
            ("native_realtime", "Native realtime model audio (gpt-realtime)"),
        ]

    for i, (_, desc) in enumerate(options, 1):
        print(f"  {i}. {desc}")

    while True:
        try:
            choice = int(input(f"\n  Option [1-{len(options)}]: "))
            if 1 <= choice <= len(options):
                return options[choice - 1][0]
        except ValueError:
            pass
        print("  ⚠ Invalid option.")


def ask_yes_no(prompt: str) -> bool:
    while True:
        r = input(f"  {prompt} (y/n): ").strip().lower()
        if r in ("y", "yes", "s", "si"):
            return True
        if r in ("n", "no"):
            return False
        print("  ⚠ Please answer 'y' or 'n'.")


def ask_float(prompt: str, default: float | None = None) -> float:
    while True:
        suffix = f" [{default}]" if default is not None else ""
        raw = input(f"  {prompt}{suffix}: ").strip()
        if not raw and default is not None:
            return default
        try:
            val = float(raw)
            if val >= 0:
                return val
        except ValueError:
            pass
        print("  ⚠ Enter a valid number >= 0.")


def ask_int(prompt: str, default: int | None = None) -> int:
    return int(ask_float(prompt, default))


def get_contact_center_params() -> dict:
    print()
    print("─" * 50)
    print("  Contact Center Parameters:")
    print("─" * 50)
    print()

    agents = ask_int("Number of concurrent AI voice agents", 10)
    calls_per_agent = ask_int("Calls per agent per day", 40)
    avg_duration_min = ask_float("Average call duration (minutes)", 5.0)
    working_days = ask_int("Working days per month", 22)

    print()
    print("  Audio distribution during the call:")
    pct_customer = ask_float("% of time the customer speaks (input)", 50.0)
    pct_agent = 100.0 - pct_customer
    print(f"  -> % of time the AI agent speaks (output): {pct_agent:.1f}%")

    print()
    pct_cached = ask_float(
        "% of input tokens that are cached (reused prompt/context)", 10.0
    )

    return {
        "agents": agents,
        "calls_per_agent": calls_per_agent,
        "avg_duration_min": avg_duration_min,
        "working_days": working_days,
        "pct_input": pct_customer / 100.0,
        "pct_output": pct_agent / 100.0,
        "pct_cached": pct_cached / 100.0,
    }


def calculate_tokens(params: dict, tier_data: dict) -> dict:
    """Calculate monthly audio and text tokens."""
    total_calls = params["agents"] * params["calls_per_agent"] * params["working_days"]
    total_seconds = total_calls * params["avg_duration_min"] * 60

    input_secs = total_seconds * params["pct_input"]
    output_secs = total_seconds * params["pct_output"]

    tps_in = tier_data["token_ratio"]["input_per_sec"]
    tps_out = tier_data["token_ratio"]["output_per_sec"]

    audio_input_tokens = input_secs * tps_in
    audio_output_tokens = output_secs * tps_out

    cached_audio_input = audio_input_tokens * params["pct_cached"]
    fresh_audio_input = audio_input_tokens - cached_audio_input

    # Text: estimate ~20% additional tokens (system prompt,
    # instructions, function calling, conversation context)
    text_input_tokens = audio_input_tokens * 0.20
    text_output_tokens = audio_output_tokens * 0.10
    cached_text_input = text_input_tokens * params["pct_cached"]
    fresh_text_input = text_input_tokens - cached_text_input

    return {
        "total_calls": total_calls,
        "total_hours": total_seconds / 3600,
        "audio_input_fresh_m": fresh_audio_input / 1_000_000,
        "audio_input_cached_m": cached_audio_input / 1_000_000,
        "audio_output_m": audio_output_tokens / 1_000_000,
        "text_input_fresh_m": fresh_text_input / 1_000_000,
        "text_input_cached_m": cached_text_input / 1_000_000,
        "text_output_m": text_output_tokens / 1_000_000,
    }


def calculate_cost(
    tier: str,
    audio_mode: str,
    tokens: dict,
    use_avatar: bool,
    avatar_minutes: float,
    use_custom_voice_hosting: bool,
) -> dict:
    """Calculate itemized monthly cost."""
    tier_data = PRICING[tier]
    costs = {}

    # ── Audio ──
    audio_prices = tier_data.get(audio_mode)
    if audio_prices:
        costs["Audio input (fresh)"] = (
            tokens["audio_input_fresh_m"] * audio_prices["input"]
        )
        cached_price = audio_prices.get("cached_input")
        if cached_price:
            costs["Audio input (cached)"] = (
                tokens["audio_input_cached_m"] * cached_price
            )
        else:
            costs["Audio input (cached — N/A)"] = 0.0

        costs["Audio output"] = tokens["audio_output_m"] * audio_prices["output"]

    # ── Text ──
    text_prices = tier_data.get("text")
    if text_prices:
        costs["Text input (fresh)"] = (
            tokens["text_input_fresh_m"] * text_prices["input"]
        )
        cached_txt = text_prices.get("cached_input")
        if cached_txt:
            costs["Text input (cached)"] = (
                tokens["text_input_cached_m"] * cached_txt
            )
        costs["Text output"] = tokens["text_output_m"] * text_prices["output"]
    else:
        costs["Text (BYO — charged separately)"] = 0.0

    # ── Avatar ──
    if use_avatar:
        costs["Interactive avatar (real-time)"] = (
            avatar_minutes * AVATAR_PRICE_PER_MINUTE
        )

    # ── Custom Voice hosting ──
    if use_custom_voice_hosting and audio_mode == "audio_custom":
        hours_month = 730  # ~24*30.4
        costs["Custom voice endpoint hosting"] = (
            hours_month * CUSTOM_VOICE_HOSTING_PER_HOUR
        )
        costs["Custom speech endpoint hosting"] = (
            hours_month * STT_CUSTOM_HOSTING_PER_HOUR
        )

    return costs


def print_results(
    tier: str,
    audio_mode: str,
    params: dict,
    tokens: dict,
    costs: dict,
):
    audio_labels = {
        "audio_standard": "Azure Speech standard",
        "audio_custom": "Azure Speech custom",
        "native_realtime": "Native realtime audio",
    }

    print()
    print("=" * 70)
    print("  RESULTS — Voice Live Monthly Cost Estimate")
    print("=" * 70)

    print()
    print(f"  Tier:              Voice Live {tier}")
    print(f"  Models:            {', '.join(PRICING[tier]['modelos'])}")
    print(f"  Audio mode:        {audio_labels.get(audio_mode, audio_mode)}")

    print()
    print("  ── Contact Center Volume ──")
    print(f"  Concurrent agents:        {params['agents']}")
    print(f"  Calls/agent/day:          {params['calls_per_agent']}")
    print(f"  Average duration:         {params['avg_duration_min']:.1f} min")
    print(f"  Working days/month:       {params['working_days']}")
    print(f"  Total calls/month:        {tokens['total_calls']:,.0f}")
    print(f"  Total audio hours/month:  {tokens['total_hours']:,.1f} hrs")

    print()
    print("  ── Estimated Tokens (millions) ──")
    print(f"  Audio input (fresh):   {tokens['audio_input_fresh_m']:>10.2f} M tokens")
    print(f"  Audio input (cached):  {tokens['audio_input_cached_m']:>10.2f} M tokens")
    print(f"  Audio output:          {tokens['audio_output_m']:>10.2f} M tokens")
    print(f"  Text input (fresh):    {tokens['text_input_fresh_m']:>10.2f} M tokens")
    print(f"  Text input (cached):   {tokens['text_input_cached_m']:>10.2f} M tokens")
    print(f"  Text output:           {tokens['text_output_m']:>10.2f} M tokens")

    print()
    print("  ── Cost Breakdown (USD/month) ──")
    total = 0.0
    for label, cost in costs.items():
        print(f"  {label:<40s} ${cost:>12,.2f}")
        total += cost

    print("  " + "─" * 55)
    print(f"  {'ESTIMATED MONTHLY TOTAL':<40s} ${total:>12,.2f}")
    print()
    if tokens["total_calls"] > 0:
        cost_per_call = total / tokens["total_calls"]
        cost_per_min = total / (tokens["total_hours"] * 60) if tokens["total_hours"] > 0 else 0
        print(f"  Cost per call:    ${cost_per_call:.4f}")
        print(f"  Cost per minute:  ${cost_per_min:.4f}")

    print()
    print("  ⚠ IMPORTANT:")
    print("    - Prices are reference estimates only.")
    print("    - They do not include taxes or commitment tier discounts.")
    print("    - Custom voice training is charged separately ($52/hr compute).")
    print("    - Verify updated prices on the Azure portal.")
    print("=" * 70)


def compare_all_tiers(params: dict, audio_mode: str):
    """Compare the 3 main tiers for the same scenario."""
    print()
    print("=" * 70)
    print("  TIER COMPARISON — Same Contact Center Scenario")
    print("=" * 70)
    print()

    results = []
    for tier in ["Pro", "Standard", "Lite"]:
        tier_data = PRICING[tier]
        effective_audio = audio_mode
        if audio_mode == "native_realtime" and tier_data.get("native_realtime") is None:
            effective_audio = "audio_standard"

        tokens = calculate_tokens(params, tier_data)
        costs = calculate_cost(tier, effective_audio, tokens, False, 0, False)
        total = sum(costs.values())
        results.append((tier, total, tokens["total_calls"]))

    print(f"  {'Tier':<20s} {'Monthly cost':>15s} {'Cost/call':>15s} {'Cost/minute':>15s}")
    print("  " + "─" * 65)
    total_calls = results[0][2]
    total_minutes = total_calls * params["avg_duration_min"]
    for tier, total, _ in results:
        cpc = total / total_calls if total_calls > 0 else 0
        cpm = total / total_minutes if total_minutes > 0 else 0
        print(f"  Voice Live {tier:<8s} ${total:>13,.2f} ${cpc:>13.4f} ${cpm:>13.4f}")

    cheapest = min(results, key=lambda x: x[1])
    print()
    print(f"  -> Most economical: Voice Live {cheapest[0]} (${cheapest[1]:,.2f}/month)")
    print("=" * 70)


def main():
    print_header()

    tier = select_tier()
    audio_mode = select_audio_mode(tier)

    params = get_contact_center_params()

    print()
    use_avatar = ask_yes_no("Will you use an interactive real-time avatar?")
    avatar_minutes = 0.0
    if use_avatar:
        avatar_minutes = params["agents"] * params["calls_per_agent"] * params["working_days"] * params["avg_duration_min"]
        print(f"  -> Estimated avatar minutes/month: {avatar_minutes:,.0f}")

    use_custom_hosting = False
    if audio_mode == "audio_custom":
        use_custom_hosting = ask_yes_no(
            "Include custom endpoint hosting cost (24/7)?"
        )

    # Calculate
    tier_data = PRICING[tier]
    tokens = calculate_tokens(params, tier_data)
    costs = calculate_cost(
        tier, audio_mode, tokens, use_avatar, avatar_minutes, use_custom_hosting
    )

    print_results(tier, audio_mode, params, tokens, costs)

    # Comparison
    print()
    do_compare = ask_yes_no("Would you like to see a comparison across the 3 tiers (Pro/Standard/Lite)?")
    if do_compare:
        compare_all_tiers(params, audio_mode)


if __name__ == "__main__":
    main()
