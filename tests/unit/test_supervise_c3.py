"""Named C3 grammar cases: a TODO stage may be referenced as blocked, not claimed complete."""

from __future__ import annotations

import pytest
from scripts.supervise import c3_is_meta, c3_todo_reference_errors


def _rows(**statuses: str) -> dict[str, dict[str, str]]:
    return {sid: {"status": status} for sid, status in statuses.items()}


def _errors(subject: str, body: str = "", **statuses: str) -> list[str]:
    return c3_todo_reference_errors([{"subject": subject, "body": body}], _rows(**statuses))


@pytest.mark.parametrize(
    ("title", "expected_step"),
    [
        pytest.param("S-033 complete while ledger TODO", "S-033", id="complete-todo-stage"),
        pytest.param("S-033 closed while ledger TODO", "S-033", id="closed-todo-stage"),
        pytest.param("S-033 GREEN while ledger TODO", "S-033", id="green-todo-stage"),
        pytest.param("implemented S-033 while ledger TODO", "S-033", id="implemented-todo-stage"),
        pytest.param("S-033 passed while ledger TODO", "S-033", id="passed-todo-stage"),
    ],
)
def test_c3_unresolved_closure_claims_fail_named(title: str, expected_step: str) -> None:
    assert _errors(title, **{expected_step: "TODO"}) == [f"{expected_step} has commits but ledger still TODO"]


@pytest.mark.parametrize(
    "title",
    [
        pytest.param("ci(loop): name the open pre-S-033 blockers without closing them", id="historical-1ca0af6-title"),
        pytest.param("S-033 TODO", id="explicit-todo"),
        pytest.param("S-033 not-started", id="explicit-not-started"),
        pytest.param("without closing S-033", id="explicit-without-closing"),
        pytest.param("open S-033 blocker", id="explicit-open-blocker"),
        pytest.param("pre-S-033 blockers", id="pre-prefix-with-blocker-context"),
        pytest.param("S-033: not started.", id="punctuation-not-started"),
        pytest.param("BUG-18 stays open for S-028, S-033, and S-086", id="open-owner-list"),
        pytest.param("BUG-18 stays open\nfor S-028, S-033, and S-086", id="wrapped-owner-list"),
        pytest.param(
            "BUG-18 tracks the always-on -y overwrite for S-028, S-033, and S-086", id="tracked-bug-owner-list"
        ),
        pytest.param("NG-1: no priority, persistence, or retry (S-072)", id="explicit-nongoal-note"),
        pytest.param("transitive audit exceptions are documented (S-037/S-035)", id="parenthetical-stage-citation"),
    ],
)
def test_c3_explicit_nonclosure_references_are_exempt_named(title: str) -> None:
    assert _errors(title, **{"S-033": "TODO"}) == []


def test_c3_bare_pre_prefix_is_not_an_exemption() -> None:
    assert _errors("pre-S-033", **{"S-033": "TODO"}) == ["S-033 has commits but ledger still TODO"]


def test_c3_closure_claim_overrides_nonclosure_context_in_same_clause() -> None:
    assert _errors("S-033 TODO but S-033 complete", **{"S-033": "TODO"}) == ["S-033 has commits but ledger still TODO"]


def test_c3_claim_words_are_case_insensitive_but_stage_ids_are_case_sensitive() -> None:
    assert _errors("s-033 cLoSeD", **{"S-033": "TODO"}) == []
    assert _errors("S-033 cLoSeD", **{"S-033": "TODO"}) == ["S-033 has commits but ledger still TODO"]


def test_c3_negated_closure_is_nonclosure_not_a_pass_claim() -> None:
    assert _errors("S-033 is not complete", **{"S-033": "TODO"}) == []


def test_c3_punctuation_does_not_hide_a_closure_claim() -> None:
    assert _errors("S-033 — COMPLETE!", **{"S-033": "TODO"}) == ["S-033 has commits but ledger still TODO"]


def test_c3_reads_subject_and_body_independently() -> None:
    assert _errors("ci(loop): documentation only", "S-033 complete", **{"S-033": "TODO"}) == [
        "S-033 has commits but ledger still TODO"
    ]
    assert _errors("ci(loop): documentation only", "S-033 not-started", **{"S-033": "TODO"}) == []


def test_c3_multiple_stage_references_are_evaluated_per_stage() -> None:
    errors = _errors(
        "pre-S-033 blockers; S-034 implemented",
        **{"S-033": "TODO", "S-034": "TODO"},
    )
    assert errors == ["S-034 has commits but ledger still TODO"]


def test_c3_nonclosure_note_does_not_mask_other_stage_claim() -> None:
    errors = _errors(
        "S-033 TODO and S-034 complete",
        **{"S-033": "TODO", "S-034": "TODO"},
    )
    assert errors == ["S-034 has commits but ledger still TODO"]


def test_c3_meta_commit_without_stage_reference_is_not_a_stage_claim() -> None:
    assert c3_is_meta("docs(loop): note readiness")
    assert (
        c3_todo_reference_errors(
            [{"subject": "docs(loop): note readiness", "body": ""}],
            _rows(**{"S-033": "TODO"}),
        )
        == []
    )


def test_c3_stage_reference_with_multiple_title_stages_preserves_open_step() -> None:
    errors = _errors(
        "S-015 and S-033 TODO",
        **{"S-015": "REVIEW", "S-033": "TODO"},
    )
    assert errors == []
