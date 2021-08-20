from .config import CONFIG, log
import re, os

class Discover:


    pdfs, folders, path = [], [], None


    def __init__(self, path: str = None) -> None:
        self.path = path
        if self.path: self.walk()
    

    def is_region_code(self, region:str) -> bool:
        log.info(f'Checking for region: {CONFIG["region_code_pattern"]} in {region}')
        return bool(re.match(CONFIG['region_code_pattern'], region))


    def attributes_from_filename(self, filename:str) -> dict:
        matches = re.match(CONFIG['naming_pattern'], filename)
        try:
            attributes = {
                'filename': filename,
                'type': matches.group('type')}
            try:
                attributes['region'] = matches.group('region')
            except:
                log.debug('Filename doesn\'t specify report region')
            log.info(f'Parsed filename for attributes: {attributes}')
            return attributes
        except:
            log.warning(f'Could not get required attributes from file name, check if it is correct: {filename}')
            return False


    def get_region_from_path(self, path:str) -> str:
        # Only match region from last folder, allow for parent folders and closin slashes in the path
        matches = re.match(r'.*' + CONFIG['region_code_pattern'] + r'[\/\\]{0,2)', path)
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
                    