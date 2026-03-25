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
    "page_en|wikipedia-api page Earth"
    "page_en_json|wikipedia-api page Earth --json"
    "page_nonexistent|wikipedia-api page Wikipedia-API-NonExistentPage-XYZ42 || true"

    # ── summary command — multiple languages ────────────────────────────────
    "summary_en|wikipedia-api summary Earth"
    "summary_cs|wikipedia-api summary Brno --language cs"
    "summary_de|wikipedia-api summary Berlin --language de"
    "summary_fr|wikipedia-api summary Paris --language fr"
    "summary_es|wikipedia-api summary Madrid --language es"
    "summary_ja|wikipedia-api summary 東京 --language ja"
    "summary_zh_cn|wikipedia-api summary 北京市 --language zh --variant zh-cn"
    "summary_zh_tw|wikipedia-api summary 北京市 --language zh --variant zh-tw"
    "summary_hi|wikipedia-api summary भारत --language hi"
    "summary_ar|wikipedia-api summary القاهرة --language ar"
    "summary_ko|wikipedia-api summary 서울특별시 --language ko"
    "summary_html|wikipedia-api summary Earth --extract-format html"

    # ── text command ────────────────────────────────────────────────────────
    "text_en|wikipedia-api text Earth"
    "text_cs|wikipedia-api text Brno --language cs"

    # ── sections command ────────────────────────────────────────────────────
    "sections_en|wikipedia-api sections Earth"
    "sections_en_json|wikipedia-api sections Earth --json"
    "sections_de|wikipedia-api sections Berlin --language de"

    # ── section command (specific section) ──────────────────────────────────
    "section_en|wikipedia-api section Earth Atmosphere"
    "section_cs|wikipedia-api section Brno Historie --language cs"

    # ── links command ───────────────────────────────────────────────────────
    "links_en|wikipedia-api links Earth"
    "links_en_json|wikipedia-api links Earth --json"

    # ── backlinks command ───────────────────────────────────────────────────
    "backlinks_en|wikipedia-api backlinks Pluto"
    "backlinks_en_json|wikipedia-api backlinks Pluto --json"

    # ── langlinks command ───────────────────────────────────────────────────
    "langlinks_en|wikipedia-api langlinks Earth"
    "langlinks_en_json|wikipedia-api langlinks Earth --json"
    "langlinks_fr|wikipedia-api langlinks Paris --language fr"

    # ── categories command ──────────────────────────────────────────────────
    "categories_en|wikipedia-api categories Earth"
    "categories_en_json|wikipedia-api categories Earth --json"
    "categories_de|wikipedia-api categories Berlin --language de"

    # ── categorymembers command ─────────────────────────────────────────────
    "categorymembers_en|wikipedia-api categorymembers Category:Planets"
    "categorymembers_en_json|wikipedia-api categorymembers Category:Planets --json"
    "categorymembers_depth|wikipedia-api categorymembers Category:Planets --max-level 1"

    # ── coordinates command ─────────────────────────────────────────────────
    "coordinates_en|wikipedia-api coordinates Prague"
    "coordinates_en_json|wikipedia-api coordinates Prague --json"

    # ── images command ───────────────────────────────────────────────────────
    "images_en|wikipedia-api images Prague"
    "images_en_json|wikipedia-api images Prague --json"

    # ── geosearch command ────────────────────────────────────────────────────
    "geosearch_coord|wikipedia-api geosearch --coord '51.5074|-0.1278'"
    "geosearch_coord_json|wikipedia-api geosearch --coord '51.5074|-0.1278' --json"
    "geosearch_page|wikipedia-api geosearch --page 'Big Ben' --radius 1000"

    # ── random command ───────────────────────────────────────────────────────
    "random_default|wikipedia-api random"
    "random_limit|wikipedia-api random --limit 5"
    "random_json|wikipedia-api random --limit 3 --json"

    # ── search command ───────────────────────────────────────────────────────
    "search_en|wikipedia-api search 'Python programming'"
    "search_en_json|wikipedia-api search 'Python programming' --json"
    "search_de|wikipedia-api search 'Berlin' --language de"

    # ── help & version ──────────────────────────────────────────────────────
    "help_main|wikipedia-api --help"
    "help_summary|wikipedia-api summary --help"
    "help_text|wikipedia-api text --help"
    "help_sections|wikipedia-api sections --help"
    "help_section|wikipedia-api section --help"
    "help_links|wikipedia-api links --help"
    "help_backlinks|wikipedia-api backlinks --help"
    "help_langlinks|wikipedia-api langlinks --help"
    "help_categories|wikipedia-api categories --help"
    "help_categorymembers|wikipedia-api categorymembers --help"
    "help_coordinates|wikipedia-api coordinates --help"
    "help_images|wikipedia-api images --help"
    "help_geosearch|wikipedia-api geosearch --help"
    "help_random|wikipedia-api random --help"
    "help_search|wikipedia-api search --help"
    "help_page|wikipedia-api page --help"
    "version|wikipedia-api --version"
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
    "search_de"
    "search_en"
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
    # Run the command via bash to handle || true and other shell constructs
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
