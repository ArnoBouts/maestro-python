import compose
import logging
import io

from dockerpty.pty import PseudoTerminal, RunOperation

log = logging.getLogger(__name__)

def up(w, service):
    log.debug('Up ' + service['name'])
    project = compose.cli.command.get_project(w + '/services/' + service['name'])
    project.up(silent=True)

def down(w, service, remove_image_type, include_volumes):
    log.debug('Down ' + service['name'])
    project = compose.cli.command.get_project(w + '/services/' + service['name'])
    project.down(remove_image_type=remove_image_type, include_volumes=include_volumes)

def pull(w, service):
    log.debug('Pull ' + service['name'])
    project = compose.cli.command.get_project(w + '/services/' + service['name'])
    project.pull(silent=True)

def checkImage(w, service):
    project = compose.cli.command.get_project(w + '/services/' + service['name'])

    uptodate = True

    services = project.get_services()
    for s in services:
        containers = s.containers()
        if len(containers) > 0:
            c = s.containers()[0]

            if(s.image()['Id'] != c.image_config['Id']):
                log.info('New version available for service %s', service['name'])
                uptodate = False

    return not uptodate

class StringStream(io.StringIO):
    def __init__(self):
        io.StringIO.__init__(self)

    def send(self, buffer):
        self.write(str(buffer, 'utf-8'))


def run (w, app, service_name, command, out=None, environment=[]):
    project = compose.cli.command.get_project(w + '/services/' + app['name'])

    service = project.get_service(service_name)

    container = service.create_container(quiet=True, one_off=True, **{
                'command': command,
                'tty': False,
                'stdin_open': False,
                'detach': False,
                'environment':environment
            })

    operation = RunOperation(
        project.client,
        container.id,
        interactive=False,
        logs=False,
        stdout=out,
    )
    pty = PseudoTerminal(project.client, operation)
    sockets = pty.sockets()
    service.start_container(container)
    pty.start(sockets)
    exit_code = container.wait()

    project.client.remove_container(container.id, force=True, v=True)

    return exit_code
