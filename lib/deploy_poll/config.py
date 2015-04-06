REQUIRED_PARAMETERS = [
    "service",
    "env",
    "release"
]
ANSIBLE_PLAYBOOK_DIRECTORY = "/etc/ansible"
ANSIBLE_PLAYBOOK_DEFAULT = "site.yml"
ANSIBLE_PLAYBOOK_COMMAND = "ansible-playbook"
MESSAGE_TIMEOUT=30
VAULT_PW_FILE = "/etc/ansible/.vaultpw"
PRIVATE_KEY_FILE = "/home/ansible/.ssh/id_rsa_github"
AWS_REGION = "us-east-1"
