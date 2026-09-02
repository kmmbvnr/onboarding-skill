# Add `--skip-validation` to `dmr_export_schema`

Source: https://github.com/wemake-services/django-modern-rest/issues/1225

The `dmr_export_schema` management command always validates the converted
OpenAPI schema. Some users need to export a schema that has small validation
problems.

Add an optional `--skip-validation` flag. Its default value must be `False`.
Pass the selected value to the schema converter as `skip_validation=`.

Follow the repository contribution rules. Add tests and update the changelog.
