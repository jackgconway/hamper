import logging

from hamper.interfaces import Command, ChatCommandPlugin, BaseInterface


log = logging.getLogger('hamper.plugins.plugin_utils')


class PluginUtils(ChatCommandPlugin):

    name = 'plugins'
    priority = 0

    @classmethod
    def get_plugins(cls, bot):
        all_plugins = set()
        for kind, plugins in bot.factory.plugins.items():
            all_plugins.update(plugins)
        return all_plugins

    class ListPlugins(Command):
        regex = r'^plugins?(?: list)?$'

        name = 'plugins'
        short_desc = 'plugins subcommand - See extended help for more details.'
        long_desc = ('Manipulate plugins\n'
                     'list - List all loaded plugins\n'
                     'reload name - Reload a plugin by name.\n'
                     'unload name - Unload a plugin by name.\n'
                     'load name - Load a plugin by name.\n')

        def command(self, bot, comm, groups):
            """Reply with a list of all currently loaded plugins."""
            plugins = PluginUtils.get_plugins(bot)
            names = ', '.join(p.name for p in plugins)
            bot.reply(comm, 'Loaded Plugins: {0}.'.format(names))
            return True

    class UnloadPlugin(Command):
        regex = r'^plugins? unload (.*)$'

        def command(self, bot, comm, groups):
            """Unload a named plugin."""
            name = groups[0]
            plugins = PluginUtils.get_plugins(bot)
            matched_plugins = [p for p in plugins if p.name == name]
            if len(matched_plugins) == 0:
                bot.reply(comm, "I can't find a plugin named {0}!"
                    .format(name))
                return False

            target_plugin = matched_plugins[0]

            bot.removePlugin(target_plugin)
            bot.reply(comm, 'Unloading {0}.'.format(target_plugin))
            return True


plugin_utils = PluginUtils()
