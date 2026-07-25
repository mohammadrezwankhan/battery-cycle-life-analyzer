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

    from .datasets import synthetic_lfp, load_cycle_data
    from .core import fit_capacity_fade, fit_all_models, best_model

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
        results = fit_all_models(x, y)
        name, best = best_model(results)
        for r in results.values():
            print(r.summary(ascii_only=True) + "\n")
        print(f"Best model: {name}")
    else:
        result = fit_capacity_fade(x, y, model=args.model)
        print(result.summary(ascii_only=True))

    from .viz import capacity_fade
    import matplotlib.pyplot as plt
    if args.model == "all":
        from .viz import model_comparison
        fig = model_comparison(results)
    else:
        fig, ax = plt.subplots()
        capacity_fade(result, ax=ax)
    fig.savefig("bcla_demo.png", dpi=150, bbox_inches="tight")
    print("Saved bcla_demo.png")


if __name__ == "__main__":
    main()
