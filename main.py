from argparse import ArgumentParser
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
        app = AppManual(1200, 900, speed=20, food_multiplier=3)
    else:
        app = AppManual(1200, 900, speed=8, food_multiplier=3)

    app.run()
