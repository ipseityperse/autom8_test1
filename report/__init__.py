from PyInquirer import prompt, Separator

from .config import SETTINGS, LOG_LEVEL
from .discover import Discover
from .scanner import Scanner
from .rapid import API

import os, threading, time

class Dialog:

    EXIT = False
    API = False

    def prompt(self, questions):
        while True:
            answer = prompt(questions)
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
            else:
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
                'when': lambda answer: answer['settings_scan_link'] and answer['settings_scan_link'] != 'add'
            },
            {
                'type': 'list',
                'name': 'edit',
                'message': 'Select link',
                'choices': [preset for preset in SETTINGS.scanner] + [
                    {'name': 'Exit', 'value': self.EXIT}
                ],
                'when': lambda answer: answer['settings_scan_link'] == 'add'
            },
            {
                'type': 'input',
                'name': 'add',
                'message': 'Enter report name or regex:',
                'default': '',
                'when': lambda answer: answer['settings_scan_link'] == 'add' and answer['edit']
            }]
        
        for choice in self.prompt(questions):
            if choice['settings_scan_link'] == 'add':
                name = choice['add']
                link = choice['edit']
            else:
                if choice['edit'] == 'delete':
                    SETTINGS.pdf.pop(choice['settings_scan_link'])
                    SETTINGS.save()
                    return 'settings_scan_link'
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


    def scan(self):

        def path_validator(path):
            path = path.strip()
            return (
                os.path.isfile(path) and path[-4:] in ('.pfd', '.PDF')
                or os.path.isdir(path)
                or path == ''
                or 'Enter a valid path or leave empty to exit')

        def cut_filter(values:str) -> tuple[str, int, tuple[int]]:
            values = values.strip()
            if values == 'auto': return values
            if not len(values): return False

            values:list = [int(value.strip()) for value in values.split('|')]
            page = values.pop(0)
            
            if len(values) == 4: return [page, tuple(values)]
            return [page]
            
        def cut_validator(values:str) -> str:
            try:
                cut_filter(values)
            except:
                return """For custom cut, use following format: page (| cut start X | start Y | end X | end Y)"""
            else:
                return True

        for scan in self.prompt([{
                'type': 'input',
                'name': 'path',
                'message': 'Enter path to a PDF file or a directory\nEmpty to exit:',
                'validate': path_validator,
                'filter': lambda path: path.strip() != '' and path or False
            }, {
                'type': 'input',
                'name': 'cut',
                'message': 'Scanner may try to process known reports (auto)\nYou can also provide scan parameters\nLeave empty to exit:',
                'default': 'auto',
                'validate': cut_validator,
                'filter': cut_filter,
                'when': lambda answers: answers['path']
            }, {
                'type': 'list',
                'name': 'apply',
                'message': 'Custom scan parameters:',
                'choices': [
                    {'name': 'Override all known presets', 'value': 'all'},
                    {'name': 'Only apply when unknown document', 'value': 'unknown'},
                    {'name': 'Exit','value': self.EXIT}],
                'when': lambda answers: answers.get('cut', False) and isinstance(answers['cut'], tuple)
            }, {
                'type': 'input',
                'name': 'output',
                'message': 'Enter output directory\nEmpty to exit:',
                'filter': lambda path: path.strip() != '' and path or False,
                'when': lambda answers: answers.get('cut', False)
            }]):

            if scan.get('output', False):
                page, cut = None, None

                def scan_from_preset(pdf):
                    if isinstance(pdf['preset'], (list,tuple)):
                        [Scanner(
                            path = pdf['path'],
                            template=preset,
                            save=True,
                            output_path=scan['output'],
                            output_filename=f"{pdf['filename'][:-4]} ({preset})")
                            for preset in pdf]

                    else: Scanner(
                        path = pdf['path'],
                        template=pdf['preset'],
                        save=True,
                        output_path=scan['output'],
                        output_filename=pdf['filename'][:-4])

                if isinstance(scan['cut'], tuple):
                    custom_preset = {
                        'page': scan['cut'].pop(0),
                        'crop': scan['cut'] and scan['cut'][0] or (0,0,9999,9999)
                    }

                    def custom_scan(pdf):
                        Scanner(
                            path = pdf['path'],
                            save=True,
                            output_path=scan['output'],
                            output_filename=pdf['filename'][:-4]
                            **custom_preset)

                    if scan['apply'] == 'all':
                        [custom_scan(pdf) for pdf in Discover(scan['path']).pdfs]
                    elif scan['apply'] == 'unknown':
                        pdfs = Discover(scan['path']).pdfs
                        for pdf in pdfs:
                            if 'preset' in pdf:
                                scan_from_preset(pdf)
                            else:
                                custom_preset(pdf)
                    else: return self.EXIT

                elif scan['cut'] == 'auto':
                    [scan_from_preset(pdf) for pdf in Discover(scan['path']).pdfs_with_preset]
                     
            else: return self.EXIT

    def login(self):
        if not self.API:
            for credentials in self.prompt([
                {
                    'type': 'input',
                    'name': 'mail',
                    'message': 'Login to Rapid7 to continue\nYour credentials will not be saved\nMail:',
                }, {
                    'type': 'password',
                    'name': 'password',
                    'message': 'Password:'}]):
                rapid = API(credentials['mail'], credentials['password'])
                if rapid.auth_status:
                    self.API = rapid
                    self.API.load_report_list(True)
                    return True
                else: print("Can not log you in, try again")

    def download_threading(self, path, ids, scan=False):
        threads = []
        ids_len = len(ids)
        wait = SETTINGS.api['max_wait_time'] / ids_len
        wait = min(max(wait, .05), 2)
        print(f'\nStarting {ids_len} threads ({ids_len * wait}s) in the background\n\nYou can continue to work while waiting\n\n=== DO NOT CLOSE AUTOM8 ===\n')
        for id in ids:
            threads.append(threading.Thread(target=self.API.download, args=(id, path)))
            threads[-1].start()
            time.sleep(wait)
        [t.join() for t in threads]
        print("=== REPORT DOWNLOAD COMPLETED ===")

        if scan:
            print("=== SCANNING ===")
            def scan_from_preset(pdf):
                if isinstance(pdf['preset'], (list,tuple)): [
                    Scanner(
                        path = pdf['path'],
                        template=preset,
                        save=True,
                        output_path=path,
                        output_filename=f"{pdf['filename'][:-4]} ({preset})")
                        for preset in pdf]

                else:
                    Scanner(
                        path = pdf['path'],
                        template=pdf['preset'],
                        save=True,
                        output_path=path,
                        output_filename=pdf['filename'][:-4])
            [scan_from_preset(pdf) for pdf in Discover(path).pdfs_with_preset]
            print("=== SCANNING COMPLETED ===")

    def download_start(self, *ids, scan=False):
        question  = {
            'type': 'input',
            'message': 'Enter download location\nEmpty to exit:',
            'name': 'path'}
        for path in self.prompt(question):
            if not path: return self.EXIT
            if not os.path.exists(path):
                try: os.makedirs(path)
                except FileExistsError: pass
            threads =threading.Thread(target=self.download_threading, args=(path, ids, scan)).start()
            return self.EXIT

    def download(self):
        print('Add report name/regex\n"done" to start downloading\n"list" will print added downloads\n"auto" will import autoprocessing list\nEmpty to exit')
        downloads, question = [], {
            'type': 'input',
            'name': 'download',
            'message': 'name/regex/auto/list/done:',
            'default': ''}

        for download in self.prompt(question):

            if not download: return self.EXIT
            else: download = download.strip()

            if download == 'auto': downloads += SETTINGS.autoprocess

            elif download in ('list', 'ls'): 
                print('\nIndex: entry\n')
                for i in range(len(downloads)):
                    print(f'{i}: {downloads[i]}')
                print('\nType "remove index(,index,index,...)" to remove it from the list')
            
            elif download.startswith('remove'):
                raw = download[6:].split(',')
                remove = []
                for r in raw:
                    try: remove.append(download[int(r.strip())])
                    except IndexError: print(f'{r} is out of index')
                    except ValueError: print(f'{r} is not a number')
                for r in remove:
                    try: downloads.remove(r)
                    except: pass
                    
            elif download == 'done':
                self.login()
                print('Searching for matching reports')
                ids = self.API.index.search_multiple_names(*downloads, iterator=False)
                len_ids = len(ids)
                print(f'Found {len_ids} reports out of {len(self.API.index.ids)} available')
                if not len_ids: continue
                for id in ids:
                    print(f"ID:{id} name:{self.API.index.ids[id]['name']} template:{self.API.index.ids[id]['template']}")
                self.download_start(*ids)
                return self.EXIT
            else: downloads.append(download)


    def auto(self):
        self.login()
        print("This will try to process these reports:")
        [print(report) for report in SETTINGS.autoprocess]
        for confirm in self.prompt({
            'type': 'confirm',
            'message': 'Do you want to continue?',
            'name': 'continue',
            'default': True}):
            if confirm:
                print('Searching for matching reports')
                ids = self.API.index.search_multiple_names(*SETTINGS.autoprocess, iterator=False)
                len_ids = len(ids)
                print(f'Found {len_ids} reports out of {len(self.API.index.ids)} available')
                if not len_ids: return None
                for id in ids:
                    print(f"ID:{id} name:{self.API.index.ids[id]['name']} template:{self.API.index.ids[id]['template']}")
                return self.download_start(*ids, scan=True)
            return self.EXIT



            




               

