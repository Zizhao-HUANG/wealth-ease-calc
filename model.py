
import json
from dataclasses import dataclass
from typing import List, Dict, Tuple

@dataclass
class Thresholds:
    US: float
    CN: float

def load_cities(path: str) -> Dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_thresholds(path: str) -> Dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def get_threshold_multiplier(t: Thresholds) -> float:
    """
    M = US_1%_threshold / CN_1%_threshold
    """
    if t.CN <= 0:
        raise ValueError("CN threshold must be > 0")
    return t.US / t.CN

def average_indices(cities: Dict, region: str, city_names: List[str]) -> Tuple[float, float]:
    """
    Returns tuple (avg_ex_rent, avg_rent) for the selected city_names in region.
    """
    if region not in cities:
        raise KeyError(f"Region '{region}' not found in dataset.")
    ex_vals, rent_vals = [], []
    for c in city_names:
        if c not in cities[region]:
            raise KeyError(f"City '{c}' not found under region '{region}'. Available: {list(cities[region].keys())}")
        ex_vals.append(cities[region][c]["ex_rent"])
        rent_vals.append(cities[region][c]["rent"])
    if not ex_vals:
        raise ValueError("No cities provided.")
    return sum(ex_vals) / len(ex_vals), sum(rent_vals) / len(rent_vals)

def composite_price_ratio(
    cities_dataset: Dict,
    cn_cities: List[str],
    us_cities: List[str],
    w_housing: float
) -> float:
    """
    Price ratio = w * (Rent_CN / Rent_US) + (1 - w) * (ExRent_CN / ExRent_US)
    All indices should be on the same scale (e.g., NYC=100).
    """
    if not (0.0 <= w_housing <= 1.0):
        raise ValueError("w_housing must be between 0 and 1.")
    ex_cn, rent_cn = average_indices(cities_dataset, "CN", cn_cities)
    ex_us, rent_us = average_indices(cities_dataset, "US", us_cities)
    if ex_us <= 0 or rent_us <= 0:
        raise ValueError("US indices must be > 0.")
    ratio_rent = rent_cn / rent_us
    ratio_ex   = ex_cn / ex_us
    return w_housing * ratio_rent + (1.0 - w_housing) * ratio_ex

def ease_multiplier(M: float, price_ratio: float) -> float:
    """
    Ease = M * price_ratio
    Interpreted as: how many times more 'room' the US-1% has vs CN-1%
    after adjusting for local prices (including housing weight).
    """
    return M * price_ratio

def equivalent_price(cn_price: float, ease: float, fx_cny_per_usd: float = None) -> Dict[str, float]:
    """
    Given a China price (in CNY), scale by 'ease' to obtain the 'US-1% feel' equivalent price (still in CNY).
    Optionally convert to USD using fx (CNY per USD).
    Returns dict with 'eq_price_cny' and (if fx given) 'eq_price_usd'.
    """
    eq_cny = cn_price * ease
    result = {"eq_price_cny": eq_cny}
    if fx_cny_per_usd and fx_cny_per_usd > 0:
        result["eq_price_usd"] = eq_cny / fx_cny_per_usd
    return result
