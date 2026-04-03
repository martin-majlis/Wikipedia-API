#!/usr/bin/env bash
# Wrapper script to run the skills verification

echo "Running skills verification..."
uv run verify_skills.py
exit_code=$?

if [ $exit_code -eq 0 ]; then
    echo "✅ All skills verified successfully!"
else
    echo "❌ Some skills failed verification."
fi

exit $exit_code
