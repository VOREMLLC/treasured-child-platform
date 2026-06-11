"""Server-side fee and price table.

THE ONLY PLACE money amounts live. ``POST /payments/initialize`` looks
them up here; the client supplies the *purpose*, never the *amount*.

All values are in **kobo** (Naira × 100). Integers only.

Per BUILD_SPEC §14 item 1, real amounts are supplied by the proprietor.
Until then everything below is a documented PLACEHOLDER.
"""

from typing import Optional

from app.models.payment import PaymentPurpose


# PLACEHOLDER — replace once the proprietor confirms the fee schedule.
# v1 doesn't differentiate by class level; later splits per BUILD_SPEC §14.
FEES_KOBO = 12_500_000  # ₦125,000

# PLACEHOLDER — keyed by programme slug; must match the slugs in
# frontend/src/lib/programmes.ts.
PROGRAMME_PRICES_KOBO: dict[str, int] = {
    "bece-prep": 2_000_000,  # ₦20,000
    "ai-data": 3_500_000,    # ₦35,000
}

# Display labels shown in receipts and emails. Keyed by programme slug.
PROGRAMME_LABELS: dict[str, str] = {
    "bece-prep": "BECE / Common entrance prep",
    "ai-data": "AI & data analytics",
}


def get_programme_label(slug: str) -> str:
    """Display name for a programme slug — falls back to the slug itself."""
    return PROGRAMME_LABELS.get(slug, slug)


class UnknownTargetError(ValueError):
    """Raised when a programme slug isn't in the price table."""


def compute_amount_kobo(
    purpose: PaymentPurpose, target: Optional[str] = None
) -> int:
    """Return the canonical amount in kobo for the given purpose.

    - ``fees`` → ``FEES_KOBO`` (target is ignored).
    - ``programme`` → ``PROGRAMME_PRICES_KOBO[target]`` (target required).

    Raises ``UnknownTargetError`` if a programme target is missing or
    not in the price table.
    """
    if purpose is PaymentPurpose.fees:
        return FEES_KOBO

    if purpose is PaymentPurpose.programme:
        if target is None:
            raise UnknownTargetError(
                "Programme payments require a 'target' (programme slug)."
            )
        try:
            return PROGRAMME_PRICES_KOBO[target]
        except KeyError as e:
            raise UnknownTargetError(
                f"Unknown programme: {target!r}."
            ) from e

    raise UnknownTargetError(f"Unsupported purpose: {purpose!r}.")
