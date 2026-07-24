"""
CLI entry point: ``python -m bcla --help``
"""
import argparse


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="python -m bcla",
        description="Battery Cycle‑Life Analyzer — quick demo",
    )
    parser.add_argument("--cycles", type=int, default=1500,
                        help="Number of synthetic cycles")
    parser.add_argument("--model", choices=["linear", "power_law", "logarithmic", "all"],
                        default="all", help="Degradation model to fit")
    args = parser.parse_args()

    from .datasets import synthetic_lfp
    from .core import fit_capacity_fade, fit_all_models, best_model

    x, y = synthetic_lfp(cycles=args.cycles)

    if args.model == "all":
        results = fit_all_models(x, y)
        name, best = best_model(results)
        for r in results.values():
            print(r.summary() + "\n")
        print(f"→ Best model: {name}")
    else:
        result = fit_capacity_fade(x, y, model=args.model)
        print(result.summary())

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
