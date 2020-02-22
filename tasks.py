from typing import Iterable

from fabric import Connection
from invoke import task


# TODO add tests
@task(help={"host": "Raspberry PI hostname or IP address"})
def setup_rpi(ctx, host):
    """
    Setup Raspberry PI.
    """
    ctx.run(f"ssh-copy-id pi@{host}")
    with ssh_connection(host) as c:
        c.sudo(apt("-y", "install", "pipenv"), pty=True)


@task(help={"host": "Raspberry PI hostname or IP address"})
def update_rpi(ctx, host):
    """
    Update Raspberry PI packages. 
    """
    with ssh_connection(host) as c:
        c.sudo(apt("update"), pty=True)
        c.sudo(apt("-y", "full-upgrade"), pty=True)
        c.sudo(apt("clean"), pty=True)


@task(help={"host": "Raspberry PI hostname or IP address",
            "backup-dir": "Backup directory (optional)"})
def backup_gateway(ctx, host, backup_dir="./backup"):
    """
    Backup webthings-gateway on Raspberry PI.
    """
    ctx.run(rsync(host, source="/home/pi/.mozilla-iot/", target=backup_dir, remote_target=False))


@task(help={"host": "Raspberry PI hostname or IP address",
            "backup-dir": "Backup directory (optional)"})
def restore_gateway(ctx, host, backup_dir="./backup"):
    """
    Restore webthings-gateway on Raspberry PI.
    """
    ctx.run(rsync(host, source=f"{backup_dir}/", target="/home/pi/.mozilla-iot", remote_target=True))


@task(help={"host": "Raspberry PI hostname or IP address"})
def deploy_server(ctx, host):
    """
    Deploy webthings-server to Raspberry PI.
    """
    files = [
        "./kupcimat",
        "./webthings-server.py",
        "./webthings-mapping.yaml",
        "Pipfile",
        "Pipfile.lock"
    ]
    ctx.run(rsync(host, source=join(files), target="/home/pi/webthings-server"))
    with ssh_connection(host) as c:
        with c.cd("webthings-server"):
            c.run(pipenv("sync"), pty=True)
            c.run(pipenv("clean"), pty=True)


def apt(*arguments: str) -> str:
    return f"apt {join(arguments)}"


def pipenv(*arguments: str) -> str:
    return f"pipenv {join(arguments)}"


def join(arguments: Iterable[str]) -> str:
    return " ".join(arguments)


def ssh_connection(host: str) -> Connection:
    return Connection(f"pi@{host}")


def rsync(host: str, source: str, target: str, remote_target: bool = True) -> str:
    options = ["--recursive", "--delete"]
    if remote_target:
        return f"rsync {join(options)} {source} pi@{host}:{target}"
    else:
        return f"rsync {join(options)} pi@{host}:{source} {target}"
