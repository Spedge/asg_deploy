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
    parser.add_argument('--queue-url', '-q',
                        required=True,
                        help='URL for SQS queue to check for deploy objects')
    parser.add_argument('--dead_letter_queue_url', '-l',
                        required=True,
                        help='URL for SQS queue where bad messages are sent.')
    parser.add_argument('--interval', '-i',
                        required=False,
                        type=check_interval,
                        default=20,
                        help='Polling interval')
    parser.add_argument('--debug', '-d',
                        action='store_true',
                        default=False,
                        help='Enable debug logging')

    args = parser.parse_args()

    # Set up logging
    logger = logging.getLogger('deploy-poll')
    setup_logging(args.debug)

    logger.info("Starting up {}".format(os.path.basename(__file__)))
    logger.debug("Args: queue_url: {0}, interval: {1}".format(args.queue_url, args.interval))

    dp = deploy_poll.DeployPoll(args.queue_url, args.dead_letter_queue_url, args.interval)
    dp.poll_queue()
