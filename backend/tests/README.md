# Champa Backend Tests

## Running Tests

### Setup
First, ensure you have installed all dependencies:
```bash
pip install -r requirements.txt
```

### Run All Tests
```bash
pytest
```

### Run Property-Based Tests Only
```bash
pytest -m property
```

### Run Specific Test File
```bash
pytest tests/test_message_normalization_properties.py -v
```

### Run with Coverage
```bash
pytest --cov=app --cov-report=html
```

## Property-Based Tests

Property-based tests use Hypothesis to generate random test data and verify that properties hold across all inputs.

### Message Normalization Properties (test_message_normalization_properties.py)

Tests the following properties from the design document:

- **Property 12**: All messages are normalized (Requirements 4.1)
- **Property 13**: Normalization preserves platform identifier (Requirements 4.2)
- **Property 14**: Normalization extracts common fields (Requirements 4.3)
- **Property 15**: Normalization preserves metadata (Requirements 4.4)

Each property test runs 100 iterations by default with randomly generated messages from Gmail, Slack, and Calendar platforms.

## Test Structure

- `tests/` - All test files
- `tests/unit/` - Unit tests (to be created)
- `tests/integration/` - Integration tests (to be created)
- `tests/property/` - Property-based tests (can be organized here)

## Notes

- Property tests are marked with `@pytest.mark.property`
- Each property test includes a docstring with the feature name, property number, and validated requirements
- Tests use Hypothesis strategies to generate valid test data for each platform
