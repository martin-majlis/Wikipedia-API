# VCR JSON Extractor

This utility extracts pure JSON responses from VCR cassette files, eliminating the need to handle escaped JSON strings.

## Purpose

VCR cassettes store HTTP responses as escaped JSON strings in `interactions[].response.body.string`. This makes it difficult to work with the actual API responses. The extractor script converts these to clean, readable JSON files.

## Usage

### Command Line

```bash
# Use default directories (tests/cassettes -> tests/cassettes-json)
python extract_vcr_json.py

# Custom directories
python extract_vcr_json.py --input-dir my-cassettes --output-dir json-output

# Verbose output
python extract_vcr_json.py --verbose

# Overwrite existing files
python extract_vcr_json.py --overwrite
```

### Makefile Target

```bash
# Extract JSON from all cassettes (overwrites existing files)
make extract-vcr-json
```

## Output Structure

The script creates a flat directory structure in `tests/cassettes-json/`:

```
tests/cassettes-json/
├── TestVcrAsyncPageExistence.test_exists_true_0.json
├── TestVcrAsyncPageExistence.test_exists_false_0.json
├── TestVcrAsyncPageExtractProps.test_summary_0.json
├── TestVcrWikiCoordinates.test_default_0.json
└── ...
```

### File Naming

- **Format**: `{test_name}_{interaction_index}.json`
- **Example**: `TestVcrWikiImages.test_default_0.json`, `TestVcrWikiImages.test_default_1.json`
- **Multiple responses**: When a cassette contains multiple HTTP interactions, each gets its own file with increasing index

## Features

- **Clean JSON**: Extracts unescaped, pretty-printed JSON responses
- **Multiple interactions**: Handles cassettes with multiple HTTP requests/responses
- **Error handling**: Gracefully skips malformed files and interactions
- **Verbose output**: Detailed processing information with `--verbose`
- **Overwrite protection**: Won't overwrite existing files unless `--overwrite` is specified

## Command Line Options

| Option         | Default                | Description                                    |
| -------------- | ---------------------- | ---------------------------------------------- |
| `--input-dir`  | `tests/cassettes`      | Source directory containing VCR cassette files |
| `--output-dir` | `tests/cassettes-json` | Output directory for extracted JSON files      |
| `--overwrite`  | `false`                | Overwrite existing output files                |
| `--verbose`    | `false`                | Enable detailed processing output              |

## Examples

### Before Extraction (VCR Cassette)

```json
{
  "version": 1,
  "interactions": [
    {
      "request": { ... },
      "response": {
        "status": { "code": 200, "message": "OK" },
        "headers": { ... },
        "body": {
          "string": "{\"batchcomplete\":\"\",\"query\":{\"pages\":{\"23862\":{\"pageid\":23862,\"title\":\"Python (programming language)\"}}}"
        }
      }
    }
  ]
}
```

### After Extraction (Clean JSON)

```json
{
  "batchcomplete": "",
  "query": {
    "pages": {
      "23862": {
        "pageid": 23862,
        "title": "Python (programming language)"
      }
    }
  }
}
```

## Integration

The extractor integrates seamlessly with the existing test infrastructure:

- **VCR Tests**: Works with all existing `@pytest.mark.vcr` tests
- **CI/CD**: Can be added to build pipelines
- **Development**: Easy way to inspect actual API responses during development

## Error Handling

The script handles various error conditions gracefully:

- **Malformed cassettes**: Skipped with warning
- **Missing interactions**: Reported with warning
- **JSON parsing errors**: Skipped with warning
- **File system errors**: Clear error messages and exit codes

## Statistics

When run, the script reports:

```
Processed 247 cassette file(s)
Extracted 349 JSON response(s) to 'tests/cassettes-json'
```

This helps you understand how many HTTP interactions were captured across your test suite.
