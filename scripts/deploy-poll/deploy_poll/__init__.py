"""Polls an SQS queue for deploy objects.
Invokes ansible when a deploy object is found.
"""
import sys
import logging
import json
import datetime
import subprocess

import boto.sqs
import boto.sqs.queue
import boto.exception

import config
import os

logger = logging.getLogger('deploy-poll')


class DeployPoll(object):
    def __init__(self, queue_url, interval):
        self.interval = interval
        self.q = self.sqs_setup(queue_url)
        self.message_count=0

    def sqs_setup(self, queue_url):
        try:
            q_conn = boto.sqs.connect_to_region(config.AWS_REGION)
        except boto.exception.NoAuthHandlerFound:
            logger.error("Unable to connect to AWS, are your credentials valid?")
            sys.exit(1)
        return boto.sqs.queue.Queue(q_conn, queue_url)

    def poll_queue(self):
        while True:
            logger.debug("Waiting for messages for " + str(self.interval) + "s, completed " + str(self.message_count) + " so far.")
            messages = self.q.get_messages(1, attributes='SentTimestamp', message_attributes=['SenderIp', 'Playbook'], wait_time_seconds=self.interval)
            if len(messages) > 0:
                message = messages.pop()
                logger.debug("Found new message!")
                (payload, sender, playbook) = self.check_object(message)
                if payload is not None and sender is not None and playbook is not None:
                    self.fork_ansible_playbook(payload, sender, playbook)
                self.delete(message)

    def delete(self, message):
        self.q.delete_message(message)

    def check_object(self, message):

	# Define the container for the error messages.
	errors = [];

        # We expect a timestamp from the message. Without one, it's not valid.
        try:
            message_sent = datetime.datetime.fromtimestamp(int(message.attributes['SentTimestamp'])/1000)
        except KeyError:
            errors.append("Error reading message timestamp. Discarding this message.")

	# We need the IP of the Sender so we know which box to configure!
        try:
            message_sender = message.message_attributes['SenderIp']['string_value']
        except KeyError:
            errors.append("SQS message missing SenderIp")

	# This will allow us to specify a playbook, or revert to the default
        # if the message explicitly does not state a playbook in the attributes.
	try:
            message_playbook = message.message_attributes['Playbook']['string_value']
	    location = config.ANSIBLE_PLAYBOOK_DIRECTORY + "/{}".format(message_playbook)

	    if not os.path.isfile(location):
              errors.append("No playbook found at " + location)

        except KeyError:
 	    logger.debug("SQS message missing Playbook attribute, using default playbook.")
            message_playbook = config.ANSIBLE_PLAYBOOK_DEFAULT

	# Load the message body into a JSON object and print in in debug.	 
	message_body = message.get_body()

        logger.debug("Message details - timestamp: {}, ip: {}, contents: {}".format(
            message_sent.strftime("%Y-%m-%d %H:%M:%S"),
            message_sender,
            message_body))

        try:
            message_json = json.loads(message_body)
        except ValueError:
            errors.append("Unable to deserialize JSON. Discarding.")

	# Check if the message is older than the configured acceptable time.
        if datetime.datetime.now() - datetime.timedelta(seconds=config.MESSAGE_TIMEOUT) > message_sent:
            errors.append("Message is older than " + str(config.MESSAGE_TIMEOUT) + " seconds. Assuming it's no longer relevant and discarding")

        for k in config.REQUIRED_PARAMETERS:
            if not k in message_json:
                errors.append("Message missing required parameter {}. Discarding".format(k))
	
	# So now we know all the problems with the message, let's print them and return.
	if len(errors) > 0:
	  for error in errors:
            logger.warn(error)

	  self.delete(message)
          return (None, None, None)
	else:
          return message_json, message_sender, message_playbook

    def fork_ansible_playbook(self, payload, sender, playbook):
        logger.info("Deploying {}".format(",".join(["{}={}".format(k, v) for k, v in payload.items()])))
        ansible_runtime_vars = " ".join(["-e {}={}".format(k, v) for k, v in payload.items()])
        playbook_cmd = [
            config.ANSIBLE_PLAYBOOK_COMMAND,
            "--private-key",
            config.PRIVATE_KEY_FILE,
            "-i",
            "{},".format(sender),
            ansible_runtime_vars,
            config.ANSIBLE_PLAYBOOK_DIRECTORY + "/{}".format(playbook)
        ]
        logger.debug("Ansible playbook command: {0}".format(' '.join(playbook_cmd)))
	self.message_count += 1
        subprocess.Popen(playbook_cmd)
