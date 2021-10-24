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
        c.sudo("curl -sSL https://get.docker.com | sh", pty=True)
        c.sudo("pip3 install docker-compose", pty=True)
        c.sudo("usermod -aG docker pi", pty=True)
        c.sudo("docker login", pty=True)


@task(help={"host": "Raspberry PI hostname or IP address"})
def update_rpi(ctx, host):
    """
    Update Raspberry PI packages.
    """
    with ssh_connection(host) as c:
        c.sudo("apt update", pty=True)
        c.sudo("apt full-upgrade --yes", pty=True)
        c.sudo("apt auto-remove --yes", pty=True)
        c.sudo("apt clean", pty=True)


@task(help={"host": "Raspberry PI hostname or IP address",
            "backup-dir": "Backup directory (optional)"})
def backup_gateway(ctx, host, backup_dir="./backup"):
    """
    Backup webthings-gateway on Raspberry PI.
    """
    ctx.run(rsync(host, source="/home/pi/.mozilla-iot", target=backup_dir, remote_target=False))
    ctx.run(rsync(host, source="/home/pi/webthings-server/webthings-mapping.yaml", target=backup_dir,
                  remote_target=False))


@task(help={"host": "Raspberry PI hostname or IP address",
            "backup-dir": "Backup directory (optional)"})
def restore_gateway(ctx, host, backup_dir="./backup"):
    """
    Restore webthings-gateway on Raspberry PI.
    """
    ctx.run(rsync(host, source=f"{backup_dir}/.mozilla-iot", target="/home/pi", remote_target=True))
    ctx.run(rsync(host, source=f"{backup_dir}/webthings-mapping.yaml", target="/home/pi/webthings-server",
                  remote_target=True))


@task(help={"tag": "Docker image name and tag (optional)"})
def build_image(ctx, tag="kupcimat/webthings-server"):
    """
    Build webthings-server docker image locally.
    """
    ctx.run(f"docker build --tag {tag} .")


@task(help={"tag": "Docker image name and tag (optional)"})
def push_image(ctx, tag="kupcimat/webthings-server"):
    """
    Push webthings-server docker image to registry.
    """
    ctx.run(f"docker push {tag}")


@task(help={"host": "Raspberry PI hostname or IP address"})
def deploy_server(ctx, host):
    """
    Deploy webthings-server on Raspberry PI.
    """
    files = ["./docker-compose.yaml", "./webthings-mapping.yaml"]
    ctx.run(rsync(host, source=" ".join(files), target="/home/pi/"))
    with ssh_connection(host) as c:
        c.run("docker-compose pull", pty=True)
        c.run("docker-compose down", pty=True)
        c.run("docker-compose up --detach", pty=True)
        c.run("docker-compose ps", pty=True)


@task(help={"host": "Raspberry PI hostname or IP address"})
def update_server(ctx, host):
    """
    Update webthings-server configuration on Raspberry PI.
    """
    ctx.run(rsync(host, source="./webthings-mapping.yaml", target="/home/pi/"))
    with ssh_connection(host) as c:
        c.run("docker-compose restart", pty=True)
        c.run("docker-compose ps", pty=True)


@task(help={"host": "Raspberry PI hostname or IP address"})
def show_logs(ctx, host):
    """
    Show webthings-server logs on Raspberry PI.
    """
    with ssh_connection(host) as c:
        c.run("docker-compose logs --follow --tail 50", pty=True)


@task
def upgrade_deps(ctx):
    """
    Upgrade application and development dependencies.
    """
    ctx.run("pip-compile --upgrade --generate-hashes requirements.in")
    ctx.run("pip-compile --upgrade --generate-hashes requirements-dev.in")


@task
def install_deps(ctx):
    """
    Install application and development dependencies.
    """
    ctx.run("pip-sync requirements.txt requirements-dev.txt")


def ssh_connection(host: str) -> Connection:
    return Connection(f"pi@{host}")


def rsync(host: str, source: str, target: str, remote_target: bool = True) -> str:
    options = ["--recursive", "--delete", "--copy-links"]
    if remote_target:
        return f"rsync {' '.join(options)} {source} pi@{host}:{target}"
    else:
        return f"rsync {' '.join(options)} pi@{host}:{source} {target}"
