from __future__ import annotations

from collections.abc import Callable
from typing import Any

from .formula import add_formula, parse_formula, subtract_formula

BaseRecord = tuple[dict[str, int], str, list[str], int, list[int] | None]
RecordFactory = Callable[..., Any]


def apply_h_shift(counts: dict[str, int], shift: int) -> dict[str, int] | None:
    if shift == 0:
        return dict(counts)
    result = dict(counts)
    result["H"] = result.get("H", 0) + shift
    if result["H"] < 0:
        return None
    return {element: count for element, count in result.items() if count}


def adduct_counts(adduct: str) -> tuple[dict[str, int], bool]:
    if adduct.startswith("-"):
        return parse_formula(adduct[1:]), False
    return parse_formula(adduct), True


def apply_adduct(counts: dict[str, int], adduct: str) -> dict[str, int] | None:
    change, is_add = adduct_counts(adduct)
    return add_formula(counts, change) if is_add else subtract_formula(counts, change)


def process_base_records(
    row: dict,
    bases: list[BaseRecord],
    config: dict,
    record_factory: RecordFactory,
    extend_penalty: float = 0.0,
) -> list[Any]:
    """Generate records from base count/path tuples by applying ion rules."""
    records: list[Any] = []
    for counts, base_type, base_path, breaks, atom_indices in bases:
        for shift in config["ion_rules"]["h_shift_range"]:
            shifted = apply_h_shift(counts, int(shift))
            if shifted is None:
                continue
            path = base_path + ([f"H shift {shift:+d}"] if shift else [])
            gen_type = base_type if shift == 0 else "h_shift"
            rec = record_factory(
                row,
                shifted,
                "neutral",
                0,
                gen_type,
                path,
                config,
                broken_bonds=breaks,
                h_shift=shift,
                fragment_atom_indices=atom_indices,
            )
            if extend_penalty:
                rec.score = max(0.0, rec.score - extend_penalty)
            records.append(rec)

            for mode, charge, adducts in [
                ("positive", 1, config["ion_rules"]["common_adducts_positive"]),
                ("negative", -1, config["ion_rules"]["common_adducts_negative"]),
            ]:
                for adduct in adducts:
                    adducted = apply_adduct(shifted, adduct)
                    if adducted is None:
                        continue
                    rec2 = record_factory(
                        row,
                        adducted,
                        mode,
                        charge,
                        "adduct",
                        path + [adduct],
                        config,
                        broken_bonds=breaks,
                        h_shift=shift,
                        adduct=adduct,
                        fragment_atom_indices=atom_indices,
                    )
                    if extend_penalty:
                        rec2.score = max(0.0, rec2.score - extend_penalty)
                    records.append(rec2)

            for loss in config["ion_rules"]["neutral_losses"]:
                lost = subtract_formula(shifted, parse_formula(loss))
                if lost is not None:
                    rec3 = record_factory(
                        row,
                        lost,
                        "neutral",
                        0,
                        "neutral_loss",
                        path + [f"-{loss}"],
                        config,
                        broken_bonds=breaks,
                        h_shift=shift,
                        neutral_losses=[loss],
                        fragment_atom_indices=atom_indices,
                    )
                    if extend_penalty:
                        rec3.score = max(0.0, rec3.score - extend_penalty)
                    records.append(rec3)
    return records


def generate_dimer_records(
    row: dict,
    parent_counts: dict[str, int],
    config: dict,
    record_factory: RecordFactory,
) -> list[Any]:
    if not config["ion_rules"].get("dimers", True):
        return []
    records = []
    doubled = add_formula(parent_counts, parent_counts)
    for adduct, mode, charge in [
        ("H", "positive", 1),
        ("Na", "positive", 1),
        ("-H", "negative", -1),
        ("Cl", "negative", -1),
    ]:
        counts = apply_adduct(doubled, adduct)
        if counts is not None:
            records.append(
                record_factory(row, counts, mode, charge, "dimer", ["2M", adduct], config, adduct=adduct)
            )
    return records
