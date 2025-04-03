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
    parser.add_argument(
        "--train",
        dest="train",
        action='store_true',
        help="AI mode training",
    )
    args = parser.parse_args()

    if args.ai:
        app = AppAI(
            640,
            480,
            speed=1000,
            block_size=20,
            food_multiplier=1,
            plot_available=True,
            train=args.train,
        )
    else:
        app = AppManual(
            800,
            800,
            speed=8,
            block_size=10,
            food_multiplier=3,
        )

    app.run()
