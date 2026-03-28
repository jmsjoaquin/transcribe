from datetime import UTC, datetime

from app.schemas.transcription import TranscriptionJobRead, TranscriptionMessage
from app.services.transcriptions import TranscriptionError, TranscriptionQueueError


def test_upload_returns_created_job(client, fake_db, current_user, monkeypatch) -> None:
    def fake_create_transcription_job(db, *, user, upload, language, model_name):
        assert db is fake_db
        assert user.id == current_user.id
        assert upload.filename == "sample.wav"
        assert language == "en"
        assert model_name is None
        return TranscriptionJobRead(
            id=8,
            status="pending",
            source_filename="sample.wav",
            language="en",
            model_name=None,
            duration_seconds=None,
            error_message=None,
            created_at=datetime(2026, 3, 27, tzinfo=UTC),
            started_at=None,
            completed_at=None,
            transcript_available=False,
        )

    monkeypatch.setattr(
        "app.api.routes.transcriptions.create_transcription_job",
        fake_create_transcription_job,
    )

    response = client.post(
        "/transcriptions/upload",
        files={"file": ("sample.wav", b"fake-audio", "audio/wav")},
        data={"language": "en"},
    )

    assert response.status_code == 201
    assert response.json()["id"] == 8
    assert response.json()["status"] == "pending"


def test_upload_maps_queue_errors_to_503(client, monkeypatch) -> None:
    def fake_create_transcription_job(db, *, user, upload, language, model_name):
        raise TranscriptionQueueError("Failed to enqueue transcription job.")

    monkeypatch.setattr(
        "app.api.routes.transcriptions.create_transcription_job",
        fake_create_transcription_job,
    )

    response = client.post(
        "/transcriptions/upload",
        files={"file": ("sample.wav", b"fake-audio", "audio/wav")},
    )

    assert response.status_code == 503
    assert response.json() == {"detail": "Failed to enqueue transcription job."}


def test_delete_transcription_returns_success_message(
    client, fake_db, current_user, monkeypatch
) -> None:
    def fake_delete_job_for_user(db, *, job_id, user):
        assert db is fake_db
        assert job_id == 8
        assert user.id == current_user.id
        return TranscriptionMessage(message="Transcription job deleted.")

    monkeypatch.setattr(
        "app.api.routes.transcriptions.delete_job_for_user",
        fake_delete_job_for_user,
    )

    response = client.delete("/transcriptions/8")

    assert response.status_code == 200
    assert response.json() == {"message": "Transcription job deleted."}


def test_delete_transcription_maps_not_found_to_404(client, monkeypatch) -> None:
    def fake_delete_job_for_user(db, *, job_id, user):
        raise TranscriptionError("Transcription job not found.")

    monkeypatch.setattr(
        "app.api.routes.transcriptions.delete_job_for_user",
        fake_delete_job_for_user,
    )

    response = client.delete("/transcriptions/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Transcription job not found."}
