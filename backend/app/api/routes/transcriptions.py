from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.transcription import TranscriptRead, TranscriptionJobList, TranscriptionJobRead
from app.services.transcriptions import (
    TranscriptionError,
    build_transcript_download_response,
    create_transcription_job,
    get_job_for_user,
    get_job_result_for_user,
    list_jobs_for_user,
)

router = APIRouter(prefix="/transcriptions", tags=["transcriptions"])


@router.get("", response_model=TranscriptionJobList)
def list_transcriptions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TranscriptionJobList:
    jobs = list_jobs_for_user(db, current_user)
    return TranscriptionJobList(jobs=jobs)


@router.post("/upload", response_model=TranscriptionJobRead, status_code=status.HTTP_201_CREATED)
def upload_transcription(
    file: UploadFile = File(...),
    language: str | None = Form(default=None),
    model_name: str | None = Form(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TranscriptionJobRead:
    try:
        return create_transcription_job(
            db,
            user=current_user,
            upload=file,
            language=language,
            model_name=model_name,
        )
    except TranscriptionError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/{job_id}", response_model=TranscriptionJobRead)
def get_transcription(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TranscriptionJobRead:
    try:
        return get_job_for_user(db, job_id=job_id, user=current_user)
    except TranscriptionError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/{job_id}/result", response_model=TranscriptRead)
def get_transcription_result(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TranscriptRead:
    try:
        return get_job_result_for_user(db, job_id=job_id, user=current_user)
    except TranscriptionError as exc:
        detail = str(exc)
        status_code = status.HTTP_409_CONFLICT
        if detail == "Transcription job not found.":
            status_code = status.HTTP_404_NOT_FOUND
        raise HTTPException(status_code=status_code, detail=detail) from exc


@router.get("/{job_id}/download")
def download_transcription_result(
    job_id: int,
    format_name: str = Query(default="txt", alias="format"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    try:
        return build_transcript_download_response(
            db,
            job_id=job_id,
            user=current_user,
            format_name=format_name.lower(),
        )
    except TranscriptionError as exc:
        detail = str(exc)
        status_code = status.HTTP_409_CONFLICT
        if detail == "Transcription job not found.":
            status_code = status.HTTP_404_NOT_FOUND
        raise HTTPException(status_code=status_code, detail=detail) from exc
