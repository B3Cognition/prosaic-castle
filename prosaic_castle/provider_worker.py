"""Prosaic Castle's scoped, read-only provider command."""

from importlib.metadata import PackageNotFoundError, distribution


def main():
    """Reject an overlapping upstream installation before opening the provider."""
    try:
        distribution("cognitive-castle")
    except PackageNotFoundError:
        pass
    else:
        raise SystemExit(
            "prosaic-castle and cognitive-castle share the cognitive_castle import "
            "namespace. Use a separate virtual environment for prosaic-castle; "
            "do not coinstall these distributions."
        )
    from cognitive_castle.provider_worker import main as legacy_main

    legacy_main()


if __name__ == "__main__":
    main()
