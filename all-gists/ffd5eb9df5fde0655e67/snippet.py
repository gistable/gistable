import click


class DefaultCmdGroup(click.Group):
    def get_command(self, ctx, cmd_name):
        click.echo(ctx.args)
        cmd = click.Group.get_command(self, ctx, cmd_name)
        if cmd is not None:
            return cmd
        else:
            return click.Group.get_command(self, ctx, 'send')

@click.command(cls=DefaultCmdGroup)
@click.pass_context
def main(ctx):
    pass

@click.command(help='Send recipient a message')
@click.argument('recipient')
@click.argument('message', nargs=-1)
@click.pass_context
def send(ctx, recipient, message):
    if ctx.parent.args[0] != 'send':
        recipient = ctx.parent.args[0]
        msg = ' '.join(ctx.parent.args[1:])
    else:
        msg = ' '.join(list(message))
    click.echo('send ' + recipient + ' ' + msg)
