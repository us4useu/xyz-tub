"""Application main module."""

import argparse
import multiprocessing as mp
from xyztank.version import __version__
from xyztank.view import ConsoleView
from xyztank.controller import Controller
from xyztank.model import XyzSystem
from xyztank.logging import get_logger


logger = get_logger("main")


def main():
    """
    Application main function.
    """
    # Parse application arguments.
    parser = argparse.ArgumentParser(description=f"XYZ-tank {__version__}.")
    parser.add_argument("--settings", dest="settings",
                        help="Path to the settings file. Optional, will run "
                             "interactive mode when settings are not given.",
                        required=False, type=str, default=None)
    parser.add_argument("--output", dest="output",
                        help="Path to the measurement output file.",
                        required=False, type=str, default=None)
    args = parser.parse_args()

    # Start the application.
    model = XyzSystem()

    if args.settings is None:
        # Interactive mode.
        event_queue = mp.Queue()
        view = ConsoleView(event_queue)
        controller = Controller(model, view, event_queue)
        controller.start()
        view.start()
        # Wait for the controller to finish it's work.
        controller.join()
    else:
        # Non-interactive mode.
        model.run_settings(args.settings)
        while True:
            progress = model.get_progress()
            if progress is not None and progress.percent == 100:
                logger.info("Measurement finished, saving data...")
                model.save_measurement(args.output)
                return


if __name__ == "__main__":
    main()
