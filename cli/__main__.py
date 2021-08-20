from . import *

class Dialog:

    def module(self):
        return prompt({
            'type': 'list',
            'name': 'module',
            'message': 'Select module',
            'choices': ['Report tools', 'Exit'],
            'filter': lambda choice: {
                'Report tools': 'report'
            }.get(choice, 'exit')
        })

    def __init__(self) -> None:
        while True:
            module = self.module()['module']
            print(module)
            if module == 'exit': return None
            next = __import__(module)
            next.Dialog()

dialog = Dialog()