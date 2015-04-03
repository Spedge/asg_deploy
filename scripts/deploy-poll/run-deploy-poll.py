"""Polls an SQS queue for deploy objects.
Invokes ansible when a deploy object is found.
"""
import os
import logging
import argparse

import deploy_poll

CONSOLE_LOGGING_FORMAT = logging.Formatter('%(asctime)s %(levelname)s %(message)s')


def setup_logging(debug):
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    if debug:
        ch.setLevel(logging.DEBUG)
    else:
        ch.setLevel(logging.INFO)
    ch.setFormatter(CONSOLE_LOGGING_FORMAT)
    logger.addHandler(ch)

# The maximum polling interval for a long poll is 20 seconds.
# http://aws.amazon.com/sqs/faqs/
def check_interval(value):
    ivalue = int(value)
    if ivalue < 1 or ivalue > 20:
         raise argparse.ArgumentTypeError("Interval has to be between 1 and 20 seconds, %s is illegal." % value)
    return ivalue

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='poll for new deployment requests')
    parser.add_argument('-q', '--queue-url',
                        required=True,
                        help='URL for SQS queue to check for deploy objects')
    parser.add_argument('-i', '--interval',
                        required=False,
                        type=check_interval,
                        default=20,
                        help='Polling interval')
    parser.add_argument('-d', '--debug',
                        action='store_true',
                        default=False,
                        help='Enable debug logging')
    args = parser.parse_args()
    queue_url = args.queue_url
    interval = args.interval

    # Set up logging
    logger = logging.getLogger('deploy-poll')
    setup_logging(args.debug)

    logger.info("Starting up {}".format(os.path.basename(__file__)))
    logger.debug("Args: queue_url: {0}, interval: {1}".format(args.queue_url, args.interval))

    dp = deploy_poll.DeployPoll(queue_url, interval)
    dp.poll_queue()
