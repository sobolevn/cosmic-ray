"Implementation of the 'new-config' command."

import qprompt

from cosmic_ray.plugins import execution_engine_names

TEMPLATE = '''module-path: {module_path}

baseline: 10

exclude-modules:

test-command: {test_command}

execution-engine:
  name: {engine}
'''


def new_config():
    """Prompt user for config variables and generate new config.

    Returns: A new configuration as a single string.
    """
    conf = {'module_path': qprompt.ask_str("Top-level module path")}

    conf['test_command'] = qprompt.ask_str('Test command')

    menu = qprompt.Menu()
    for at_pos, engine_name in enumerate(execution_engine_names()):
        menu.add(str(at_pos), engine_name)
    conf['engine'] = menu.show(header="Execution engine",
                               returns="desc")
    return TEMPLATE.format(**conf)
