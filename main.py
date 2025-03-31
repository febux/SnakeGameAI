from argparse import ArgumentParser

from app.app_ai import AppAI
from app.app_manual import AppManual

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(
        "--ai-mode",
        dest="ai",
        action='store_true',
        help="AI mode setting",
    )
    args = parser.parse_args()

    if args.ai:
        app = AppAI(640, 480, speed=400, block_size=10, food_multiplier=1, plot_available=True)
    else:
        app = AppManual(800, 800, speed=8, block_size=10, food_multiplier=3)

    app.run()
