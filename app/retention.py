"""Zero-retention purge for uploaded production media."""

import logging
from pathlib import Path

from app.config import settings

logger = logging.getLogger("cineclear.retention")


def purge_upload_if_ephemeral(file_path: str | Path) -> bool:
    """Deletes a file only if it lives under the uploads directory. Sample media is never deleted."""
    try:
        target = Path(file_path).resolve()
        upload_root = settings.UPLOAD_DIR.resolve()
        if upload_root in target.parents or target.parent == upload_root:
            target.unlink(missing_ok=True)
            logger.info("Purged ephemeral upload: %s", target.name)
            return True
    except Exception as e:
        logger.warning("Upload purge skipped for %s: %s", file_path, e)
    return False
