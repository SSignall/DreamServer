#!/bin/sh
# VAD patch for Speaches STT service

STT_FILE="/home/ubuntu/speaches/src/speaches/routers/stt.py"
PATCH_MARKER="DREAM_PATCHED"

# Check if file exists - explicit failure mode
check_file() {
    if [ ! -f "$STT_FILE" ]; then
        echo "ERROR: Target file does not exist: $STT_FILE" >&2
        echo "Container may not function correctly without patch" >&2
        return 1
    fi
    return 0
}

# Apply patch idempotently
apply_patch() {
    # Already patched? Skip to prevent duplicate insertion on restart
    if grep -q "$PATCH_MARKER" "$STT_FILE" 2>/dev/null; then
        echo "Patch already applied (marker found)"
        return 0
    fi

    # Check if target pattern exists (robust: allow whitespace variations)
    if ! grep -qE 'vad_filter\s*=\s*effective_vad_filter' "$STT_FILE" 2>/dev/null; then
        echo "WARNING: Target pattern not found in $STT_FILE" >&2
        echo "Patch may not be needed or upstream changed" >&2
        return 0
    fi

    # Apply patch with flexible whitespace matching
    # Uses perl for more robust pattern matching than sed
    if command -v perl >/dev/null 2>&1; then
        perl -i -pe "s/(vad_filter\s*=\s*effective_vad_filter)/\$1,\n            vad_parameters={\"threshold\": 0.3, \"min_silence_duration_ms\": 400, \"min_speech_duration_ms\": 50, \"speech_pad_ms\": 200},  # $PATCH_MARKER/" "$STT_FILE"
    else
        # Fallback to sed with more flexible pattern
        sed -i -E "s/vad_filter[[:space:]]*=[[:space:]]*effective_vad_filter[[:space:]]*,?[[:space:]]*/vad_filter = effective_vad_filter,\n            vad_parameters={\\"threshold\\": 0.3, \\"min_silence_duration_ms\\": 400, \\"min_speech_duration_ms\\": 50, \\"speech_pad_ms\\": 200},  # $PATCH_MARKER/" "$STT_FILE"
    fi

    # Verify patch applied
    if grep -q "$PATCH_MARKER" "$STT_FILE" 2>/dev/null; then
        echo "Patch applied successfully"
        return 0
    else
        echo "ERROR: Patch may not have been applied correctly" >&2
        return 1
    fi
}

# Check file is writable before patching
check_writable() {
    if [ ! -w "$STT_FILE" ]; then
        echo "ERROR: Target file is not writable: $STT_FILE" >&2
        return 1
    fi
    return 0
}

# Main
# Check file exists, is writable, and has target pattern before patching
if check_file && check_writable && grep -qE 'vad_filter\s*=\s*effective_vad_filter' "$STT_FILE" 2>/dev/null; then
    apply_patch
else
    echo "WARNING: Patch skipped (file missing, not writable, or pattern not found)" >&2
fi

# Always start uvicorn (patch failure is non-fatal but logged)
exec uvicorn --factory speaches.main:create_app --host 0.0.0.0 --port 8000
