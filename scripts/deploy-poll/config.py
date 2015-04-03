REQUIRED_PARAMETERS = [
    "service",
    "env",
    "release"
]
ANSIBLE_PLAYBOOKS = "/etc/ansible"
ANSIBLE_PLAYBOOK_DEFAULT="site.yml"

VAULT_PW_FILE = "/etc/ansible/.vaultpw"
PRIVATE_KEY_FILE = "/home/ansible/.ssh/id_rsa_github"
AWS_REGION = "us-east-1"
MESSAGE_TIMEOUT=30
