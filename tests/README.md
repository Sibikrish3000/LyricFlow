# LyricFlow Tests

This directory contains comprehensive unit tests and integration tests for the LyricFlow package.

## Test Structure

```
tests/
├── conftest.py              # Pytest fixtures and configuration
├── test_config.py           # Configuration management tests
├── test_romanizer.py        # Romanization functionality tests
├── test_audio_handler.py    # Audio file handling tests
├── test_lyrics_sync.py      # Lyrics synchronization tests
├── test_integration.py      # End-to-end integration tests
└── test_lyricflow.py        # Legacy manual tests
```

## Running Tests

### Run All Tests
```bash
pytest
```

### Run Specific Test File
```bash
pytest tests/test_config.py
pytest tests/test_romanizer.py
```

### Run Specific Test Class
```bash
pytest tests/test_config.py::TestAPIConfig
pytest tests/test_romanizer.py::TestLocalRomanizer
```

### Run Specific Test
```bash
pytest tests/test_config.py::TestAPIConfig::test_default_values
```

### Run with Coverage
```bash
pytest --cov=lyricflow --cov-report=html
```

This generates an HTML coverage report in `htmlcov/index.html`.

### Run with Verbose Output
```bash
pytest -v
```

### Run Only Fast Tests (Skip Slow Tests)
```bash
pytest -m "not slow"
```

### Run Only Unit Tests
```bash
pytest -m unit
```

### Run Only Integration Tests
```bash
pytest -m integration
```

## Test Categories

### Unit Tests

**test_config.py**
- Configuration loading from YAML
- Environment variable override
- Default values
- Config validation

**test_romanizer.py**
- Local romanization (pykakasi + fugashi)
- AI romanization initialization
- Fallback mechanisms
- Edge cases (particles, special characters)

**test_audio_handler.py**
- Metadata extraction
- LRC embedding
- Format support (MP3, M4A, FLAC, OGG)
- Error handling

**test_lyrics_sync.py**
- LRC file discovery
- LRC parsing and romanization
- Complete workflow
- Error handling

### Integration Tests

**test_integration.py**
- End-to-end workflows
- Component integration
- Batch processing
- Real file processing

## Test Fixtures

Defined in `conftest.py`:

- `temp_dir` - Temporary directory for test files
- `sample_lrc_content` - Sample LRC file content
- `sample_lrc_file` - Creates a temporary LRC file
- `mock_config` - Mock configuration object
- `test_audio_files` - List of available test audio files

## Test Data

The `tests/` directory includes sample audio files:
- `01 Shogeki.m4a` / `01 Shogeki.lrc`
- `16 Soul's Refrain.m4a` / `16 Soul's Refrain.lrc`

These files are used for integration testing with real audio.

## Writing New Tests

### Basic Test Structure

```python
import pytest
from lyricflow.core.romanizer import Romanizer

class TestMyFeature:
    """Test suite for my feature."""
    
    def test_basic_functionality(self):
        """Test basic functionality."""
        romanizer = Romanizer()
        result = romanizer.romanize("こんにちは")
        assert len(result) > 0
```

### Using Fixtures

```python
def test_with_config(mock_config):
    """Test using mock configuration."""
    assert mock_config.api.default_provider == "local"
```

### Parametrized Tests

```python
@pytest.mark.parametrize("input,expected", [
    ("こんにちは", "konnichiwa"),
    ("ありがとう", "arigatō"),
])
def test_multiple_cases(input, expected):
    romanizer = Romanizer()
    result = romanizer.romanize(input)
    assert expected in result.lower()
```

### Skip Tests Conditionally

```python
@pytest.mark.skipif(not Path("tests/file.m4a").exists(),
                    reason="Test file not available")
def test_with_real_file():
    # Test code
    pass
```

## Coverage Goals

Target: 80%+ code coverage

Current coverage by module:
- `lyricflow.utils.config`: Target 90%+
- `lyricflow.core.romanizer`: Target 85%+
- `lyricflow.core.audio_handler`: Target 80%+
- `lyricflow.core.lyrics_sync`: Target 85%+

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -e .[dev]
      - run: pytest --cov=lyricflow
```

## Testing Best Practices

1. **Test Naming**: Use descriptive names that explain what is being tested
2. **One Assert Per Test**: Focus each test on a single behavior
3. **Arrange-Act-Assert**: Structure tests clearly
4. **Use Fixtures**: Reuse common setup code
5. **Mock External Services**: Don't make real API calls in tests
6. **Test Edge Cases**: Empty inputs, invalid data, boundary conditions
7. **Document Complex Tests**: Add docstrings explaining what and why

## Mocking External Services

For testing AI romanization without API calls:

```python
def test_ai_romanization(mocker):
    """Test AI romanization with mocked API."""
    mock_response = mocker.Mock()
    mock_response.choices[0].message.content = "konnichiwa"
    
    mocker.patch('openai.ChatCompletion.create', return_value=mock_response)
    
    # Test code
```

## Troubleshooting

### Tests Hanging
- Check for missing mocks on network calls
- Verify timeout settings
- Use `pytest -s` to see print output

### Import Errors
- Ensure package is installed: `pip install -e .`
- Check PYTHONPATH
- Verify virtual environment is activated

### Fixture Not Found
- Check `conftest.py` is present
- Verify fixture name spelling
- Ensure fixture scope is correct

## Contributing Tests

When adding new features:
1. Write tests first (TDD approach)
2. Ensure all tests pass: `pytest`
3. Check coverage: `pytest --cov`
4. Add integration tests for new workflows
5. Update this README if adding new test categories
