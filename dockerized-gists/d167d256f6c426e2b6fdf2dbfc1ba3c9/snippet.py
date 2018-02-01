import click


def prompt_proxy(ctx, param, use_proxy):
    if use_proxy:
        host = ctx.params.get('proxy_host')
        if not host:
            host = click.prompt('Proxy host', default='localhost')

        port = ctx.params.get('proxy_port')
        if not port:
            port = click.prompt('Proxy port', default=9000)

        return (host, port)


@click.command()
@click.option('--use-proxy/--no-proxy', is_flag=True, default=False, callback=prompt_proxy)
@click.option('--proxy-host', is_eager=True)
@click.option('--proxy-port', is_eager=True, type=int)
def cli(use_proxy, proxy_host, proxy_port):
    if use_proxy:
        click.echo('Using proxy {}:{}'.format(*use_proxy))
    else:
        click.echo('Not using proxy.')


if __name__ == '__main__':
    cli()
