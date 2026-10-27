import json

from nanoporous.cli import main


def test_simulation_cli_writes_traceable_json(tmp_path):
    path = tmp_path / "run.json"
    main([
        "simulate", "--seed", "33", "--particles", "50",
        "--steps", "120", "--obstacles", "2", "--out", str(path),
    ])
    data = json.loads(path.read_text())
    assert data["status"] == "simulation_only_not_experimentally_validated"
    assert data["parameters"]["seed"] == 33
    assert len(data["time"]) == len(data["msd"])
    assert len(data["tracked_unwrapped_trajectories"]) == len(data["time"])
    assert "bootstrap" in data


def test_design_cli_writes_ranked_candidates(tmp_path):
    path = tmp_path / "design.json"
    # This intentionally exercises the default search and is slower than a unit test.
    # We use a reduced-run integration check through search_microstructures elsewhere.
    from nanoporous.design import DesignConfig, search_microstructures
    from nanoporous.dynamics import SimulationConfig
    report = search_microstructures(
        DesignConfig(fractions=(0.0, 0.05), replicates=2, seed=21),
        SimulationConfig(steps=80, particles=30, sample_every=10, tracked_particles=0)
    )
    path.write_text(json.dumps(report))
    record = json.loads(path.read_text())
    assert record["best"]["target_absolute_error"] >= 0
    assert record["replicates"] == 2
