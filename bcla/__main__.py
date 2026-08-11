"""
CLI entry point: ``python -m bcla --help``
"""
import argparse


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="python -m bcla",
        description="Battery Cycle-Life Analyzer - quick demo",
    )
    parser.add_argument("--cycles", type=int, default=1500,
                        help="Number of synthetic cycles")
    parser.add_argument("--model", choices=["linear", "power_law", "logarithmic", "all"],
                        default="all", help="Degradation model to fit")
    parser.add_argument(
        "--selection",
        choices=["validation", "in-sample"],
        default="validation",
        help="Selection method when --model all (default: validation)",
    )
    parser.add_argument(
        "--validation-fraction",
        type=float,
        default=0.2,
        help="Latest observation fraction held out for validation (default: 0.2)",
    )
    parser.add_argument(
        "--bootstrap-samples",
        type=int,
        default=0,
        help="Residual-bootstrap replicates for EOL/RUL intervals; 0 disables",
    )
    parser.add_argument("--csv", type=str,
                        help="Path to a CSV/TSV file with cycle + capacity columns")
    parser.add_argument("--cycle-col", default="cycle",
                        help="Column name for cycle data (default: cycle)")
    parser.add_argument("--capacity-col", default="capacity",
                        help="Column name for capacity data (default: capacity)")
    parser.add_argument(
        "--sep",
        default=None,
        help="Separator character; defaults to tab for .tsv/.tab and comma otherwise",
    )
    parser.add_argument("--no-normalize", action="store_true",
                        help="Disable normalization when loading CSV capacity")
    args = parser.parse_args()
    if args.bootstrap_samples != 0 and args.bootstrap_samples < 20:
        parser.error("--bootstrap-samples must be 0 or at least 20")
    if not 0.0 < args.validation_fraction < 1.0:
        parser.error("--validation-fraction must be between 0 and 1")

    from .datasets import synthetic_lfp, load_cycle_data
    from .core import (
        best_model,
        bootstrap_life_projection,
        fit_all_models,
        fit_capacity_fade,
        select_model_by_validation,
    )

    if args.csv:
        x, y = load_cycle_data(
            args.csv,
            cycle_col=args.cycle_col,
            capacity_col=args.capacity_col,
            sep=args.sep,
            normalize=not args.no_normalize,
        )
    else:
        x, y = synthetic_lfp(cycles=args.cycles)

    if args.model == "all":
        if args.selection == "validation":
            try:
                selection = select_model_by_validation(
                    x,
                    y,
                    validation_fraction=args.validation_fraction,
                )
            except ValueError as exc:
                parser.error(f"cannot select a model: {exc}")
            name, best = selection.model_name, selection.fit
            score = selection.validation_score
        results = fit_all_models(x, y)
        for r in results.values():
            print(r.summary(ascii_only=True) + "\n")
        if args.selection == "validation":
            print(
                f"Selected model: {name} "
                f"(held-out RMSE={score.rmse:.5f}, "
                f"validation points={score.validation_size})"
            )
        else:
            name, best = best_model(results)
            print(f"Selected model: {name} (lowest in-sample RMSE)")
    else:
        best = fit_capacity_fade(x, y, model=args.model)
        print(best.summary(ascii_only=True))

    if args.bootstrap_samples:
        try:
            interval = bootstrap_life_projection(
                best,
                samples=args.bootstrap_samples,
                random_state=42,
            )
        except ValueError as exc:
            parser.error(f"cannot compute bootstrap interval: {exc}")
        confidence_pct = interval.confidence * 100.0
        print(
            "Bootstrap replicates: "
            f"successful={interval.successful_samples}, "
            f"censored={interval.censored_samples}, "
            f"failed={interval.failed_samples}, "
            f"requested={interval.requested_samples}"
        )
        if interval.eol_lower is None:
            print(
                f"{confidence_pct:.0f}% EOL/RUL interval unavailable: "
                "bounds withheld because at least one replicate was censored "
                "or failed"
            )
        else:
            print(
                f"{confidence_pct:.0f}% EOL interval: "
                f"{interval.eol_lower:.0f}-{interval.eol_upper:.0f} cycles"
            )
            print(
                f"{confidence_pct:.0f}% RUL interval: "
                f"{interval.rul_lower:.0f}-{interval.rul_upper:.0f} cycles"
            )

    from .viz import capacity_fade
    import matplotlib.pyplot as plt
    if args.model == "all":
        from .viz import model_comparison
        fig = model_comparison(results)
    else:
        fig, ax = plt.subplots()
        capacity_fade(best, ax=ax)
    fig.savefig("bcla_demo.png", dpi=150, bbox_inches="tight")
    print("Saved bcla_demo.png")


if __name__ == "__main__":
    main()
