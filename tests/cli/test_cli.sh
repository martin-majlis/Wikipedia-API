#!/usr/bin/env bash
#
# CLI Integration Test Script for wikipedia-api
# ==============================================
#
# This script tests the wikipedia-api command line tool by running all
# supported commands against real Wikipedia pages in multiple languages
# and comparing their output against expected results.
#
# MODES
# -----
#   record   — Run all commands and save their output as expected fixtures.
#              Use this when the CLI output intentionally changes, or when
#              setting up fixtures for the first time.
#
#   verify   — Run all commands and compare their output against previously
#              recorded expected fixtures. Exits with code 1 if any test
#              fails.
#
# USAGE
# -----
#   # Record expected output (run from repository root):
#   bash tests/cli/test_cli.sh record
#
#   # Verify output matches expected:
#   bash tests/cli/test_cli.sh verify
#
#   # Run only tests containing 'geo':
#   bash tests/cli/test_cli.sh verify geo
#
#   # Record only tests containing 'coordinates':
#   bash tests/cli/test_cli.sh record coordinates
#
# PREREQUISITES
# -------------
#   - The wikipedia-api CLI must be installed (pip install -e .)
#   - Internet access is required (tests call live Wikipedia API)
#
# ADDING NEW TESTS
# ----------------
#   1. Add a new entry to the TESTS array below. Format:
#        "<test_name>|<command and arguments>"
#   2. Run in record mode to generate the expected fixture.
#   3. Review the fixture file in tests/cli/expected/<test_name>.txt
#   4. Commit the fixture file.
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXPECTED_DIR="${SCRIPT_DIR}/expected"

# ── Colours for terminal output ─────────────────────────────────────────────

if [ -t 1 ]; then
    GREEN='\033[0;32m'
    RED='\033[0;31m'
    YELLOW='\033[0;33m'
    CYAN='\033[0;36m'
    NC='\033[0m'
else
    GREEN='' RED='' YELLOW='' CYAN='' NC=''
fi

# ── Common CLI parameters ─────────────────────────────────────────────────────
# Define common parameters once for easier maintenance

RETRY_PARAMS="--max-retries 10 --retry-wait 5"
UV_CMD="uv run wikipedia-api"

# ── Test definitions ────────────────────────────────────────────────────────
# Format: "test_name|command args..."
#
# Pages are chosen to be stable and well-known across languages editions.
# Smaller pages are used for commands that produce large output.

TESTS=(
    # ── page command ────────────────────────────────────────────────────────
    "page_en|${UV_CMD} page Earth ${RETRY_PARAMS}"
    "page_en_json|${UV_CMD} page Earth --json ${RETRY_PARAMS}"
    "page_nonexistent|${UV_CMD} page 'NonexistentPage12345' ${RETRY_PARAMS} || true"

    # ── summary command ────────────────────────────────────────────────────
    "summary_en|${UV_CMD} summary Earth ${RETRY_PARAMS}"
    "summary_cs|${UV_CMD} summary Earth --language cs ${RETRY_PARAMS}"
    "summary_de|${UV_CMD} summary Earth --language de ${RETRY_PARAMS}"
    "summary_fr|${UV_CMD} summary Earth --language fr ${RETRY_PARAMS}"
    "summary_es|${UV_CMD} summary Earth --language es ${RETRY_PARAMS}"
    "summary_ja|${UV_CMD} summary Earth --language ja ${RETRY_PARAMS}"
    "summary_zh_cn|${UV_CMD} summary Earth --language zh --variant zh-cn ${RETRY_PARAMS}"
    "summary_zh_tw|${UV_CMD} summary Earth --language zh --variant zh-tw ${RETRY_PARAMS}"
    "summary_ar|${UV_CMD} summary Earth --language ar ${RETRY_PARAMS}"
    "summary_ko|${UV_CMD} summary Earth --language ko ${RETRY_PARAMS}"
    "summary_html|${UV_CMD} summary Earth --extract-format html ${RETRY_PARAMS}"

    # ── text command ─────────────────────────────────────────────────────────
    "text_en|${UV_CMD} text Earth ${RETRY_PARAMS}"
    "text_cs|${UV_CMD} text Earth --language cs ${RETRY_PARAMS}"

    # ── sections command ─────────────────────────────────────────────────────
    "sections_en|${UV_CMD} sections Earth ${RETRY_PARAMS}"
    "sections_en_json|${UV_CMD} sections Earth --json ${RETRY_PARAMS}"
    "sections_de|${UV_CMD} sections Neue_Heimat --language de ${RETRY_PARAMS}"

    # ── section command ──────────────────────────────────────────────────────
    "section_en|${UV_CMD} section Earth 'Etymology' ${RETRY_PARAMS}"
    "section_cs|${UV_CMD} section Země 'Vznik Země' --language cs ${RETRY_PARAMS}"

    # ── links command ────────────────────────────────────────────────────────
    "links_en|${UV_CMD} links Earth ${RETRY_PARAMS}"
    "links_en_json|${UV_CMD} links Earth --json ${RETRY_PARAMS}"

    # ── backlinks command ───────────────────────────────────────────────────
    "backlinks_en|${UV_CMD} backlinks Pluto ${RETRY_PARAMS}"
    "backlinks_en_json|${UV_CMD} backlinks Pluto --json ${RETRY_PARAMS}"

    # ── langlinks command ───────────────────────────────────────────────────
    "langlinks_en|${UV_CMD} langlinks Earth ${RETRY_PARAMS}"
    "langlinks_en_json|${UV_CMD} langlinks Earth --json ${RETRY_PARAMS}"
    "langlinks_fr|${UV_CMD} langlinks Paris --language fr ${RETRY_PARAMS}"

    # ── categories command ──────────────────────────────────────────────────
    "categories_en|${UV_CMD} categories Earth ${RETRY_PARAMS}"
    "categories_en_json|${UV_CMD} categories Earth --json ${RETRY_PARAMS}"
    "categories_de|${UV_CMD} categories Berlin --language de ${RETRY_PARAMS}"

    # ── categorymembers command ─────────────────────────────────────────────
    "categorymembers_en|${UV_CMD} categorymembers Category:Planets ${RETRY_PARAMS}"
    "categorymembers_en_json|${UV_CMD} categorymembers Category:Planets --json ${RETRY_PARAMS}"
    "categorymembers_depth|${UV_CMD} categorymembers Category:Planets --max-level 1 ${RETRY_PARAMS}"

    # ── coordinates command ─────────────────────────────────────────────────
    "coordinates_en|${UV_CMD} coordinates Prague ${RETRY_PARAMS}"
    "coordinates_en_json|${UV_CMD} coordinates Prague --json ${RETRY_PARAMS}"
    "coordinates_primary_all|${UV_CMD} coordinates Prague --primary all ${RETRY_PARAMS}"
    "coordinates_primary_secondary|${UV_CMD} coordinates Prague --primary secondary --json ${RETRY_PARAMS}"

    # ── images command ───────────────────────────────────────────────────────
    "images_en|${UV_CMD} images Prague ${RETRY_PARAMS}"
    "images_en_json|${UV_CMD} images Prague --json ${RETRY_PARAMS}"
    "images_en_imageinfo|${UV_CMD} images Prague --imageinfo ${RETRY_PARAMS}"
    "images_en_imageinfo_json|${UV_CMD} images Prague --imageinfo --json ${RETRY_PARAMS}"
    "images_en_limit|${UV_CMD} images Prague --limit 5 ${RETRY_PARAMS}"
    "images_en_language|${UV_CMD} images Prague --language de ${RETRY_PARAMS}"

    # ── geosearch command ────────────────────────────────────────────────────
    "geosearch_coord|${UV_CMD} geosearch --coord \"51.5074|-0.1278\" ${RETRY_PARAMS}"
    "geosearch_coord_json|${UV_CMD} geosearch --coord \"51.5074|-0.1278\" --json ${RETRY_PARAMS}"
    "geosearch_page|${UV_CMD} geosearch --page \"Big Ben\" --radius 1000 ${RETRY_PARAMS}"
    "geosearch_bbox|${UV_CMD} geosearch --bbox \"51.7|-0.1|51.6|-0.05\" --sort relevance ${RETRY_PARAMS}"
    "geosearch_bbox_json|${UV_CMD} geosearch --bbox \"51.7|-0.1|51.6|-0.05\" --sort distance --json ${RETRY_PARAMS}"
    "geosearch_globe|${UV_CMD} geosearch --coord \"51.5074|-0.1278\" --globe mars --limit 5 ${RETRY_PARAMS}"
    "geosearch_primary|${UV_CMD} geosearch --coord \"51.5074|-0.1278\" --primary all --json ${RETRY_PARAMS}"
    "geosearch_max_dim|${UV_CMD} geosearch --coord \"51.5074|-0.1278\" --max-dim 1000 --sort relevance ${RETRY_PARAMS}"

    # ── random command ───────────────────────────────────────────────────────
    "random_default|${UV_CMD} random ${RETRY_PARAMS}"
    "random_limit|${UV_CMD} random --limit 5 ${RETRY_PARAMS}"
    "random_json|${UV_CMD} random --limit 3 --json ${RETRY_PARAMS}"
    "random_filter_redirects|${UV_CMD} random --filter-redirect all --limit 3 ${RETRY_PARAMS}"
    "random_filter_redirects_json|${UV_CMD} random --filter-redirect redirects --json ${RETRY_PARAMS}"
    "random_size_limits|${UV_CMD} random --min-size 1000 --max-size 10000 --limit 5 ${RETRY_PARAMS}"
    "random_combined|${UV_CMD} random --filter-redirect nonredirects --min-size 500 --limit 2 --json ${RETRY_PARAMS}"

    # ── search command ───────────────────────────────────────────────────────
    "search_en|${UV_CMD} search \"Python programming\" ${RETRY_PARAMS}"
    "search_en_json|${UV_CMD} search \"Python programming\" --json ${RETRY_PARAMS}"
    "search_de|${UV_CMD} search \"Python unterstützt mehrere Programmierparadigmen\" --language de ${RETRY_PARAMS}"
    "search_sort_timestamp|${UV_CMD} search \"Python programming\" --search-sort create_timestamp_desc --limit 5 ${RETRY_PARAMS}"
    "search_sort_random|${UV_CMD} search \"Python programming\" --search-sort random --json ${RETRY_PARAMS}"
    "search_sort_title|${UV_CMD} search \"Python programming\" --search-sort title_natural_asc --limit 3 ${RETRY_PARAMS}"
    "search_sort_links|${UV_CMD} search \"Python programming\" --search-sort incoming_links_desc --json ${RETRY_PARAMS}"

    # ── help & version ──────────────────────────────────────────────────────
    "help_main|${UV_CMD} --help"
    "help_summary|${UV_CMD} summary --help"
    "help_text|${UV_CMD} text --help"
    "help_sections|${UV_CMD} sections --help"
    "help_section|${UV_CMD} section --help"
    "help_links|${UV_CMD} links --help"
    "help_backlinks|${UV_CMD} backlinks --help"
    "help_langlinks|${UV_CMD} langlinks --help"
    "help_categories|${UV_CMD} categories --help"
    "help_categorymembers|${UV_CMD} categorymembers --help"
    "help_coordinates|${UV_CMD} coordinates --help"
    "help_images|${UV_CMD} images --help"
    "help_geosearch|${UV_CMD} geosearch --help"
    "help_random|${UV_CMD} random --help"
    "help_search|${UV_CMD} search --help"
    "help_page|${UV_CMD} page --help"
    "version|${UV_CMD} --version"
)

# ── Non-deterministic tests ────────────────────────────────────────────────
# These tests produce different output on every run (random pages, volatile
# search results).  In verify mode we only check that:
#   - the command exits successfully
#   - the output is non-empty
#   - for JSON tests: the output is valid JSON
#   - for text tests: the line count is within ±50 % of the recorded fixture

NONDETERMINISTIC_TESTS=(
    "images_en_json"
    "images_en_imageinfo_json"
    "random_default"
    "random_limit"
    "random_json"
    "random_filter_redirects"
    "random_filter_redirects_json"
    "random_size_limits"
    "random_combined"
    "search_de"
    "search_en"
    "search_sort_timestamp"
    "search_sort_random"
    "search_sort_title"
    "search_sort_links"
)

is_nondeterministic() {
    local name="$1"
    for nd in "${NONDETERMINISTIC_TESTS[@]}"; do
        if [ "$nd" = "$name" ]; then
            return 0
        fi
    done
    return 1
}

# ── Functions ───────────────────────────────────────────────────────────────

filter_tests() {
    local pattern="$1"
    if [ -z "$pattern" ]; then
        # Return all tests if no pattern provided
        printf '%s\n' "${TESTS[@]}"
        return
    fi

    # Filter tests by name (case-insensitive)
    for entry in "${TESTS[@]}"; do
        local name="${entry%%|*}"
        if echo "$name" | grep -iq "$pattern"; then
            echo "$entry"
        fi
    done
}

usage() {
    echo "Usage: $0 {record|verify} [grep_pattern]"
    echo ""
    echo "  record         — Run all commands and save output as expected fixtures"
    echo "  verify         — Run all commands and compare against expected output"
    echo "  grep_pattern   — Optional pattern to filter tests (e.g., 'geo', 'coordinates')"
    echo ""
    echo "Examples:"
    echo "  $0 record                    # Record all tests"
    echo "  $0 verify                    # Verify all tests"
    echo "  $0 verify geo               # Verify only tests containing 'geo'"
    echo "  $0 record coordinates       # Record only tests containing 'coordinates'"
    exit 1
}

run_test() {
    local name="$1"
    local cmd="$2"
    local error_file="$3"
    local tmp_err
    tmp_err=$(mktemp)
    local output
    # Run the command directly (uv run is now included in the cmd)
    output=$(bash -c "$cmd" 2>"$tmp_err") || true
    # Save stderr to the .error file
    cp "$tmp_err" "$error_file"
    # Print stderr if non-empty
    if [ -s "$tmp_err" ]; then
        echo -e "    ${YELLOW}stderr:${NC}" >&2
        sed 's/^/    /' "$tmp_err" >&2
    fi
    rm -f "$tmp_err"
    echo "$output"
}

strip_whitespace() {
    # Remove leading and trailing whitespace and newlines
    sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' | sed -e '/./,$!d' | sed -e ':a' -e '/^\n*$/{$d;N;ba' -e '}'
}

record_mode() {
    local grep_pattern="$1"
    mkdir -p "${EXPECTED_DIR}"

    # Get filtered tests
    local filtered_tests=()
    while IFS= read -r line; do
        filtered_tests+=("$line")
    done < <(filter_tests "$grep_pattern")
    local total=${#filtered_tests[@]}
    local count=0
    local failed=0
    local failed_names=()

    if [ "$total" -eq 0 ]; then
        if [ -n "$grep_pattern" ]; then
            echo -e "${YELLOW}No tests found matching pattern '${grep_pattern}'${NC}"
        else
            echo -e "${YELLOW}No tests found${NC}"
        fi
        return 0
    fi

    if [ -n "$grep_pattern" ]; then
        echo -e "${CYAN}Recording ${total} test fixtures matching '${grep_pattern}'...${NC}"
    else
        echo -e "${CYAN}Recording ${total} test fixtures...${NC}"
    fi
    echo ""

    for entry in "${filtered_tests[@]}"; do
        local name="${entry%%|*}"
        local cmd="${entry#*|}"
        count=$((count + 1))

        printf "  [%2d/%2d] %-30s " "$count" "$total" "$name"
        local output
        local error_file="${EXPECTED_DIR}/${name}.error"
        output=$(run_test "$name" "$cmd" "$error_file" | strip_whitespace)

        # Only write fixture if output is non-empty
        if [ -n "$output" ]; then
            echo "$output" > "${EXPECTED_DIR}/${name}.txt"
            echo -e "${GREEN}recorded${NC}"
        else
            echo -e "${RED}FAILED${NC} (empty output - fixture not saved)"
            failed=$((failed + 1))
            failed_names+=("$name (empty output)")
            # Remove any existing empty fixture file
            rm -f "${EXPECTED_DIR}/${name}.txt"
        fi
    done

    echo ""
    local passed=$((total - failed))
    echo "───────────────────────────────────────"
    echo -e "  Total:   ${total}"
    echo -e "  Recorded: ${GREEN}${passed}${NC}"
    echo -e "  Failed:  ${RED}${failed}${NC}"
    echo "───────────────────────────────────────"

    if [ ${#failed_names[@]} -gt 0 ]; then
        echo ""
        echo -e "${RED}Failed tests (empty output - fixtures not saved):${NC}"
        for name in "${failed_names[@]}"; do
            echo "  - $name"
        done
        echo ""
        echo -e "${YELLOW}Fix the API issues and re-run recording for these tests.${NC}"
        exit 1
    fi

    echo ""
    echo -e "${GREEN}All ${total} fixtures saved to ${EXPECTED_DIR}/${NC}"
}

verify_mode() {
    local grep_pattern="$1"
    if [ ! -d "${EXPECTED_DIR}" ]; then
        echo -e "${RED}Expected output directory not found: ${EXPECTED_DIR}${NC}"
        echo "Run '$0 record' first to generate expected fixtures."
        exit 1
    fi

    # Get filtered tests
    local filtered_tests=()
    while IFS= read -r line; do
        filtered_tests+=("$line")
    done < <(filter_tests "$grep_pattern")
    local total=${#filtered_tests[@]}

    if [ "$total" -eq 0 ]; then
        if [ -n "$grep_pattern" ]; then
            echo -e "${YELLOW}No tests found matching pattern '${grep_pattern}'${NC}"
        else
            echo -e "${YELLOW}No tests found${NC}"
        fi
        return 0
    fi

    local count=0
    local passed=0
    local failed=0
    local small_mismatch=0
    local missing=0
    local skipped=0
    local failed_names=()
    local mismatched_names=()

    if [ -n "$grep_pattern" ]; then
        echo -e "${CYAN}Verifying ${total} tests matching '${grep_pattern}' against expected output...${NC}"
    else
        echo -e "${CYAN}Verifying ${total} tests against expected output...${NC}"
    fi
    echo ""

    for entry in "${filtered_tests[@]}"; do
        local name="${entry%%|*}"
        local cmd="${entry#*|}"
        count=$((count + 1))

        printf "  [%2d/%2d] %-30s " "$count" "$total" "$name"

        local expected_file="${EXPECTED_DIR}/${name}.txt"
        if [ ! -f "$expected_file" ]; then
            echo -e "${YELLOW}MISSING${NC} (no expected fixture)"
            missing=$((missing + 1))
            failed_names+=("$name (missing fixture)")
            continue
        fi

        if [ ! -s "$expected_file" ]; then
            echo -e "${YELLOW}SKIPPED${NC} (empty expected fixture)"
            skipped=$((skipped + 1))
            continue
        fi

        local error_file="${EXPECTED_DIR}/${name}.error"
        local actual
        actual=$(run_test "$name" "$cmd" "$error_file" | strip_whitespace)

        local expected
        expected=$(cat "$expected_file" | strip_whitespace)

        if is_nondeterministic "$name"; then
            # Weak check: non-empty output + format validation
            if [ -z "$actual" ]; then
                echo -e "${RED}FAIL${NC} (empty output)"
                failed=$((failed + 1))
                failed_names+=("$name")
            elif [[ "$name" == *_json ]]; then
                # Validate JSON structure
                if echo "$actual" | python3 -m json.tool > /dev/null 2>&1; then
                    echo -e "${GREEN}PASS${NC} (non-deterministic, valid JSON)"
                    passed=$((passed + 1))
                else
                    echo -e "${RED}FAIL${NC} (invalid JSON)"
                    failed=$((failed + 1))
                    failed_names+=("$name")
                fi
            else
                # Check line count is within ±50% of fixture
                local lines_actual
                lines_actual=$(echo "$actual" | wc -l | tr -d ' ')
                local lines_expected
                lines_expected=$(echo "$expected" | wc -l | tr -d ' ')
                if [ "$lines_expected" -eq 0 ]; then
                    echo -e "${GREEN}PASS${NC} (non-deterministic, non-empty)"
                    passed=$((passed + 1))
                else
                    local lo=$(( lines_expected / 2 ))
                    local hi=$(( lines_expected * 3 / 2 ))
                    if [ "$lines_actual" -ge "$lo" ] && [ "$lines_actual" -le "$hi" ]; then
                        echo -e "${GREEN}PASS${NC} (non-deterministic, ${lines_actual} lines)"
                        passed=$((passed + 1))
                    else
                        echo -e "${RED}FAIL${NC} (expected ~${lines_expected} lines, got ${lines_actual})"
                        failed=$((failed + 1))
                        failed_names+=("$name")
                    fi
                fi
            fi
        elif [ "$actual" = "$expected" ]; then
            echo -e "${GREEN}PASS${NC}"
            passed=$((passed + 1))
        else
            local words_actual
            words_actual=$(echo "$actual" | wc -w | tr -d ' ')
            local words_expected
            words_expected=$(echo "$expected" | wc -w | tr -d ' ')

            if [ "$words_expected" -eq 0 ]; then
                echo -e "${RED}FAIL${NC}"
                failed=$((failed + 1))
                failed_names+=("$name")
            else
                # Calculate if mismatch is small (< 5% word count difference)
                local diff=$(( words_actual - words_expected ))
                local abs_diff=${diff#-}
                local percentage=$(( (abs_diff * 100) / words_expected ))

                if [ "$percentage" -lt 5 ]; then
                    echo -e "${YELLOW}SMALL MISMATCH${NC}"
                    small_mismatch=$((small_mismatch + 1))
                    mismatched_names+=("$name")
                else
                    echo -e "${RED}FAIL${NC}"
                    failed=$((failed + 1))
                    failed_names+=("$name")

                    diff_output=$(diff <(echo "$expected") <(echo "$actual") | head -20) || true
                    echo -e "    ${YELLOW}Diff (first 20 lines):${NC}"
                    echo "${diff_output//^/    }"
                    echo ""
                fi
            fi
        fi
    done

    echo ""
    echo "───────────────────────────────────────"
    echo -e "  Total:   ${total}"
    echo -e "  Passed:  ${GREEN}${passed}${NC}"
    echo -e "  Failed:  ${RED}${failed}${NC}"
    echo -e "  Small Mismatch: ${YELLOW}${small_mismatch}${NC}"
    echo -e "  Skipped: ${YELLOW}${skipped}${NC}"
    echo -e "  Missing: ${YELLOW}${missing}${NC}"
    echo "───────────────────────────────────────"

    if [ ${#failed_names[@]} -gt 0 ] || [ ${#mismatched_names[@]} -gt 0 ]; then
        echo ""
        if [ ${#failed_names[@]} -gt 0 ]; then
            echo -e "${RED}Failed tests:${NC}"
            for name in "${failed_names[@]}"; do
                echo "  - $name"
            done
        fi
        if [ ${#mismatched_names[@]} -gt 0 ]; then
            echo ""
            echo -e "${YELLOW}Tests with small mismatches (<5% word diff):${NC}"
            for name in "${mismatched_names[@]}"; do
                echo "  - $name"
            done
        fi
        echo ""
        if [ -n "$grep_pattern" ]; then
            echo "To update expected output for filtered tests, run: $0 record $grep_pattern"
        else
            echo "To update expected output, run: $0 record"
        fi
        exit 1
    fi

    echo ""
    echo -e "${GREEN}All tests passed.${NC}"
}

# ── Main ────────────────────────────────────────────────────────────────────

if [ $# -lt 1 ] || [ $# -gt 2 ]; then
    usage
fi

MODE="$1"
PATTERN="${2:-}"

case "$MODE" in
    record)
        record_mode "$PATTERN"
        ;;
    verify)
        verify_mode "$PATTERN"
        ;;
    *)
        usage
        ;;
esac
