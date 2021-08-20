from prompt_toolkit.validation import Validator, ValidationError
from PyInquirer import prompt, style_from_dict
class Dialog:

    def action(self):
        return prompt({
            'type': 'list',
            'name': 'action',
            'message': 'Select action',
            'choices': [
                'Auto processing',
                'Scan files',
                'Download reports',
                'Settings',
                'Exit'
            ],
            'filter': lambda choice: {
                'Auto processing': 'auto',
                'Scan files': 'scan',
                'Download reports': 'download',
                'Settings': 'settings'
            }.get(choice, 'exit')
        })['action']

    def __init__(self):
        while True:
            action = self.action()
            if action == 'exit': return None
            print(action)

Dialog()