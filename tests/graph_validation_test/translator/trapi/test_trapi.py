"""
Unit tests of the low level TRAPI (ARS, KP & ARA) calling subsystem.
"""
from typing import Optional
import pytest

from graph_validation_tests.translator.trapi import (
    get_component_infores_object_id,
    resolve_component_endpoint
)

pytest_plugins = ('pytest_asyncio',)


@pytest.mark.parametrize(
    "component,infores",
    [
        ("arax", "arax"),
        ("aragorn", "aragorn"),
        ("bte", "biothings-explorer"),
        ("improving", "improving-agent"),
        ("molepro", "molepro")
    ]
)
def test_get_get_component_infores_object_id(component: str, infores: str):
    assert get_component_infores_object_id(component=component) == infores


@pytest.mark.skip(
    reason="These tests often work fine with fresh data, " +
           "but fail later due to changes in online resources"
)
@pytest.mark.parametrize(
    "component,environment,result",
    [
        (None, None, f"https://ars.ci.transltr.io/ars/api/"),
        ("ars", None, f"https://ars.ci.transltr.io/ars/api/"),
        ("ars", "non-environment", None),
        ("ars", "test", f"https://ars.test.transltr.io/ars/api/"),
        ("arax", "dev", "https://arax.ncats.io/beta/api/arax/v1.4"),
        # ("aragorn", "prod", "https://aragorn.transltr.io/aragorn"),
        ("bte", "test", "https://bte.test.transltr.io/v1"),
        # ("improving", "test", "https://ia.test.transltr.io/api/v1.4/"),
        ("molepro", "ci", "https://molepro-trapi.ci.transltr.io/molepro/trapi/v1.5"),
        ("foobar", "ci", None),
        ("arax", "non-environment", None),
    ]
)
def test_resolve_component_endpoint(
        component: Optional[str],
        environment: Optional[str],
        result: Optional[str]
):
    endpoint: Optional[str] = \
        resolve_component_endpoint(
            component=component,
            environment=environment,
            target_trapi_version=None,
            target_biolink_version=None
        )
    assert endpoint == result


# @pytest.mark.asyncio
# async def test_execute_trapi_lookup():
#     url: str = TRAPI_TEST_ENDPOINT
#     subject_id = 'MONDO:0005301'
#     subject_category = "biolink:Disease"
#     predicate_name = "treats"
#     predicate_id = f"biolink:{predicate_name}"
#     object_id = 'PUBCHEM.COMPOUND:107970'
#     object_category = "biolink:SmallMolecule"
#     oht: OneHopTest = OneHopTest(endpoints=[url])
#     test_asset: TestAsset = oht.build_test_asset(
#         subject_id=subject_id,
#         subject_category=subject_category,
#         predicate_id=predicate_id,
#         object_id=object_id,
#         object_category=object_category
#     )
#     report: UnitTestReport = await run_one_hop_unit_test(
#         url=url,
#         test_asset=test_asset,
#         creator=by_subject,
#         trapi_version="1.4.2",
#         # biolink_version=None
#     )
#     assert report
