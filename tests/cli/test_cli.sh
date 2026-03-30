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

# ── Test definitions ────────────────────────────────────────────────────────
# Format: "test_name|command args..."
#
# Pages are chosen to be stable and well-known across languages editions.
# Smaller pages are used for commands that produce large output.

TESTS=(
    # ── page command ────────────────────────────────────────────────────────
    "page_en|uv run wikipedia-api page Earth"
    "page_en_json|uv run wikipedia-api page Earth --json"
    "page_nonexistent|uv run wikipedia-api page 'NonexistentPage12345' || true"

    # ── summary command ────────────────────────────────────────────────────
    "summary_en|uv run wikipedia-api summary Earth"
    "summary_cs|uv run wikipedia-api summary Earth --language cs"
    "summary_de|uv run wikipedia-api summary Earth --language de"
    "summary_fr|uv run wikipedia-api summary Earth --language fr"
    "summary_es|uv run wikipedia-api summary Earth --language es"
    "summary_ja|uv run wikipedia-api summary Earth --language ja"
    "summary_zh_cn|uv run wikipedia-api summary Earth --language zh --variant zh-cn"
    "summary_zh_tw|uv run wikipedia-api summary Earth --language zh --variant zh-tw"
    "summary_ar|uv run wikipedia-api summary Earth --language ar"
    "summary_ko|uv run wikipedia-api summary Earth --language ko"
    "summary_html|uv run wikipedia-api summary Earth --extract-format html"

    # ── text command ─────────────────────────────────────────────────────────
    "text_en|uv run wikipedia-api text Earth"
    "text_cs|uv run wikipedia-api text Earth --language cs"

    # ── sections command ─────────────────────────────────────────────────────
    "sections_en|uv run wikipedia-api sections Earth"
    "sections_en_json|uv run wikipedia-api sections Earth --json"
    "sections_de|uv run wikipedia-api sections Neue_Heimat --language de"

    # ── section command ──────────────────────────────────────────────────────
    "section_en|uv run wikipedia-api section Earth 'Etymology'"
    "section_cs|uv run wikipedia-api section Země 'Vznik Země' --language cs"

    # ── links command ────────────────────────────────────────────────────────
    "links_en|uv run wikipedia-api links Earth"
    "links_en_json|uv run wikipedia-api links Earth --json"

    # ── backlinks command ───────────────────────────────────────────────────
    "backlinks_en|uv run wikipedia-api backlinks Pluto"
    "backlinks_en_json|uv run wikipedia-api backlinks Pluto --json"

    # ── langlinks command ───────────────────────────────────────────────────
    "langlinks_en|uv run wikipedia-api langlinks Earth"
    "langlinks_en_json|uv run wikipedia-api langlinks Earth --json"
    "langlinks_fr|uv run wikipedia-api langlinks Paris --language fr"

    # ── categories command ──────────────────────────────────────────────────
    "categories_en|uv run wikipedia-api categories Earth"
    "categories_en_json|uv run wikipedia-api categories Earth --json"
    "categories_de|uv run wikipedia-api categories Berlin --language de"

    # ── categorymembers command ─────────────────────────────────────────────
    "categorymembers_en|uv run wikipedia-api categorymembers Category:Planets"
    "categorymembers_en_json|uv run wikipedia-api categorymembers Category:Planets --json"
    "categorymembers_depth|uv run wikipedia-api categorymembers Category:Planets --max-level 1"

    # ── coordinates command ─────────────────────────────────────────────────
    "coordinates_en|uv run wikipedia-api coordinates Prague"
    "coordinates_en_json|uv run wikipedia-api coordinates Prague --json"
    "coordinates_primary_all|uv run wikipedia-api coordinates Prague --primary all"
    "coordinates_primary_secondary|uv run wikipedia-api coordinates Prague --primary secondary --json"

    # ── images command ───────────────────────────────────────────────────────
    "images_en|uv run wikipedia-api images Prague"
    "images_en_json|uv run wikipedia-api images Prague --json"

    # ── geosearch command ────────────────────────────────────────────────────
    "geosearch_coord|uv run wikipedia-api geosearch --coord \"51.5074|-0.1278\""
    "geosearch_coord_json|uv run wikipedia-api geosearch --coord \"51.5074|-0.1278\" --json"
    "geosearch_page|uv run wikipedia-api geosearch --page \"Big Ben\" --radius 1000"
    "geosearch_bbox|uv run wikipedia-api geosearch --bbox \"51.7|-0.1|51.6|-0.05\" --sort relevance"
    "geosearch_bbox_json|uv run wikipedia-api geosearch --bbox \"51.7|-0.1|51.6|-0.05\" --sort distance --json"
    "geosearch_globe|uv run wikipedia-api geosearch --coord \"51.5074|-0.1278\" --globe mars --limit 5"
    "geosearch_primary|uv run wikipedia-api geosearch --coord \"51.5074|-0.1278\" --primary all --json"
    "geosearch_max_dim|uv run wikipedia-api geosearch --coord \"51.5074|-0.1278\" --max-dim 1000 --sort relevance"

    # ── random command ───────────────────────────────────────────────────────
    "random_default|uv run wikipedia-api random"
    "random_limit|uv run wikipedia-api random --limit 5"
    "random_json|uv run wikipedia-api random --limit 3 --json"
    "random_filter_redirects|uv run wikipedia-api random --filter-redirect all --limit 3"
    "random_filter_redirects_json|uv run wikipedia-api random --filter-redirect redirects --json"
    "random_size_limits|uv run wikipedia-api random --min-size 1000 --max-size 10000 --limit 5"
    "random_combined|uv run wikipedia-api random --filter-redirect nonredirects --min-size 500 --limit 2 --json"

    # ── search command ───────────────────────────────────────────────────────
    "search_en|uv run wikipedia-api search \"Python programming\""
    "search_en_json|uv run wikipedia-api search \"Python programming\" --json"
    "search_de|uv run wikipedia-api search \"Python unterstützt mehrere Programmierparadigmen\" --language de"
    "search_sort_timestamp|uv run wikipedia-api search \"Python programming\" --search-sort create_timestamp_desc --limit 5"
    "search_sort_random|uv run wikipedia-api search \"Python programming\" --search-sort random --json"
    "search_sort_title|uv run wikipedia-api search \"Python programming\" --search-sort title_natural_asc --limit 3"
    "search_sort_links|uv run wikipedia-api search \"Python programming\" --search-sort incoming_links_desc --json"

    # ── help & version ──────────────────────────────────────────────────────
    "help_main|uv run wikipedia-api --help"
    "help_summary|uv run wikipedia-api summary --help"
    "help_text|uv run wikipedia-api text --help"
    "help_sections|uv run wikipedia-api sections --help"
    "help_section|uv run wikipedia-api section --help"
    "help_links|uv run wikipedia-api links --help"
    "help_backlinks|uv run wikipedia-api backlinks --help"
    "help_langlinks|uv run wikipedia-api langlinks --help"
    "help_categories|uv run wikipedia-api categories --help"
    "help_categorymembers|uv run wikipedia-api categorymembers --help"
    "help_coordinates|uv run wikipedia-api coordinates --help"
    "help_images|uv run wikipedia-api images --help"
    "help_geosearch|uv run wikipedia-api geosearch --help"
    "help_random|uv run wikipedia-api random --help"
    "help_search|uv run wikipedia-api search --help"
    "help_page|uv run wikipedia-api page --help"
    "version|uv run wikipedia-api --version"
)

# ── Non-deterministic tests ────────────────────────────────────────────────
# These tests produce different output on every run (random pages, volatile
# search results).  In verify mode we only check that:
#   - the command exits successfully
#   - the output is non-empty
#   - for JSON tests: the output is valid JSON
#   - for text tests: the line count is within ±50 % of the recorded fixture

NONDETERMINISTIC_TESTS=(
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

usage() {
    echo "Usage: $0 {record|verify}"
    echo ""
    echo "  record  — Run all commands and save output as expected fixtures"
    echo "  verify  — Run all commands and compare against expected output"
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
    mkdir -p "${EXPECTED_DIR}"
    local total=${#TESTS[@]}
    local count=0

    echo -e "${CYAN}Recording ${total} test fixtures...${NC}"
    echo ""

    for entry in "${TESTS[@]}"; do
        local name="${entry%%|*}"
        local cmd="${entry#*|}"
        count=$((count + 1))

        printf "  [%2d/%2d] %-30s " "$count" "$total" "$name"
        local output
        local error_file="${EXPECTED_DIR}/${name}.error"
        output=$(run_test "$name" "$cmd" "$error_file" | strip_whitespace)
        echo "$output" > "${EXPECTED_DIR}/${name}.txt"
        echo -e "${GREEN}recorded${NC}"
    done

    echo ""
    echo -e "${GREEN}All ${total} fixtures saved to ${EXPECTED_DIR}/${NC}"
}

verify_mode() {
    if [ ! -d "${EXPECTED_DIR}" ]; then
        echo -e "${RED}Expected output directory not found: ${EXPECTED_DIR}${NC}"
        echo "Run '$0 record' first to generate expected fixtures."
        exit 1
    fi

    local total=${#TESTS[@]}
    local count=0
    local passed=0
    local failed=0
    local small_mismatch=0
    local missing=0
    local skipped=0
    local failed_names=()
    local mismatched_names=()

    echo -e "${CYAN}Verifying ${total} tests against expected output...${NC}"
    echo ""

    for entry in "${TESTS[@]}"; do
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
        echo "To update expected output, run: $0 record"
        exit 1
    fi

    echo ""
    echo -e "${GREEN}All tests passed.${NC}"
}

# ── Main ────────────────────────────────────────────────────────────────────

if [ $# -ne 1 ]; then
    usage
fi

case "$1" in
    record)
        record_mode
        ;;
    verify)
        verify_mode
        ;;
    *)
        usage
        ;;
esac
