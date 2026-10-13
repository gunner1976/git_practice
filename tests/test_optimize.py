from casingdesign.catalog import Catalog
from casingdesign.design import optimize_string


def test_optimizer_returns_passing_sorted_by_cost(onshore_well):
    cat = Catalog.default()
    s = onshore_well.string("Intermediate")
    res = optimize_string(onshore_well, s, cat)
    assert res, "expected at least one passing design"
    assert all(c.result.passes for c in res)
    costs = [c.cost_per_ft for c in res]
    assert costs == sorted(costs)
    # The 40# L-80 is known to fail this well.
    assert not any(c.spec.pipe.nominal_weight == 40.0 and c.spec.grade.name == "L-80"
                   for c in res)


def test_sour_well_excludes_non_sour_grades(onshore_well):
    cat = Catalog.default()
    onshore_well.formation.sour = True
    s = onshore_well.string("Production")
    for c in optimize_string(onshore_well, s, cat):
        assert c.spec.grade.sour_service
