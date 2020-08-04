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
        c.sudo("usermod -aG docker pi", pty=True)
        c.sudo("pip3 install docker-compose", pty=True)


@task(help={"host": "Raspberry PI hostname or IP address"})
def update_rpi(ctx, host):
    """
    Update Raspberry PI packages.
    """
    with ssh_connection(host) as c:
        c.sudo("apt update", pty=True)
        c.sudo("apt full-upgrade --yes", pty=True)
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


@task(
    pre=[build_image, push_image],
    help={"host": "Raspberry PI hostname or IP address"}
)
def deploy_server(ctx, host):
    """
    Deploy webthings-server to Raspberry PI.
    """
    ctx.run(rsync(host, source="./docker-compose.yaml", target="/home/pi/webthings-server"))
    with ssh_connection(host) as c:
        with c.cd("webthings-server"):
            c.run("docker-compose pull", pty=True)
            c.run("docker-compose down", pty=True)
            c.run("docker-compose up --detach", pty=True)
            c.run("docker-compose images", pty=True)


@task(help={"host": "Raspberry PI hostname or IP address"})
def show_logs(ctx, host):
    """
    Show webthings-server logs on Raspberry PI.
    """
    with ssh_connection(host) as c:
        with c.cd("webthings-server"):
            c.run("docker-compose logs", pty=True)


def ssh_connection(host: str) -> Connection:
    return Connection(f"pi@{host}")


def rsync(host: str, source: str, target: str, remote_target: bool = True) -> str:
    options = ["--recursive", "--delete"]
    if remote_target:
        return f"rsync {' '.join(options)} {source} pi@{host}:{target}"
    else:
        return f"rsync {' '.join(options)} pi@{host}:{source} {target}"
