from .config import CONFIG, SETTINGS, log
import re, os

class Discover:


    pdfs, path = [], None

    def pdfs_with_attribute(self, attribute):
        return [pdf for pdf in self.pdfs if attribute in pdf]
    
    @property
    def pdfs_with_preset(self):
        return self.pdfs_with_attribute('preset')

    def __init__(self, path:str = None) -> None:
        self.path = path
        if os.path.isdir(self.path): self.walk()
        elif os.path.isfile(self.path): self.file(*os.path.split(self.path)) 
    

    def is_region_code(self, region:str) -> bool:
        log.info(f'Checking for region: {CONFIG["region_code_pattern"]} in {region}')
        return bool(re.match(CONFIG['region_code_pattern'], region))


    def attributes_from_filename(self, filename:str) -> dict:
        matches = re.match(CONFIG['naming_pattern'], filename)

        try: attributes = {'filename': filename, 'type': matches.group('type')}
        except:
            log.warning(f'Could not get required attributes from file name, check if it is correct: {filename}')
            return False

        try: attributes['region'] = matches.group('region')
        except: log.debug('Filename doesn\'t specify report region')

        for key, preset in SETTINGS.pdf.items():
            if re.match(key, attributes['type']):
                attributes['preset'] = preset

        log.info(f'Parsed filename for attributes: {attributes}')
        return attributes


    def get_region_from_path(self, path:str) -> str:
        # Only match region from last folder, allow for parent folders and closin slashes in the path
        matches = re.match(r'.*' + CONFIG['region_code_pattern'] + r'[\/\\]{0,2}', path)
        try:
            region = matches.group('region')
            log.debug(f'Parsed path for region code: {region}')
            return region
        except:
            log.debug(f'Path does not contain a region code: {path}')
            return False


    def get_path(self, path:str=None) -> str:
        if path := path or self.path or False:
            return path
        log.error('Path not provided')
        raise Exception('Path not provided')
        

    def walk(self, path:str=None):
        # Walk through the directories looking for pdfs
        for root, _, files in os.walk(self.get_path(path)):
            log.debug(f'Walking: {root}, {files}')
            for file in files:
                self.file(root, file)

    def file(self, root, file):
        if (os.path.isfile(os.path.join(root, file)) # If a file, has pdf extension,
            and file[-3:].lower() == 'pdf' # try to parse it for attributes
            and (attributes := self.attributes_from_filename(file))):
            # collect pdf attributes and add path, root folder
            found = {**attributes, 'root': root, 'path': os.path.join(root, file)}

            # skip region extraction from path if region present in atributes
            # and file region prefered over path region
            if 'region' in found and CONFIG['separate_by_regions']:
                log.debug(f"Accept filename region: {found['region']}")

            # else try to extract region from path
            elif region := self.get_region_from_path(root):
                log.debug(f'Extracting region from folder: {region}')
                found['region'] = region

            # else, warn about missing region code
            else:
                log.warning(f'Region could not be extracted from path or filename: {found}')
                    
            log.debug(f'Discovered PDF: {found}')
            self.pdfs.append(found)
                    