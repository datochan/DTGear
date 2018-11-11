"""
    cli
    ~~~~~~~~~~~~~~
    命令模块 - 数据的更新和维护.

    :copyright: (c) 2016-10-26 by datochan.
"""
import os
import click

plugin_folder = os.path.join(os.path.join(os.path.dirname(__file__), 'app'), 'cmd')


class DatoCLI(click.MultiCommand):

    def list_commands(self, ctx):
        rv = []
        for filename in os.listdir(plugin_folder):
            if filename.endswith('.py'):
                rv.append(filename[:-3])
        rv.sort()
        return rv

    def get_command(self, ctx, name):
        ns = {}
        fn = os.path.join(plugin_folder, name + '.py')
        with open(fn) as f:
            code = compile(f.read(), fn, 'exec')
            eval(code, ns, ns)
        return ns[name]


cli = DatoCLI(help='命令模块 - 数据的更新和维护')


if __name__ == '__main__':
    cli()
