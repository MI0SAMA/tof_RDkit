from __future__ import annotations

import re

MASS = {
    "H": 1.00782503223,
    "C": 12.00000000000,
    "N": 14.00307400443,
    "O": 15.99491461957,
    "F": 18.99840316273,
    "Na": 22.9897692820,
    "Mg": 23.985041697,
    "Al": 26.98153853,
    "Si": 27.97692653465,
    "P": 30.97376199842,
    "S": 31.9720711744,
    "Cl": 34.968852682,
    "K": 38.9637064864,
    "Ca": 39.962590863,
    "Ti": 47.94794198,
    "Fe": 55.93493633,
    "Cu": 62.92959772,
    "Zn": 63.92914201,
    "Br": 78.9183376,
    "I": 126.9044719,
    "Cs": 132.90545196,
}

TOKEN_RE = re.compile(r"([A-Z][a-z]?)(\d*)")


def parse_formula(formula: str) -> dict[str, int]:
    formula = str(formula).strip()
    if not formula:
        raise ValueError("Formula is empty")
    pos = 0
    counts: dict[str, int] = {}
    for match in TOKEN_RE.finditer(formula):
        if match.start() != pos:
            raise ValueError(f"Invalid formula near {formula[pos:]!r}")
        element, raw_count = match.groups()
        if element not in MASS:
            raise ValueError(f"Unknown element {element!r}")
        count = int(raw_count) if raw_count else 1
        if count <= 0:
            raise ValueError(f"Invalid count for {element}: {count}")
        counts[element] = counts.get(element, 0) + count
        pos = match.end()
    if pos != len(formula):
        raise ValueError(f"Invalid formula near {formula[pos:]!r}")
    return counts


def format_formula(counts: dict[str, int]) -> str:
    clean = {element: int(count) for element, count in counts.items() if int(count) != 0}
    for element, count in clean.items():
        if element not in MASS:
            raise ValueError(f"Unknown element {element!r}")
        if count < 0:
            raise ValueError(f"Negative count for {element}: {count}")
    if not clean:
        raise ValueError("Formula has no atoms")
    if "C" in clean:
        order = ["C"] + (["H"] if "H" in clean else []) + sorted(e for e in clean if e not in {"C", "H"})
    else:
        order = sorted(clean)
    return "".join(element + (str(clean[element]) if clean[element] != 1 else "") for element in order)


def add_formula(a: dict[str, int], b: dict[str, int]) -> dict[str, int]:
    result = dict(a)
    for element, count in b.items():
        result[element] = result.get(element, 0) + count
    return {element: count for element, count in result.items() if count}


def subtract_formula(a: dict[str, int], b: dict[str, int]) -> dict[str, int] | None:
    result = dict(a)
    for element, count in b.items():
        next_count = result.get(element, 0) - count
        if next_count < 0:
            return None
        result[element] = next_count
    filtered = {element: count for element, count in result.items() if count}
    return filtered if filtered else None


def exact_mass(counts: dict[str, int]) -> float:
    return sum(MASS[element] * count for element, count in counts.items())


def is_valid_formula(counts: dict[str, int], allowed_elements: list[str]) -> bool:
    allowed = set(allowed_elements)
    return all(element in allowed and count >= 0 for element, count in counts.items())


def normalize_formula_string(formula: str) -> str:
    return format_formula(parse_formula(formula))


def mass_error(observed_mz: float, theoretical_mz: float) -> tuple[float, float]:
    da = float(observed_mz) - float(theoretical_mz)
    ppm = da / float(theoretical_mz) * 1_000_000 if theoretical_mz else 0.0
    return da, ppm
