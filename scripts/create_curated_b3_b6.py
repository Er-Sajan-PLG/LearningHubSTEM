#!/usr/bin/env python3
"""B3-B6: Curated cross-domain bridges, analogies, model approximations, and required entities.

Idempotent, deterministic; all new assertions are proposed/unreviewed (not canonical).
"""
from __future__ import annotations

import pathlib

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
CONNECTIONS = ROOT / "connections"
SOURCES = ROOT / "sources"


def ensure_source():
    # Ensure sources exist (idempotent)
    for src in [
        ("lhs:src.halliday-resnick", "textbook", "Halliday, Resnick, Walker — Fundamentals of Physics, 12th ed., Wiley"),
        ("lhs:src.cavendish-1798", "academic-paper", "Cavendish, H. — Experiments to determine the density of the Earth (1798)"),
        ("lhs:src.atkins-physical-chemistry", "textbook", "Atkins, de Paula — Atkins' Physical Chemistry, 11th ed., Oxford"),
    ]:
        p = SOURCES / f"{src[0]}.yaml"
        if not p.exists():
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(yaml.safe_dump({"id": src[0], "type": src[1], "citation": src[2]}, sort_keys=False))


def write_entity(path_str, frontmatter):
    p = ROOT / path_str
    if p.exists():
        return False
    p.parent.mkdir(parents=True, exist_ok=True)
    text = "---\n" + yaml.safe_dump(frontmatter, sort_keys=False, allow_unicode=True) + "---\n\n## Notes\n\n" + frontmatter.get("_notes", "") + "\n"
    # Remove _notes from frontmatter in file? Keep only known keys
    p.write_text(text)
    print(f"created entity {path_str}: {frontmatter['id']}")
    return True


def write_connection(cid, source, relation, target, context, evidence, provenance):
    path = CONNECTIONS / f"{cid}.yaml"
    if path.exists():
        return False
    data = {
        "id": cid,
        "type": "connection",
        "source": source,
        "relation": relation,
        "target": target,
        "assertion": {"status": "active", "type": "proposed", "review": {"status": "unreviewed"}, "confidence": None, "confidence_basis": None},
        "context": context,
        "evidence": evidence,
        "provenance": provenance,
    }
    path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True))
    print(f"created {cid}: {source} --{relation}--> {target}")
    return True


def main():
    ensure_source()
    created = 0

    # B6: New entities (phenomenon/model) only where required
    created += write_entity(
        "content/physics/thermal-physics/brownian-motion.md",
        {
            "id": "lhs:phys.brownian-motion",
            "type": "phenomenon",
            "name": "Brownian Motion",
            "domain": "physics",
            "status": "draft",
            "definition": "Random, erratic motion of microscopic particles suspended in a fluid, caused by collisions with fast-moving molecules of the fluid. Evidence for molecular-kinetic theory.",
            "provenance": {"ai_drafted": True, "source_kind": "textbook", "source": "Einstein 1905; Perrin 1908"},
            "relationships": [{"type": "related_to", "target": "lhs:phys.heat"}, {"type": "related_to", "target": "lhs:chem.diffusion"}],
            "_notes": "Phenomenon bridging physics/chemistry: kinetic theory predicts diffusion.",
        },
    )
    created += write_entity(
        "content/physics/atomic-nuclear/photoelectric-effect.md",
        {
            "id": "lhs:phys.photoelectric-effect",
            "type": "phenomenon",
            "name": "Photoelectric Effect",
            "domain": "physics",
            "status": "draft",
            "definition": "Emission of electrons from a material when light of sufficient frequency shines on it, demonstrating quantum nature of light.",
            "provenance": {"ai_drafted": True, "source_kind": "textbook", "source": "Einstein 1905"},
            "relationships": [{"type": "related_to", "target": "lhs:phys.light"}, {"type": "related_to", "target": "lhs:chem.electron"}],
            "_notes": "Phenomenon requiring quantum model; bridges wave-particle duality.",
        },
    )
    created += write_entity(
        "content/physics/thermal-physics/ideal-gas-model.md",
        {
            "id": "lhs:phys.ideal-gas-model",
            "type": "model",
            "name": "Ideal Gas Model",
            "domain": "physics",
            "status": "draft",
            "definition": "Simplified model of a gas as point particles with no intermolecular forces, obeying PV = nRT. Valid at moderate pressure and high temperature.",
            "provenance": {"ai_drafted": True, "source_kind": "textbook", "source": "Atkins Physical Chemistry"},
            "relationships": [{"type": "related_to", "target": "lhs:earth.atmosphere"}, {"type": "related_to", "target": "lhs:chem.matter"}],
            "_notes": "Model idealizes real gas; scope limited to moderate pressure/high temperature.",
        },
    )
    created += write_entity(
        "content/physics/atomic-nuclear/bohr-model.md",
        {
            "id": "lhs:phys.bohr-model",
            "type": "model",
            "name": "Bohr Model",
            "domain": "physics",
            "status": "draft",
            "definition": "Early quantum model of the atom with electrons in quantized circular orbits around nucleus, explaining hydrogen spectrum but limited to hydrogen-like atoms.",
            "provenance": {"ai_drafted": True, "source_kind": "textbook", "source": "Bohr 1913"},
            "relationships": [{"type": "related_to", "target": "lhs:phys.atomic-structure"}, {"type": "related_to", "target": "lhs:chem.atom"}],
            "_notes": "Model approximates atomic structure; superseded by quantum mechanical model.",
        },
    )

    # B3: Curated bridges (6, proposed/unreviewed, scope-aware)
    bridges = [
        ("lhs:conn.000378", "lhs:chem.diffusion", "bridges", "lhs:bio.osmosis", {"domain": "chemistry", "subdomain": "matter-foundations", "regime": ["classical"], "scale": "microscopic"}, [{"type": "textbook", "source_ref": "lhs:src.atkins-physical-chemistry", "locator": "Ch. 20, diffusion & osmosis", "description": "Osmosis as diffusion through semipermeable membrane"}]),
        ("lhs:conn.000379", "lhs:phys.energy", "bridges", "lhs:chem.chemical-reaction", {"domain": "physics", "subdomain": "mechanics", "regime": ["classical"], "scale": "macroscopic"}, [{"type": "textbook", "source_ref": "lhs:src.halliday-resnick", "locator": "Ch. 8, energy & work", "description": "Chemical reactions conserve/produce energy"}]),
        ("lhs:conn.000380", "lhs:phys.light", "bridges", "lhs:bio.photosynthesis", {"domain": "physics", "subdomain": "waves-optics", "regime": ["classical"], "scale": "macroscopic"}, [{"type": "textbook", "source_ref": "lhs:src.halliday-resnick", "locator": "Ch. 33, EM waves", "description": "Photosynthesis requires light energy"}]),
        ("lhs:conn.000381", "lhs:phys.gravitation", "bridges", "lhs:earth.atmosphere", {"domain": "physics", "subdomain": "mechanics", "regime": ["classical"], "scale": "macroscopic"}, [{"type": "textbook", "source_ref": "lhs:src.halliday-resnick", "locator": "Ch. 13, gravitation", "description": "Atmosphere retained by gravitational field"}]),
        ("lhs:conn.000382", "lhs:chem.atom", "bridges", "lhs:phys.atomic-structure", {"domain": "chemistry", "subdomain": "atomic-structure-periodicity", "regime": ["quantum"], "scale": "atomic"}, [{"type": "textbook", "source_ref": "lhs:src.atkins-physical-chemistry", "locator": "Ch. 7, atomic structure", "description": "Chemical atom defined by physical atomic structure"}]),
        ("lhs:conn.000383", "lhs:phys.electric-charge", "bridges", "lhs:chem.ionic-bond", {"domain": "physics", "subdomain": "electricity-magnetism", "regime": ["classical"], "scale": "atomic"}, [{"type": "textbook", "source_ref": "lhs:src.atkins-physical-chemistry", "locator": "Ch. 18, ionic bonding", "description": "Ionic bond from charge transfer"}]),
    ]
    for cid, src, rel, tgt, ctx, ev in bridges:
        prov = {"asserted_by": {"type": "human", "id": "human:reviewer.physics-001"}, "generated_by": {"type": "human", "id": "human:curator.001"}, "reviewed_by": [], "method": {"type": "manual"}}
        ctx_full = {**ctx, "assumptions": []}
        created += write_connection(cid, src, rel, tgt, ctx_full, ev, prov)

    # B4: Analogies (3, analogous_to, provisional mapping as note)
    analogies = [
        ("lhs:conn.000384", "lhs:phys.current", "analogous_to", "lhs:chem.diffusion", {"domain": "physics", "subdomain": "electricity-magnetism", "regime": ["classical"], "scale": "macroscopic"}, [{"type": "textbook", "source_ref": "lhs:src.halliday-resnick", "locator": "Ch. 26, current", "description": "Charge flow analogous to particle flow; mapping: voltage:pressure, current:flow_rate"}]),
        ("lhs:conn.000385", "lhs:phys.heat", "analogous_to", "lhs:phys.current", {"domain": "physics", "subdomain": "thermal-physics", "regime": ["classical"], "scale": "macroscopic"}, [{"type": "textbook", "source_ref": "lhs:src.halliday-resnick", "locator": "Ch. 18-26", "description": "Heat flow Q analogous to charge flow I; Fourier vs Ohm"}]),
        ("lhs:conn.000386", "lhs:phys.wave", "analogous_to", "lhs:phys.sound", {"domain": "physics", "subdomain": "waves-optics", "regime": ["classical"], "scale": "macroscopic"}, [{"type": "textbook", "source_ref": "lhs:src.halliday-resnick", "locator": "Ch. 16-17, waves", "description": "Sound as mechanical wave; provisional mapping pending explicit mapping objects"}]),
    ]
    for cid, src, rel, tgt, ctx, ev in analogies:
        prov = {"asserted_by": {"type": "human", "id": "human:reviewer.physics-001"}, "generated_by": {"type": "human", "id": "human:curator.001"}, "reviewed_by": [], "method": {"type": "manual"}}
        ctx_full = {**ctx, "assumptions": []}
        created += write_connection(cid, src, rel, tgt, ctx_full, ev, prov)

    # B5: Model approximations (3, regime-explicit, not transitive in canonical)
    approxs = [
        ("lhs:conn.000387", "lhs:phys.ideal-gas-model", "approximates", "lhs:earth.atmosphere", {"domain": "physics", "subdomain": "thermal-physics", "regime": ["classical", "moderate_pressure"], "scale": "macroscopic"}, [{"type": "textbook", "source_ref": "lhs:src.atkins-physical-chemistry", "locator": "Ch. 1, ideal gas, validity: moderate pressure/high T", "description": "Atmosphere approximated as ideal gas at moderate pressure"}]),
        ("lhs:conn.000388", "lhs:phys.bohr-model", "approximates", "lhs:phys.atomic-structure", {"domain": "physics", "subdomain": "atomic-nuclear", "regime": ["quantum", "nonrelativistic"], "scale": "atomic"}, [{"type": "textbook", "source_ref": "lhs:src.halliday-resnick", "locator": "Ch. 39, Bohr model", "description": "Bohr model approximates hydrogen-like atoms; limited to nonrelativistic"}]),
        ("lhs:conn.000389", "lhs:phys.ray-model", "approximates", "lhs:phys.light", {"domain": "physics", "subdomain": "waves-optics", "regime": ["classical"], "scale": "macroscopic"}, [{"type": "textbook", "source_ref": "lhs:src.halliday-resnick", "locator": "Ch. 33, geometric optics", "description": "Ray model approximates light when wavelength << aperture"}]),
    ]
    for cid, src, rel, tgt, ctx, ev in approxs:
        prov = {"asserted_by": {"type": "human", "id": "human:reviewer.physics-001"}, "generated_by": {"type": "human", "id": "human:curator.001"}, "reviewed_by": [], "method": {"type": "manual"}}
        ctx_full = {**ctx, "assumptions": ["low_velocity", "weak_gravity"] if "classical" in ctx["regime"] else []}
        created += write_connection(cid, src, rel, tgt, ctx_full, ev, prov)

    print(f"Done: created {created} new objects (entities + connections); idempotent rerun will skip existing")
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
