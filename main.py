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
        app = AppAI(800, 800, speed=200, food_multiplier=3, agents_amount=1)
    else:
        app = AppManual(800, 800, speed=8, food_multiplier=3)

    app.run()
