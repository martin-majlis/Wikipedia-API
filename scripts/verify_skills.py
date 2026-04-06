#!/usr/bin/env python3
"""
Verify all code samples in the SKILLS directory execute successfully.

This script discovers and runs all async.py, sync.py, and cli.sh files
in the SKILLS directory using uv run, then reports comprehensive statistics.
"""

import pathlib
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
from dataclasses import dataclass


@dataclass
class TestResult:
    """Result of executing a skill script."""

    file_path: str
    skill_dir: str
    script_type: str
    success: bool
    output: str
    error: str
    exit_code: int
    execution_time: float


def find_test_files() -> list[pathlib.Path]:
    """Find all target files in SKILLS directory."""
    skills_dir = pathlib.Path("SKILLS")
    if not skills_dir.exists():
        print(f"Error: SKILLS directory not found at {skills_dir}")
        sys.exit(1)

    target_files = []
    for pattern in ["**/async.py", "**/sync.py", "**/cli.sh"]:
        target_files.extend(skills_dir.glob(pattern))

    return sorted(target_files)


def execute_script(script_path: pathlib.Path) -> TestResult:
    """Execute a script with uv run and capture results."""
    start_time = time.time()
    skill_dir = script_path.parent
    skill_name = skill_dir.name
    script_name = script_path.stem  # filename without extension
    script_type = script_path.suffix[1:] if script_path.suffix != ".sh" else "sh"

    # Prepare log file paths
    stdout_log = skill_dir / f"{script_name}.stdout.log"
    stderr_log = skill_dir / f"{script_name}.stderr.log"

    try:
        # Change to script's directory for execution
        cwd = skill_dir

        # Determine command based on file type
        if script_path.suffix == ".sh":
            # Shell scripts need bash
            cmd = ["uv", "run", "bash", str(script_path.name)]
        else:
            # Python scripts can run directly
            cmd = ["uv", "run", str(script_path.name)]

        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=300,  # 300 second timeout per script
        )

        execution_time = time.time() - start_time

        # Save stdout and stderr to log files
        try:
            stdout_log.write_text(result.stdout, encoding="utf-8")
        except Exception as e:
            print(f"Warning: Failed to write stdout log {stdout_log}: {e}")

        try:
            stderr_log.write_text(result.stderr, encoding="utf-8")
        except Exception as e:
            print(f"Warning: Failed to write stderr log {stderr_log}: {e}")

        return TestResult(
            file_path=str(script_path),
            skill_dir=skill_name,
            script_type=script_type,
            success=result.returncode == 0,
            output=result.stdout,
            error=result.stderr,
            exit_code=result.returncode,
            execution_time=execution_time,
        )

    except subprocess.TimeoutExpired:
        execution_time = time.time() - start_time

        # Save partial output for timeout case
        error_msg = "Script execution timed out after 30 seconds"
        try:
            stdout_log.write_text("", encoding="utf-8")  # Empty stdout for timeout
        except Exception as e:
            print(f"Warning: Failed to write stdout log {stdout_log}: {e}")

        try:
            stderr_log.write_text(error_msg, encoding="utf-8")
        except Exception as e:
            print(f"Warning: Failed to write stderr log {stderr_log}: {e}")

        return TestResult(
            file_path=str(script_path),
            skill_dir=skill_name,
            script_type=script_type,
            success=False,
            output="",
            error=error_msg,
            exit_code=124,
            execution_time=execution_time,
        )
    except Exception as e:
        execution_time = time.time() - start_time

        # Save error information
        error_msg = f"Failed to execute script: {e}"
        try:
            stdout_log.write_text("", encoding="utf-8")  # Empty stdout for error
        except Exception as log_e:
            print(f"Warning: Failed to write stdout log {stdout_log}: {log_e}")

        try:
            stderr_log.write_text(error_msg, encoding="utf-8")
        except Exception as log_e:
            print(f"Warning: Failed to write stderr log {stderr_log}: {log_e}")

        return TestResult(
            file_path=str(script_path),
            skill_dir=skill_name,
            script_type=script_type,
            success=False,
            output="",
            error=error_msg,
            exit_code=1,
            execution_time=execution_time,
        )


def print_progress(current: int, total: int, result: TestResult = None):
    """Print progress update."""
    if result:
        status = "✓" if result.success else "✗"
        relative_path = result.file_path.replace("SKILLS/", "")
        print(
            f"{status} {relative_path} ({result.script_type}) - {result.execution_time:.2f}s"
            " (logs saved)"
        )
    else:
        print(f"Progress: {current}/{total}")


def print_summary(results: list[TestResult]):
    """Print comprehensive results summary."""
    total = len(results)
    successful = sum(1 for r in results if r.success)
    failed = total - successful
    success_rate = (successful / total * 100) if total > 0 else 0

    print("\n" + "=" * 50)
    print("RESULTS SUMMARY")
    print("=" * 50)
    print(f"Total scripts: {total}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Success rate: {success_rate:.1f}%")

    # Group by skill directory
    by_skill: dict[str, list[TestResult]] = {}
    for result in results:
        if result.skill_dir not in by_skill:
            by_skill[result.skill_dir] = []
        by_skill[result.skill_dir].append(result)

    print("\nResults by skill directory:")
    print("-" * 30)
    for skill_dir, skill_results in sorted(by_skill.items()):
        skill_success = sum(1 for r in skill_results if r.success)
        skill_total = len(skill_results)
        status = "✓" if skill_success == skill_total else "✗"
        print(f"{status} {skill_dir}: {skill_success}/{skill_total} passed")

    if failed > 0:
        print("\nFailed scripts:")
        print("-" * 30)
        for result in results:
            if not result.success:
                relative_path = result.file_path.replace("SKILLS/", "")
                print(f"✗ {relative_path}")
                if result.error.strip():
                    print(f"   Error: {result.error.strip()}")
                if result.output.strip():
                    # Show first line of output
                    first_line = result.output.strip().split("\n")[0]
                    print(f"   Output: {first_line}")

    # Execution time statistics
    total_time = sum(r.execution_time for r in results)
    avg_time = total_time / total if total > 0 else 0
    print("\nExecution time statistics:")
    print("-" * 30)
    print(f"Total time: {total_time:.2f}s")
    print(f"Average time: {avg_time:.2f}s")

    # Group by script type
    by_type: dict[str, list[TestResult]] = {}
    for result in results:
        if result.script_type not in by_type:
            by_type[result.script_type] = []
        by_type[result.script_type].append(result)

    print("\nResults by script type:")
    print("-" * 30)
    for script_type, type_results in sorted(by_type.items()):
        type_success = sum(1 for r in type_results if r.success)
        type_total = len(type_results)
        print(f"{script_type}: {type_success}/{type_total} passed")


def main():
    """Main verification script."""
    print("SKILLS Verification Script")
    print("=" * 50)

    # Find all test files
    test_files = find_test_files()
    if not test_files:
        print("No test files found in SKILLS directory")
        return 0

    print(f"Found {len(test_files)} skill scripts to verify")
    print()

    # Execute scripts with some parallelism but not too much
    results = []
    max_workers = min(4, len(test_files))  # Limit to 4 concurrent executions

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all jobs
        future_to_file = {executor.submit(execute_script, f): f for f in test_files}

        # Collect results as they complete
        completed = 0
        for future in as_completed(future_to_file):
            result = future.result()
            results.append(result)
            completed += 1
            print_progress(completed, len(test_files), result)

    # Sort results for consistent output
    results.sort(key=lambda r: (r.skill_dir, r.script_type))

    # Print summary
    print_summary(results)

    # Return appropriate exit code
    failed_count = sum(1 for r in results if not r.success)
    if failed_count > 0:
        print(f"\n❌ Verification failed: {failed_count} scripts failed")
        return 1
    else:
        print("\n✅ All scripts passed verification!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
