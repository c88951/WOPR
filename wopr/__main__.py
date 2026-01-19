"""Entry point for WOPR: python -m wopr"""

import argparse
import sys

from . import __version__


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        prog="wopr",
        description="WOPR - War Operation Plan Response. A faithful recreation of the WarGames (1983) supercomputer.",
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"WOPR {__version__}",
    )

    parser.add_argument(
        "--skip-intro",
        action="store_true",
        help="Skip the modem dialup sequence",
    )

    parser.add_argument(
        "--no-sound",
        action="store_true",
        help="Disable all audio",
    )

    parser.add_argument(
        "--no-voice",
        action="store_true",
        help="Disable voice synthesis only",
    )

    parser.add_argument(
        "--fast",
        action="store_true",
        help="Disable typing animations",
    )

    parser.add_argument(
        "--game",
        type=str,
        metavar="GAME",
        help="Jump directly to a specific game",
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode",
    )

    args = parser.parse_args()

    # Run the application
    from .app import run_app

    try:
        run_app(
            skip_intro=args.skip_intro,
            no_sound=args.no_sound,
            no_voice=args.no_voice,
            fast_mode=args.fast,
            start_game=args.game,
            debug=args.debug,
        )
        return 0
    except KeyboardInterrupt:
        print("\n\nCONNECTION TERMINATED")
        return 0
    except Exception as e:
        if args.debug:
            raise
        print(f"\nERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
