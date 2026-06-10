from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
from pandas.errors import EmptyDataError

from .matching import calculate_final_score, load_networks, load_rf_candidates, match_rf_with_network, match_spectrum_by_mass
from .molecule_io import get_formula_from_mol, mol_from_smiles, read_compounds, validate_compound_row
from .network import generate_formula_network, write_network_csv, write_network_json
from .reporting import write_markdown_report, write_matches_csv
from .spectrum_io import find_spectrum_files, preprocess_spectrum, read_spectrum_txt, standardize_spectrum, write_parsed_spectrum
from .utils import ensure_dirs, load_config


def _spectrum_id(path: Path) -> str:
    parent = path.parent.name
    stem = path.stem.replace("+", "pos_").replace("-", "neg_").replace(" ", "_")
    return f"{parent}_{stem}" if parent != "data" else stem


def parse_spectra(args) -> None:
    cfg = load_config(args.config)
    paths = ensure_dirs(cfg["io"]["output_dir"])
    for old in paths["parsed_spectra"].glob("*.csv"):
        old.unlink()
    rows = []
    for path in find_spectrum_files(cfg["io"]["data_dir"]):
        sid = _spectrum_id(path)
        try:
            df = read_spectrum_txt(path)
            std = standardize_spectrum(preprocess_spectrum(df, cfg), sid, str(path))
            if std.empty:
                raise ValueError("No peaks remain after preprocessing filters")
            out_path = paths["parsed_spectra"] / f"{sid}.csv"
            write_parsed_spectrum(std, out_path)
            rows.append({"spectrum_id": sid, "source_file": str(path), "status": "parsed", "rows": len(std), "message": ""})
            print(f"parsed {path} -> {out_path}")
        except Exception as exc:
            rows.append({"spectrum_id": sid, "source_file": str(path), "status": "skipped", "rows": 0, "message": str(exc)})
            print(f"skipped {path}: {exc}")
    pd.DataFrame(rows).to_csv(paths["summary"] / "spectrum_parse_summary.csv", index=False)


def build_network(args) -> None:
    cfg = load_config(args.config)
    paths = ensure_dirs(cfg["io"]["output_dir"])
    for old in list(paths["networks"].glob("*.csv")) + list(paths["networks"].glob("*.json")):
        old.unlink()
    compounds_path = Path(args.compounds or cfg["io"]["compounds_file"])
    compounds = read_compounds(compounds_path)
    summary = []
    for _, row in compounds.iterrows():
        try:
            validate_compound_row(row)
            row = row.to_dict()
            mol = mol_from_smiles(row["smiles"])
            if not row.get("formula"):
                row["formula"] = get_formula_from_mol(mol)
            records = generate_formula_network(row, cfg)
            safe_id = str(row["compound_id"]).replace("/", "_")
            write_network_json(records, paths["networks"] / f"{safe_id}.json", row)
            write_network_csv(records, paths["networks"] / f"{safe_id}.csv")
            summary.append({"compound_id": row["compound_id"], "name": row["name"], "status": "built", "records": len(records), "message": ""})
            print(f"built network {row['compound_id']}: {len(records)} records")
        except Exception as exc:
            summary.append({"compound_id": row.get("compound_id", ""), "name": row.get("name", ""), "status": "skipped", "records": 0, "message": str(exc)})
            print(f"skipped compound {row.get('compound_id', '')}: {exc}")
    pd.DataFrame(summary).to_csv(paths["summary"] / "network_build_summary.csv", index=False)


def match_rf(args) -> pd.DataFrame:
    cfg = load_config(args.config)
    paths = ensure_dirs(cfg["io"]["output_dir"])
    rf = load_rf_candidates(args.rf or cfg["io"]["rf_candidates_file"])
    networks = load_networks(args.networks or paths["networks"])
    matches = calculate_final_score(match_rf_with_network(rf, networks, cfg), cfg)
    out = paths["matches"] / "rf_formula_matches.csv"
    write_matches_csv(matches, out)
    print(f"RF formula matches: {len(matches)} -> {out}")
    return matches


def match_spectrum(args) -> pd.DataFrame:
    cfg = load_config(args.config)
    paths = ensure_dirs(cfg["io"]["output_dir"])
    networks = load_networks(args.networks or paths["networks"])
    frames = []
    spectra_dir = Path(args.spectra or paths["parsed_spectra"])
    for path in sorted(spectra_dir.glob("*.csv")):
        spectrum = pd.read_csv(path)
        frames.append(match_spectrum_by_mass(spectrum, networks, cfg["spectrum"]["peak_match_ppm"], cfg["spectrum"]["peak_match_da"]))
    matches = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    out = paths["matches"] / "spectrum_mass_matches.csv"
    write_matches_csv(matches, out)
    print(f"spectrum mass matches: {len(matches)} -> {out}")
    return matches


def report(args) -> None:
    cfg = load_config(args.config)
    paths = ensure_dirs(cfg["io"]["output_dir"])
    for old in paths["reports"].glob("*.md"):
        old.unlink()
    match_frames = []
    for name in ["rf_formula_matches.csv", "spectrum_mass_matches.csv"]:
        path = paths["matches"] / name
        if path.exists() and path.stat().st_size:
            try:
                df = pd.read_csv(path)
            except EmptyDataError:
                continue
            if not df.empty:
                match_frames.append(df)
    matches = pd.concat(match_frames, ignore_index=True) if match_frames else pd.DataFrame()
    spectra = {path.stem: pd.read_csv(path) for path in paths["parsed_spectra"].glob("*.csv")}
    spectrum_ids = (set(matches["spectrum_id"]) if "spectrum_id" in matches else set()) | set(spectra)
    if not spectrum_ids:
        write_markdown_report("global", matches, pd.DataFrame(), paths["reports"] / "global_report.md", cfg)
    for sid in sorted(spectrum_ids):
        sid_matches = matches[matches["spectrum_id"] == sid] if not matches.empty and "spectrum_id" in matches else pd.DataFrame()
        write_markdown_report(sid, sid_matches, spectra.get(sid, pd.DataFrame()), paths["reports"] / f"{sid}_report.md", cfg)
    summary = matches.groupby("spectrum_id").size().reset_index(name="match_rows") if not matches.empty and "spectrum_id" in matches else pd.DataFrame(columns=["spectrum_id", "match_rows"])
    summary.to_csv(paths["summary"] / "match_summary.csv", index=False)
    print(f"reports written -> {paths['reports']}")


def run_all(args) -> None:
    parse_spectra(args)
    build_network(args)
    match_rf(args)
    match_spectrum(args)
    report(args)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="tofsims_formula_network")
    parser.add_argument("--config", default="config/default.yaml")
    sub = parser.add_subparsers(dest="command", required=True)
    for name, func in [
        ("parse-spectra", parse_spectra),
        ("build-network", build_network),
        ("match-rf", match_rf),
        ("match-spectrum", match_spectrum),
        ("report", report),
        ("run-all", run_all),
    ]:
        cmd = sub.add_parser(name)
        cmd.add_argument("--config", default="config/default.yaml")
        cmd.add_argument("--compounds", default=None)
        cmd.add_argument("--rf", default=None)
        cmd.add_argument("--networks", default=None)
        cmd.add_argument("--spectra", default=None)
        cmd.set_defaults(func=func)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
