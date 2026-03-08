"""
=== GENERATED TEST FILE — NEEDS REVIEW ===
Generated: 2026-03-08T02:35:50.591992+00:00
Source: extensions/services/bark/server.py
Generator: Qwen3-Coder (local GPU)

This file was auto-generated and has NOT been reviewed or run.
Review before using. May need fixture adjustments or mock updates.
================================================================
"""

import pytest
import base64
import io
import threading
from unittest.mock import patch, MagicMock, call
from fastapi.testclient import TestClient
from fastapi import HTTPException

# Import the module under test
from extensions.services.bark.server import (
    app,
    TTSRequest,
    TTSResponse,
    _load_models,
    _generate_audio_sync,
    _generate_audio_stream_sync,
    VALID_FORMATS,
    MAX_TEXT_LENGTH,
    _executor,
    _models_loaded,
    _model_lock,
)


# Fixtures
@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_bark_generate_audio():
    with patch("extensions.services.bark.server.generate_audio") as mock:
        # Generate a simple 1-second audio array at 24kHz
        import numpy as np
        audio = np.zeros(24000, dtype=np.float32)
        mock.return_value = audio
        yield mock


@pytest.fixture
def mock_bark_preload_models():
    with patch("extensions.services.bark.server.preload_models") as mock:
        yield mock


@pytest.fixture
def mock_soundfile_write():
    with patch("extensions.services.bark.server.sf.write") as mock:
        # Simulate writing to buffer
        def side_effect(buf, audio_array, sample_rate, format=None):
            # Simulate writing by just storing data
            buf.write(b"fake_audio_data")
        mock.side_effect = side_effect
        yield mock


@pytest.fixture
def reset_model_state():
    """Reset global model state before each test"""
    global _models_loaded
    original = _models_loaded
    _models_loaded = False
    yield
    # Don't restore - keep state clean for other tests


# Tests for /health endpoint
def test_health_initial(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["models_loaded"] is False


def test_health_after_generation(client, mock_bark_generate_audio, mock_bark_preload_models, reset_model_state):
    # First request loads models
    response = client.post("/tts", json={"text": "Hello world"})
    assert response.status_code == 200
    
    # Now check health
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["models_loaded"] is True


# Tests for /tts endpoint
def test_tts_success(client, mock_bark_generate_audio, mock_bark_preload_models, mock_soundfile_write, reset_model_state):
    response = client.post("/tts", json={
        "text": "Hello world",
        "voice_preset": "v2/en_speaker_6",
        "output_format": "wav"
    })
    assert response.status_code == 200
    data = response.json()
    assert "audio_base64" in data
    assert data["sample_rate"] == 24000  # Assuming SAMPLE_RATE=24000
    assert data["format"] == "wav"
    # Verify base64 decodes to something
    decoded = base64.b64decode(data["audio_base64"])
    assert len(decoded) > 0


def test_tts_default_values(client, mock_bark_generate_audio, mock_bark_preload_models, mock_soundfile_write, reset_model_state):
    response = client.post("/tts", json={"text": "Hello world"})
    assert response.status_code == 200
    # Verify default voice_preset and output_format were used
    assert mock_bark_generate_audio.call_args[1]["history_prompt"] == "v2/en_speaker_6"


def test_tts_invalid_format(client):
    response = client.post("/tts", json={
        "text": "Hello world",
        "output_format": "avi"
    })
    assert response.status_code == 422  # Pydantic validation error


def test_tts_text_too_long(client):
    long_text = "x" * (MAX_TEXT_LENGTH + 1)
    response = client.post("/tts", json={"text": long_text})
    assert response.status_code == 422


def test_tts_empty_text(client):
    response = client.post("/tts", json={"text": ""})
    assert response.status_code == 200  # Empty text is allowed (though Bark might fail)


def test_tts_case_insensitive_format(client, mock_bark_generate_audio, mock_bark_preload_models, mock_soundfile_write, reset_model_state):
    response = client.post("/tts", json={
        "text": "Hello world",
        "output_format": "WAV"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["format"] == "wav"


def test_tts_all_valid_formats(client, mock_bark_generate_audio, mock_bark_preload_models, mock_soundfile_write, reset_model_state):
    for fmt in VALID_FORMATS:
        response = client.post("/tts", json={
            "text": "Hello world",
            "output_format": fmt.lower()
        })
        assert response.status_code == 200


def test_tts_thread_pool_execution(client, mock_bark_generate_audio, mock_bark_preload_models, mock_soundfile_write, reset_model_state):
    # Check that the executor is used
    with patch.object(_executor, 'submit') as mock_submit:
        mock_submit.return_value.result.return_value = {
            "audio_base64": "dGVzdA==",
            "sample_rate": 24000,
            "format": "wav"
        }
        response = client.post("/tts", json={"text": "Hello world"})
        assert response.status_code == 200
        mock_submit.assert_called_once()


def test_tts_validation_error(client):
    response = client.post("/tts", json={
        "text": "Hello world",
        "output_format": "invalid"
    })
    assert response.status_code == 422
    assert "output_format" in response.json()["detail"].lower() or "invalid" in response.json()["detail"].lower()


def test_tts_generation_exception(client, mock_bark_generate_audio, mock_bark_preload_models, reset_model_state):
    # Make generate_audio raise an exception
    mock_bark_generate_audio.side_effect = Exception("Bark error")
    
    response = client.post("/tts", json={"text": "Hello world"})
    assert response.status_code == 500
    assert "TTS generation failed" in response.json()["detail"]


# Tests for /tts/stream endpoint
def test_tts_stream_success(client, mock_bark_generate_audio, mock_bark_preload_models, mock_soundfile_write, reset_model_state):
    response = client.post("/tts/stream", json={
        "text": "Hello world",
        "voice_preset": "v2/en_speaker_6"
    })
    assert response.status_code == 200
    assert response.headers["content-type"] == "audio/wav"
    assert response.headers["content-disposition"] == "attachment; filename=bark_output.wav"
    assert len(response.content) > 0


def test_tts_stream_default_format(client, mock_bark_generate_audio, mock_bark_preload_models, mock_soundfile_write, reset_model_state):
    response = client.post("/tts/stream", json={"text": "Hello world"})
    assert response.status_code == 200
    # Verify it always uses WAV format
    assert mock_soundfile_write.call_args[1]["format"] == "WAV"


def test_tts_stream_validation_error(client):
    response = client.post("/tts/stream", json={
        "text": "Hello world",
        "output_format": "invalid"  # This field doesn't exist in stream endpoint
    })
    # The stream endpoint doesn't accept output_format, so this should be a 422
    assert response.status_code == 422


def test_tts_stream_generation_exception(client, mock_bark_generate_audio, mock_bark_preload_models, reset_model_state):
    mock_bark_generate_audio.side_effect = Exception("Stream error")
    
    response = client.post("/tts/stream", json={"text": "Hello world"})
    assert response.status_code == 500
    assert "TTS generation failed" in response.json()["detail"]


# Tests for /voices endpoint
def test_list_voices(client):
    response = client.get("/voices")
    assert response.status_code == 200
    data = response.json()
    assert "english" in data
    assert "german" in data
    assert "chinese" in data
    assert len(data["english"]) == 10
    assert data["english"][0] == "v2/en_speaker_0"
    assert data["english"][-1] == "v2/en_speaker_9"


# Tests for model loading
def test_load_models_thread_safety(mock_bark_preload_models, reset_model_state):
    # Simulate concurrent requests
    results = []
    errors = []
    
    def load_and_check():
        try:
            _load_models()
            results.append(_models_loaded)
        except Exception as e:
            errors.append(e)
    
    threads = [threading.Thread(target=load_and_check) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
    assert len(errors) ==
