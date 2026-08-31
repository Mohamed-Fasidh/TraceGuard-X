from dataclasses import dataclass


@dataclass(frozen=True)
class AdversarialCase:
    """
    A bounded adversarial verification case.

    expected_output is optional because only cases for which
    the expected behavior can be established from the task
    semantics should be executed as correctness tests.
    """

    case_id: str
    rationale: str
    input_value: object
    expected_output: object = None


def _existing_inputs(trace):
    """
    Collect inputs already covered by the declared test suite.
    """

    existing = set()

    for case in trace.test_cases:

        if not isinstance(case, dict):
            continue

        if "input" not in case:
            continue

        existing.add(
            repr(case["input"])
        )

    return existing


def _is_identity_task(trace):
    """
    Detect whether the task explicitly requires the function
    to return its input unchanged.

    This is intentionally conservative.
    """

    text = (
        trace.task
        + " "
        + " ".join(trace.requirements)
    ).lower()

    identity_signals = [
        "returns its input unchanged",
        "return its input unchanged",
        "returns the input unchanged",
        "return the input unchanged",
        "input unchanged",
        "input unmodified",
        "returns the input as-is",
        "return the input as-is",
        "identity function",
        "identity",
    ]

    return any(
        signal in text
        for signal in identity_signals
    )


def _identity_candidates():
    """
    High-value counterexamples for identity functions.

    For an identity function:

        expected_output == input_value

    These cases specifically target implementations that
    accidentally normalize, cast, strip, trim, or otherwise
    transform the input.
    """

    return [
        AdversarialCase(
            case_id="I1",
            rationale="leading whitespace must be preserved",
            input_value=" hello ",
            expected_output=" hello ",
        ),
        AdversarialCase(
            case_id="I2",
            rationale="leading tab must be preserved",
            input_value="\thello",
            expected_output="\thello",
        ),
        AdversarialCase(
            case_id="I3",
            rationale="trailing newline must be preserved",
            input_value="hello\n",
            expected_output="hello\n",
        ),
        AdversarialCase(
            case_id="I4",
            rationale="integer type must be preserved",
            input_value=123,
            expected_output=123,
        ),
        AdversarialCase(
            case_id="I5",
            rationale="negative integer type must be preserved",
            input_value=-1,
            expected_output=-1,
        ),
        AdversarialCase(
            case_id="I6",
            rationale="boolean type must be preserved",
            input_value=True,
            expected_output=True,
        ),
        AdversarialCase(
            case_id="I7",
            rationale="list value and type must be preserved",
            input_value=[1, 2, 3],
            expected_output=[1, 2, 3],
        ),
        AdversarialCase(
            case_id="I8",
            rationale="dictionary value and type must be preserved",
            input_value={"key": "value"},
            expected_output={"key": "value"},
        ),
    ]


def _generic_candidates():
    """
    Generic adversarial cases for tasks where the expected
    output cannot safely be inferred.

    These cases intentionally have no expected_output.
    """

    return [
        AdversarialCase(
            case_id="A1",
            rationale="representative input",
            input_value="hello",
        ),
        AdversarialCase(
            case_id="A2",
            rationale="empty input boundary",
            input_value="",
        ),
        AdversarialCase(
            case_id="A3",
            rationale="single-character boundary",
            input_value="x",
        ),
        AdversarialCase(
            case_id="A4",
            rationale="whitespace boundary",
            input_value=" ",
        ),
        AdversarialCase(
            case_id="A5",
            rationale="unicode boundary",
            input_value="café",
        ),
        AdversarialCase(
            case_id="A6",
            rationale="long-input boundary",
            input_value="x" * 128,
        ),
        AdversarialCase(
            case_id="A7",
            rationale="numeric-looking string",
            input_value="123",
        ),
        AdversarialCase(
            case_id="A8",
            rationale="newline boundary",
            input_value="hello\n",
        ),
    ]


def _prioritize_generic(candidates, trace):
    """
    Prioritize generic cases using explicit task signals.
    """

    text = (
        trace.task
        + " "
        + " ".join(trace.requirements)
    ).lower()

    prioritized = list(candidates)

    def move_to_front(case_id):

        for index, case in enumerate(prioritized):

            if case.case_id == case_id:

                selected = prioritized.pop(index)

                prioritized.insert(
                    0,
                    selected,
                )

                return

    if (
        "empty" in text
        or "missing" in text
        or "blank" in text
    ):
        move_to_front("A2")

    if (
        "unicode" in text
        or "utf-8" in text
        or "character encoding" in text
    ):
        move_to_front("A5")

    if (
        "newline" in text
        or "line break" in text
        or "\\n" in text
    ):
        move_to_front("A8")

    if (
        "whitespace" in text
        or "trim" in text
        or "strip" in text
    ):
        move_to_front("A4")

    if (
        "long" in text
        or "length" in text
        or "large input" in text
        or "maximum" in text
    ):
        move_to_front("A6")

    return prioritized


def generate_cases(trace, budget=8):
    """
    Generate deterministic adversarial verification cases.

    Rules:

    1. Never exceed the requested budget.
    2. Never duplicate declared test inputs.
    3. Identity tasks receive type-preserving and
       transformation-sensitive counterexamples.
    4. Generic tasks receive boundary-focused inputs.
    5. Expected outputs are supplied only when the task
       semantics establish them directly.
    """

    try:
        budget = int(budget)
    except (
        TypeError,
        ValueError,
    ):
        budget = 8

    if budget <= 0:
        return []

    existing_inputs = _existing_inputs(
        trace
    )

    if _is_identity_task(trace):

        candidates = _identity_candidates()

    else:

        candidates = _generic_candidates()

        candidates = _prioritize_generic(
            candidates,
            trace,
        )

    unique = []

    seen = set(
        existing_inputs
    )

    for case in candidates:

        key = repr(
            case.input_value
        )

        if key in seen:
            continue

        seen.add(key)

        unique.append(case)

        if len(unique) >= budget:
            break

    return unique