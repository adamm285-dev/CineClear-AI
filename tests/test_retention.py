from pathlib import Path

from app.config import settings
from app.retention import purge_upload_if_ephemeral


def test_purge_deletes_uploads_only():
    settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    ephemeral = settings.UPLOAD_DIR / "ephemeral_legal_test.bin"
    ephemeral.write_bytes(b"secret dailies")
    assert ephemeral.exists()
    assert purge_upload_if_ephemeral(ephemeral) is True
    assert not ephemeral.exists()


def test_purge_never_deletes_sample_media():
    sample = settings.SAMPLE_MEDIA_DIR / "sample_set_photo.jpg"
    assert sample.exists()
    assert purge_upload_if_ephemeral(sample) is False
    assert sample.exists()
