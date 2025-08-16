
import argparse, json, os, sys
from typing import List
from model import (
    load_cities, load_thresholds, Thresholds, get_threshold_multiplier,
    composite_price_ratio, ease_multiplier, equivalent_price
)

def parse_args():
    p = argparse.ArgumentParser(description="1% Ease Multiplier Calculator (CN vs US)")
    p.add_argument("--cities", default="data/cities.json", help="Path to cities.json")
    p.add_argument("--thresholds", default="data/thresholds.json", help="Path to thresholds.json")
    p.add_argument("--cn", nargs="+", required=True, help="China city list (space-separated)")
    p.add_argument("--us", nargs="+", required=True, help="US city list (space-separated)")
    p.add_argument("--w_h", type=float, default=0.25, help="Housing weight in [0,1] (default 0.25)")
    p.add_argument("--method", choices=["KF","SCF_LOW","SCF_HIGH","CUSTOM"], default="KF", help="Threshold preset method")
    p.add_argument("--us_threshold", type=float, default=None, help="Custom US threshold (USD) if method=CUSTOM")
    p.add_argument("--cn_threshold", type=float, default=None, help="Custom CN threshold (USD) if method=CUSTOM")
    p.add_argument("--cn_price", type=float, default=None, help="Optional CN price to convert to 'US-feel' equivalent")
    p.add_argument("--fx", type=float, default=None, help="Optional CNY per USD for displaying USD equivalent")
    p.add_argument("--out", default=None, help="Optional output JSON path for results")
    return p.parse_args()

def main():
    args = parse_args()
    cities = load_cities(args.cities)
    th_all = load_thresholds(args.thresholds)

    if args.method == "CUSTOM":
        if args.us_threshold is None or args.cn_threshold is None:
            print("For CUSTOM method, please provide --us_threshold and --cn_threshold", file=sys.stderr)
            sys.exit(1)
        th = Thresholds(US=float(args.us_threshold), CN=float(args.cn_threshold))
    else:
        presets = th_all.get("presets", {})
        if args.method not in presets:
            print(f"Preset '{args.method}' not found.", file=sys.stderr)
            sys.exit(1)
        p = presets[args.method]
        th = Thresholds(US=float(p["US"]), CN=float(p["CN"]))

    M = get_threshold_multiplier(th)
    price_ratio = composite_price_ratio(cities, args.cn, args.us, args.w_h)
    ease = ease_multiplier(M, price_ratio)

    result = {
        "inputs": {
            "cn_cities": args.cn,
            "us_cities": args.us,
            "w_h": args.w_h,
            "method": args.method,
            "thresholds_used": {"US": th.US, "CN": th.CN},
            "cn_price": args.cn_price,
            "fx_cny_per_usd": args.fx
        },
        "outputs": {
            "threshold_multiplier_M": M,
            "price_ratio": price_ratio,
            "ease_multiplier": ease
        }
    }

    if args.cn_price is not None:
        eq = equivalent_price(args.cn_price, ease, args.fx)
        result["outputs"]["equivalent_price"] = eq

    txt = json.dumps(result, ensure_ascii=False, indent=2)
    print(txt)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(txt)
        print(f"\nSaved to: {args.out}")

if __name__ == "__main__":
    main()
