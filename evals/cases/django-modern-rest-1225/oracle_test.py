import json
from io import StringIO

import pytest
from django.core.management import call_command

from dmr.management.commands import dmr_export_schema


@pytest.mark.parametrize(
    ('kwargs', 'expected'),
    [({}, False), ({'skip_validation': True}, True)],
)
def test_skip_validation_reaches_converter(
    monkeypatch: pytest.MonkeyPatch,
    kwargs: dict[str, bool],
    expected: bool,
) -> None:
    observed: list[bool] = []

    class FakeSchema:
        def convert(self, *, skip_validation: bool) -> dict[str, bool]:
            observed.append(skip_validation)
            return {'skip_validation': skip_validation}

    monkeypatch.setattr(dmr_export_schema, 'import_string', lambda _: FakeSchema())

    out = StringIO()
    call_command(
        'dmr_export_schema',
        'server.urls:schema',
        stdout=out,
        **kwargs,
    )

    assert observed == [expected]
    assert json.loads(out.getvalue()) == {'skip_validation': expected}
