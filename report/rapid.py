from .settings import (
    RAPID_REPORT_GENERATE,
    RAPID_REPORT_DOWNLOAD,
    RAPID_REPORT_LIST,
    RAPID_LIST_REPORTS_SIZE,
    log
)
from typing import Dict, List, Union, Iterator
import requests, json, threading, re


class Index:
    class IncompatibleAddOperation(ValueError):
        pass
    
    # Predefine indexes and data structure
    ids:Dict[int, Dict[str, str]] = {}
    names:Dict[str, List[int]] = {}
    templates:Dict[str, List[int]] = {}
    required_attributes:tuple = ('id', 'name', 'template')

    def add_id(self, id:int, name:str, template:str) -> Dict[int, Dict[str, str]]:
        """Adds a new id to the index and associates it
        with a name and a template name of a report.

        Args:
            id (int): rapid report identifier.
            name (str): rapid report name.
            template (str): rapid report template name.

        Returns:
            Dict[int, Dict[str, str]]: newly added index entry.
        """
        new_entry = {id: {'name': name, 'template': template}}
        self.ids.update(new_entry)
        return new_entry

    def add_template(self, id:int, template:str) -> int:
        """Adds report identifier to templates index.

        Args:
            id (int): rapid report identifier.
            template (str): rapid report template name.

        Returns:
            int: rapid report identifier.
        """
        if template in self.templates:
            if id not in self.templates[template]:
                self.templates[template].append(id)
        else:
            self.templates.update({template:[id]})
        return id

    def add_name(self, id:int, name:str) -> int:
        """Adds report identifier to names index.

        Args:
            id (int): rapid report identifier.
            name (str): rapid report name.

        Returns:
            int: rapid report identifier.
        """
        if name in self.names:
            if id not in self.names[name]:
                self.names[name].append(id)
        else:
            self.names.update({name:[id]})
        return id

    def add(self, id:int, name:str, template:str) -> Dict[int, Dict[str, str]]:
        """Adds report details to all indexes.

        Args:
            id (int): rapid report identifier.
            name (str): rapid report name.
            template (str): rapid report template name.

        Returns:
            Dict[int, Dict[str, str]]: Newly added index entry.
        """        
        self.add_template(id=id, template=template)
        self.add_name(id=id, name=name)
        return self.add_id(id=id, name=name, template=template)

    def __add__(self, other:Union[dict, list, tuple]) -> Dict[int, Dict[str, str]]:
        """Provides interface for + operator.

        Args:
            other (Union[dict, list, tuple]): Dicts with Index.required_attribues
        or List|Tuple with values corresponding to Index.add arguments.

        Raises:
            self.IncompatibleAddOperation: When provided Dict|List|Tuple does not comply.
            with index structures as stated in argument descriptions.

        Returns:
            Dict[int, Dict[str, str]]: Index entry as interpreted while adding provided values.
        """        
        if isinstance(other, dict):
            required_attributes_check = (attribute in other for attribute in self.required_attributes)
            if all(required_attributes_check) and len(other) == len(self.required_attributes):
                return self.add(**other)
        elif isinstance(other, (list, tuple)):
            return self.add(*other)
        raise self.IncompatibleAddOperation(f"Data can not be added to Rapid Index: {other}") 

    def __getitem__(self, key:int) -> Dict[str, str]:
        """Shurtcut for accessing Index.ids.

        Args:
            key (int): rapid report identifier.

        Returns:
            Dict[str, str]: parameters of requested report.
        """        
        return self.ids[key]
    
    def search_names(self, regex:str, iterator:bool=True) -> Union[List[int], Iterator[int]]:
        """Search for names that match the given regex.

        Args:
            regex (str): regular expresion to match names with.
            iterator (bool, optional): Returns an iterator if True, or a list if False.
            Defaults to True.

        Returns:
            Union[List[int], Iterator[int]]: An iterator or a list of ids with matching names.
        """        
        generator = (id for name, ids in self.names.items() if re.match(regex, name) for id in ids)
        return iterator and generator or [item for item in generator]

    def search_multiple_names(self, *regex:str, iterator:bool=True) -> Union[List[int], Iterator[int]]:
        """A shortcut to create one search from multiple regular expressions.

        Args:
            *regex (str): regular expresions to match names with.
            iterator (bool, optional): Returns an iterator if True, or a list if False.
            Defaults to True.

        Returns:
            Union[List[int], Iterator[int]]: An iterator or a list of ids with matching names.
        """        
        return self.search_names('|'.join(f'({option})' for option in regex), iterator)

class Rapid:

    def __init__(self, mail:str, password:str) -> None:
        self.auth = (mail, password)
        self.index = Index()

    def generate_report(self, id) -> str:
        return requests.post(
            RAPID_REPORT_GENERATE.substitute(id=id),
            auth=self.auth)

    def download_report(self, id) -> str:
        return requests.get(
            RAPID_REPORT_DOWNLOAD.substitute(id=id),
            auth=self.auth)

    def resources_to_index(self, resources:dict) -> None:
        for report in resources:
            # Only index needed info
            print(report['id'], report['format'])
            if report['format'] == 'pdf':
                self.index.add(
                        id=report['id'],
                        name=report['name'],
                        template=report['template'])
    
    def reports_fetch_page(self, page:int, size:int=RAPID_LIST_REPORTS_SIZE) -> dict:
        # Create API url
        url:str = RAPID_REPORT_LIST.substitute(size=size, page=page)
        response:requests.Response = requests.get(url, auth=self.auth)
        print(url, response.status_code)
        return json.loads(response.text)

    def load_report_list_page(self, page:int, size:int=RAPID_LIST_REPORTS_SIZE) -> None:
        print("Loading page", page)
        data = self.reports_fetch_page(page=page, size=size)
        self.resources_to_index(data['resources'])

    def load_report_list(self):
        # Prefetch number of pages
        data:dict = self.reports_fetch_page(page=1)
        pages:int = int(data['page']['totalPages'])

        # Start seperate thread for each page
        threads:List[threading.Thread] = []
        for page in range(1, pages + 1):
            print('page', page)
            thread = threading.Thread(target=self.load_report_list_page, args=(page,))
            thread.start()
            threads.append(thread)
        for thread in threads:
            thread.join()

