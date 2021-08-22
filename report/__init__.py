from prompt_toolkit.validation import Validator, ValidationError
from PyInquirer import prompt, Separator
from . import rapid, scanner, discover
from .config import SETTINGS, LOG_LEVEL

from prompt_toolkit.validation import Validator, ValidationError

class Dialog:

    EXIT = False

    # questions = {
    #     'settings': [
    #         {
    #             'type': 'list',
    #             'name': 'auto',
    #             'message': 'Auto processing: Select setting',
    #             'choices': [
    #                 'Automatically processed reports',
    #                 'Find and add reports',
    #                 'Exit'
    #             ],
    #             'filter': lambda choice: {
    #                 'Automatically processed reports': 'list',
    #                 'Find and add reports': 'add',
    #             }.get(choice, self.EXIT),
    #             'when': lambda answers: answers['scope'] == 'auto'
    #         }
    #     ],
    #     'cut': [
    #         {
    #             'type': 'list',
    #             'name': 'settings_api',
    #             'message': 'API: Select setting',
    #             'choices': [
    #                 'Pagination',
    #                 'Timeout',
    #                 'Endpoint URL',
    #                 'Listing URL',
    #                 'Instance history URL',
    #                 'Download URL',
    #                 'Exit'
    #             ],
    #             'filter': lambda choice: {
    #                 'Pagination': 'pagination',
    #                 'Timeout': 'timeout',
    #                 'Endpoint URL': 'endpoint',
    #                 'Listing URL': 'listing',
    #                 'Generate report URL': 'generate',
    #                 'Instance history URL': 'instance_history',
    #                 'Download URL': 'download'
    #             }.get(choice, self.EXIT),
    #             'when': lambda answers: answers['scope'] == 'settings_api'
    #         }
    #     ]
    # }


    def prompt(self, questions):
        while True:
            answer = prompt(questions)
            print(answer)
            if len(answer) == 1: 
                for key, value in answer.items():
                    if value == self.EXIT: return None
                    yield value
            else: yield answer

    def resolve_map(self, name, mapping={}):
        if name in mapping:
            return mapping[name]
        else: 
            try:
                return self.__getattribute__(name)
            except:
                return None

    def enter(self, choice, mapping):
        while choice:
            next = self.resolve_map(choice, mapping)
            if callable(next):
                choice = next()
        return choice

    def mapping(self, question, mapping={}) -> None:
        for choice in self.prompt(question):
            if choice:
                self.enter(choice, mapping)
            else: return None


    def __init__(self):
        return self.mapping({
            'type': 'list',
            'name': 'action',
            'message': 'Action:',
            'choices': [
                {'name': 'Auto processing', 'value': 'auto'},
                {'name': 'Scan files', 'value': 'scan'},
                {'name': 'Download reports','value': 'download'},
                {'name': 'Settings','value': 'settings'},
                {'name': 'Exit','value': self.EXIT}]})


    def settings(self):
        return self.mapping({
            'type': 'list',
            'name': 'scope',
            'message': 'Settings:',
            'choices': [
                {'name': 'Scanning','value': 'settings_scan'},
                {'name': 'Rapid API','value': 'settings_api'},
                {'name': 'Logging','value': 'settings_log'},
                {'name': 'Auto processing','value': 'settings_auto'},
                {'name': 'Exit','value': self.EXIT}]})
    

    def settings_scan(self):
        return self.mapping({
            'type': 'list',
            'name': 'settings_scan',
            'message': 'Scanning:',
            'choices': [
                {'name': 'Cut position presets', 'value': 'settings_scan_cut'},
                {'name': 'Link reports to cut presets', 'value': 'settings_scan_link'},
                {'name': 'Exit', 'value': self.EXIT}]})

    def settings_scan_cut(self):
        def default(answers:dict):
            preset_name = answers['settings_scan_cut'] != 'add' and answers['settings_scan_cut'] or 'new'
            preset = SETTINGS.scanner.get(preset_name, {
                'page': 1,
                'crop': (1,1,1000,1000)})
            return f'''{
                preset_name} | {
                    preset["page"]} | {
                        preset["crop"][0]} | {
                            preset["crop"][1]} | {
                                preset["crop"][2]} | {
                                    preset["crop"][3]}'''

        def filter(values:str) -> tuple[str, int, tuple[int]]:
            if not len(values.strip()): return False
            values = [value.strip() for value in values.split('|')]
            name = values[0]
            ints = [int(value) for value in values[1:]]
            page = ints[0]
            cut = tuple(ints[1:])
            assert len(cut) == 4 and not ' ' in name
            return (name, page, cut)

        def validator(values:str) -> str:
            try:
                filter(values)
            except:
                return """Use following formating: name|page|cut start X|start Y|end X|end Y"""
            else:
                return True

        questions = [{
            'type': 'list',
            'name': 'settings_scan_cut',
            'message': 'Edit cut presets',
            'choices':
                [{'name': 'Add', 'value': 'add'}] + [
                    {
                        'name': f'{key}: page {preset["page"]}, crop {preset["crop"]}',
                        'value': key
                    } for key, preset in SETTINGS.scanner.items()
                ] + [{'name': 'Exit', 'value': self.EXIT}]},{
            'type': 'input',
            'name': 'edit',
            'message': 'Edit cut, erase to delete',
            'default': default,
            'validate': validator,
            'when': lambda answer: answer['settings_scan_cut'],
            'filter': filter}]
        
        for choice in self.prompt(questions):
            if edit := choice['edit']:
                name, page, cut = edit
                SETTINGS.scanner.update({name:{'page': page, 'crop': cut}})
                SETTINGS.save()
            if not choice['edit']:
                SETTINGS.scanner.pop(choice['settings_scan_cut'])
                SETTINGS.save()
            return 'settings_scan_cut'

    def settings_scan_link(self):

        questions = [
            {
                'type': 'list',
                'name': 'settings_scan_link',
                'message': 'Linking:',
                'choices': [{'name': 'Add', 'value': 'add'}] + [
                    {'name': f'{name}: {link}', 'value': name}
                    for name, link in SETTINGS.pdf.items()
                ] + [{'name': 'Exit', 'value': self.EXIT}]
            },
            {
                'type': 'list',
                'name': 'edit',
                'message': 'Select link',
                'choices': [preset for preset in SETTINGS.scanner] + [
                    {'name': 'Delete', 'value': 'delete'},
                    {'name': 'Exit', 'value': self.EXIT}
                ],
                'when': lambda answer: answer['settings_scan_link']
            },
            {
                'type': 'input',
                'name': 'add',
                'message': 'Enter report name or regex:',
                'default': '',
                'when': lambda answer: answer['settings_scan_link'] == 'add'
            }]
        
        for choice in self.prompt(questions):
            if choice['settings_scan_link'] == 'add':
                name = choice['add']
                link = choice['edit']
            else:
                if choice['edit'] == 'delete':
                    SETTINGS.pdf.pop(choice['settings_scan_link'])
                    SETTINGS.save()
                    return 'add'
                else:
                    name = choice['settings_scan_link']
                    link = choice['edit']
            SETTINGS.pdf[name] = link
            SETTINGS.save()
            return 'settings_scan_link'


    def settings_log(self):
        questions = [
            {
                'type': 'list',
                'name': 'settings_log',
                'message': 'Logging:',
                'choices': [
                    {'name': 'Filename', 'value': 'name'},
                    {'name': 'Level', 'value': 'level'},
                    {'name': 'Format', 'value': 'format'},
                    {'name': 'Exit', 'value': self.EXIT}]},
            {
                'type': 'input',
                'name': 'value',
                'message': 'Enter filename:',
                'default': SETTINGS.log['name'],
                'when': lambda answer: answer['settings_log'] == 'name'
            }, {
                'type': 'input',
                'name': 'value',
                'message': 'Enter format:',
                'default': SETTINGS.log['format'],
                'when': lambda answer: answer['settings_log'] == 'format'
            }, {
                'type': 'list',
                'name': 'value',
                'message': 'Level:',
                'choices': [level for level in LOG_LEVEL],
                'when': lambda answer: answer['settings_log'] == 'level'}]

        for choice in self.prompt(questions):
            SETTINGS.log[choice['settings_log']] = choice['value']
            SETTINGS.save()
            return 'settings_log'

    def settings_api(self):

        def connection_validator(min, max):
            def validator(value):
                try:
                    value = int(value)
                except:
                    return 'Enter an integer value'
                if min <= value <= max: return True
                else: return f'Choose a value between {min} and {max}'
            return validator

        def url_validator(*required):
            def validator(value):
                if all((var in value) for var in required):
                    return True
                else: return f'You need to use all required variables: {required}'
            return validator

        questions = [
            {
                'type': 'list',
                'name': 'settings_api',
                'message': 'Rapid API:',
                'choices': [
                    Separator('= Connection ='),
                    {'name': 'Pagination', 'value': 'single_fetch_size'},
                    {'name': 'Interval for generation assertion', 'value': 'max_wait_time'},
                    Separator('= URLs ='),
                    {'name': 'Endpoint', 'value': 'endpoint'},
                    {'name': 'Report listing', 'value': 'list'},
                    {'name': 'Report generation', 'value': 'generate'},
                    {'name': 'Report instance history', 'value': 'instance_history'},
                    {'name': 'Report instance download', 'value': 'download'},
                    {'name': 'Exit', 'value': self.EXIT}]
            },{
                'type': 'input',
                'name': 'value',
                'message': 'Edit pagination:',
                'default': lambda answer: str(SETTINGS.api[answer['settings_api']]),
                'when': lambda answer: answer.get('settings_api', False) == 'single_fetch_size',
                'validate': connection_validator(1,100),
                'filter': lambda value: int(value)
            }, {
                'type': 'input',
                'name': 'value',
                'message': 'Edit interval in seconds:',
                'default': lambda answer: str(SETTINGS.api[answer['settings_api']]),
                'when': lambda answer: answer.get('settings_api', False) == 'max_wait_time',
                'validate': connection_validator(10, 60),
                'filter': lambda value: int(value)
            }, {
                'type': 'input',
                'name': 'value',
                'message': 'Edit endpoint URL:',
                'default': lambda answer: SETTINGS.api[answer['settings_api']],
                'when': lambda answer: answer.get('settings_api', False) == 'endpoint'
            }, {
                'type': 'input',
                'name': 'value',
                'message': 'Edit URL (page and request size vars required):',
                'default': lambda answer: SETTINGS.api[answer['settings_api']],
                'when': lambda answer: answer.get('settings_api', False) == 'list',
                'validate': url_validator('$PAGE', '$SIZE')
            }, {
                'type': 'input',
                'name': 'value',
                'message': 'Edit URL (report id var required):',
                'default': lambda answer: SETTINGS.api[answer['settings_api']],
                'when': lambda answer: answer.get('settings_api', False) == 'generate',
                'validate': url_validator('$ID')
            }, {
                'type': 'input',
                'name': 'value',
                'message': 'Edit URL (report id and instance id var required):',
                'default': lambda answer: SETTINGS.api[answer['settings_api']],
                'when': lambda answer: answer.get('settings_api', False) in ('instance_history', 'download'),
                'validate': url_validator('$ID', '$INSTANCE')}]

        for choice in self.prompt(questions):
            SETTINGS.api[choice['settings_api']] = choice['value']
            SETTINGS.save()
            return 'settings_api'

    def settings_auto(self):
        questions = [
            {
                'type': 'list',
                'name': 'settings_auto',
                'message': 'Edit list of automatically processed reports:',
                'choices': [
                    {'name': 'Add','value': 'add'},
                    {'name': 'Edit individually','value': 'report'},
                    {'name': 'Delete multiple','value': 'delete'},
                    {'name': 'Exit','value': self.EXIT}],
                'when': lambda x: len(SETTINGS.autoprocess)},
            {
                'type': 'list',
                'name': 'settings_auto',
                'message': 'Edit list of automatically processed reports:',
                'choices': [
                    {'name': 'Add','value': 'add'},
                    {'name': 'Exit','value': self.EXIT}],
                'when': lambda x: not len(SETTINGS.autoprocess)},
            {
                'type': 'input',
                'name': 'add',
                'message': 'Enter report name or regex:',
                'when': lambda answer: answer['settings_auto'] == 'add'
            }, {
                'type': 'list',
                'name': 'report',
                'message': 'Select report to edit:',
                'choices': [name for name in SETTINGS.autoprocess],
                'when': lambda answer: answer['settings_auto'] == 'report'
            }, {
                'type': 'input',
                'name': 'edit',
                'message': 'Edit report name or regex, erase to delete:',
                'default': lambda answer: answer['report'],
                'when': lambda answer: 'report' in answer
            }, {
                'type': 'checkbox',
                'name': 'delete',
                'message': 'Edit list of automatically processed reports:',
                'choices': [{'name': name} for name in SETTINGS.autoprocess],
                'when': lambda answer: answer['settings_auto'] == 'delete'
            }]

        def delete(*args):
            for item in args:
                SETTINGS.autoprocess.remove(item)
            SETTINGS.save()
        
        for choice in self.prompt(questions):
            if choice['settings_auto'] == 'add' and (name := choice['add'].strip()):
                SETTINGS.autoprocess.append(name)
                SETTINGS.save()
            elif choice['settings_auto'] == 'report':
                if edit := choice['edit'].strip():
                    index = SETTINGS.autoprocess.index(choice['report'])
                    SETTINGS.autoprocess[index] = edit
                    SETTINGS.save()
                else: delete(choice['report'])
            elif choice['settings_auto'] == 'delete':
                delete(*choice['delete'])
            return 'settings_auto'




