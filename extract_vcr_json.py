#!/usr/bin/env python3
"""Extract pure JSON responses from VCR cassette files.

This script processes VCR cassette files and extracts unescaped JSON responses
from interactions[].response.body.string into separate, pretty-printed JSON files.

Usage:
    python extract_vcr_json.py [--input-dir DIR] [--output-dir DIR] [--overwrite] [--verbose]
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Extract JSON responses from VCR cassette files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    %(prog)s                                    # Use default directories
    %(prog)s --input-dir my-cassettes            # Custom input directory
    %(prog)s --output-dir json-output --verbose   # Custom output with details
    %(prog)s --overwrite                         # Overwrite existing files
        """,
    )

    parser.add_argument(
        "--input-dir",
        default="tests/cassettes",
        help="Source directory containing VCR cassette files (default: tests/cassettes)",
    )

    parser.add_argument(
        "--output-dir",
        default="tests/cassettes-responses",
        help="Output directory for extracted JSON files (default: tests/cassettes-response-json)",
    )

    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing output files",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output",
    )

    return parser.parse_args()


def extract_json_from_cassette(
    cassette_path: Path, output_dir: Path, overwrite: bool, verbose: bool
) -> int:
    """Extract JSON responses from a single VCR cassette file.

    Args:
        cassette_path: Path to the VCR cassette file
        output_dir: Directory to write extracted JSON files
        overwrite: Whether to overwrite existing files
        verbose: Whether to print verbose output

    Returns:
        Number of JSON files extracted from this cassette
    """
    try:
        with open(cassette_path, encoding="utf-8") as f:
            cassette_data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        if verbose:
            print(f"Warning: Could not parse {cassette_path}: {e}", file=sys.stderr)
        return 0

    if "interactions" not in cassette_data:
        if verbose:
            print(f"Warning: No 'interactions' found in {cassette_path}", file=sys.stderr)
        return 0

    interactions: list[dict[str, Any]] = cassette_data["interactions"]
    extracted_count = 0

    for index, interaction in enumerate(interactions):
        try:
            # Extract the response body string
            response_body = interaction.get("response", {}).get("body", {}).get("string")
            if not response_body:
                if verbose:
                    print(
                        f"Warning: No response body found in interaction "
                        f"{index} of {cassette_path}",
                        file=sys.stderr,
                    )
                continue

            # Parse the escaped JSON string
            try:
                json_data = json.loads(response_body)
            except json.JSONDecodeError as e:
                if verbose:
                    print(
                        f"Warning: Could not parse JSON in interaction "
                        f"{index} of {cassette_path}: {e}",
                        file=sys.stderr,
                    )
                continue

            # Generate output filename
            base_name = cassette_path.stem  # Remove .json extension
            output_filename = f"{base_name}_{index}.json"
            output_path = output_dir / output_filename

            # Check if file exists
            if output_path.exists() and not overwrite:
                if verbose:
                    print(
                        f"Skipping {output_filename} (already exists, use --overwrite to replace)",
                        file=sys.stderr,
                    )
                continue

            # Write pretty-printed JSON
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)

            extracted_count += 1
            if verbose:
                print(f"Extracted: {output_filename}")

        except Exception as e:
            if verbose:
                print(
                    f"Warning: Error processing interaction {index} of {cassette_path}: {e}",
                    file=sys.stderr,
                )
            continue

    return extracted_count


def main() -> None:
    """Main entry point."""
    args = parse_arguments()

    # Convert paths to Path objects
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)

    # Validate input directory
    if not input_dir.exists():
        print(f"Error: Input directory '{input_dir}' does not exist", file=sys.stderr)
        sys.exit(1)

    if not input_dir.is_dir():
        print(f"Error: '{input_dir}' is not a directory", file=sys.stderr)
        sys.exit(1)

    # Create output directory if needed
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        print(f"Error: Could not create output directory '{output_dir}': {e}", file=sys.stderr)
        sys.exit(1)

    # Find all JSON files in input directory
    cassette_files = list(input_dir.glob("*.json"))
    if not cassette_files:
        print(f"No JSON files found in '{input_dir}'", file=sys.stderr)
        sys.exit(0)

    # Process each cassette file
    total_extracted = 0
    processed_files = 0

    for cassette_path in sorted(cassette_files):
        if args.verbose:
            print(f"Processing: {cassette_path.name}")

        extracted = extract_json_from_cassette(
            cassette_path, output_dir, args.overwrite, args.verbose
        )
        total_extracted += extracted
        processed_files += 1

        if args.verbose:
            print(f"  Extracted {extracted} JSON response(s)")

    # Print summary
    print(f"Processed {processed_files} cassette file(s)")
    print(f"Extracted {total_extracted} JSON response(s) to '{output_dir}'")

    if total_extracted == 0:
        print("Warning: No JSON responses were extracted", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
