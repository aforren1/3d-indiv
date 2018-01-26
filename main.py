import argparse
import sys

from exp_implementation import Individuation

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--id', help='Subject ID', default='007')
    parser.add_argument(
        '--tgt', help='Path to trial table', default='tables/test.txt')
    parser.add_argument('--dev', help='Device to use', default='mouse')
    args = parser.parse_args()
    if args.dev is 'mouse':
        pass
    demo = Individuation(dev=args.dev, trial_table=args.tgt)
    demo.run()
