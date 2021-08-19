from .settings import SCANNER_DEFAULTS as conf
from .settings import log
from PIL import Image
import fitz, os

class Scanner:

    class PDFNotProvidedException(Exception):
        pass


    class PDFNotFoundException(Exception):
        pass

    
    working_pdf = False
    working_page = False
    working_pixels = False
    working_image = False


    def __init__(self, path:str=None, page:int=None, crop:tuple=None, template:str=None, save=False, output_path:str=conf['output_image_path'],
        output_filename=conf['output_image_filename']) -> None:
        log.debug(f"Scanner on")
        # Preload document if given the path
        if path:
            log.debug(f"Load document, path: {path}")
            self.scan(path)
        else:
            log.debug(f"No path provided, skipping init")
            return None
        # Preload scan template data
        if template:
            log.debug(f"Loading scan template: {template}")
            from .settings import PDF2IMG_EXPORT_PRESETS as preset
            if template in preset:
                page_temp = preset[template]['page']
                crop_temp = preset[template]['crop']
                log.info(f"Scan template: {preset[template]}")
            else:
                log.warning(f"Provided template does not exist: {template}")
        # Skip template if custom page/crop
        if not page and page_temp:
            page = page_temp
            if not crop: 
                crop = crop_temp
        # Process page image
        if page:
            self.page(page)
            if crop:
                self.crop(crop)
        else:
            return None
        # Autosave on demand:
        if save:
            self.save(path=output_path, filename=output_filename)


    def scan(self, pdf_path:str):
        log.debug(f"Document path: {pdf_path}")
        # Try to load document from path, return it or raise exception when failed
        try:
            self.working_pdf = fitz.open(pdf_path)
            return self.working_pdf
        except:
            raise self.PDFNotFoundException(f'Could not open provided document: {pdf_path}')
    

    @property
    def matrix(self, zoom_x=conf['zoom']['x'], zoom_y=conf['zoom']['y'], rotate=conf['rotate']):
        # Can be used as property with default values or as a function with custom values
        # Returns a matrix to be filled with pixels
        log.debug(f"Creating matrix: zoom_x:{zoom_x}, zoom_y:{zoom_y}, rotate:{rotate}")
        return fitz.Matrix(zoom_x, zoom_y).preRotate(rotate)


    def page(self, number:int, pdf=None):
        log.debug(f"Getting page {number}, pdf={pdf}")
        if not pdf: # If pdf is not passed, try to use last parsed pdf
            if self.working_pdf:
                pdf = self.working_pdf
                log.debug(f"PDF not provided, using last scanned document")
            else:
                log.error(f"PDF not provided, nor scanned, can not get page")
                raise self.PDFNotfoundException("Provide scan to get a page")
        # Validate page number and retrive it
        try:
            # Shift to allign with array indexing (pages start from 1, index from 0)
            number = int(number) - 1
            page = pdf[number]
            log.info(f'Page {number+1} loaded')
        except ValueError:
            raise ValueError(f'{type(number)} can not be a page number: {number}')
        except KeyError:
            raise KeyError(f'Page[{number+1}] not found, page count: {pdf.pageCount}')
        # Set current working page and return it
        self.working_page = page
        return self.working_page


    @property
    def pixelmap(self, page=None, matrix=None, colorspace=conf['colorspace']):
        # Can be used as a property given a working page being selected before
        # Or as a function where the page and custom matrix can be passed
        log.debug(f"Converting page to pixels, page={page}, matrix={matrix}")
        if not page: # If page is not passed, try to use last parsed page
            if self.working_page:
                page = self.working_page
                log.debug(f"Page not provided, using last selected page")
            else:
                log.error(f"Page not provided, nor selected before")
                raise self.PDFNotfoundException("Provide page to get a pixelmap")
        if not matrix:
            log.debug(f"Matrix not provided, using default values")
            matrix = self.matrix
        # Fill matrix with pixels from page, save state and return
        self.working_pixels = page.getPixmap(matrix=matrix, alpha=False, colorspace=colorspace)
        return self.working_pixels


    @property
    def image(self, pixels=None, colorspace=conf['colorspace']):
        if not pixels:
            if self.working_pixels:
                pixels = self.working_pixels
                log.debug(f"PixMap not provided, using last used pixels")
            elif self.working_page:
                pixels = self.pixelmap
                log.debug(f"PixMap not provided, generating from last used page")
            else:
                log.error(f"Page not provided, nor selected before")
                raise self.PDFNotfoundException("Provide page to get a pixelmap")
        try:
            img = Image.frombytes(colorspace, [pixels.width, pixels.height], pixels.samples)
        except:
            log.error(f"Could not convert to PIL Image")
            raise Exception("Could not convert to PIL Image")
        self.working_image = img
        return self.working_image


    def crop(self, points:tuple, image=None):
        if not image:
            if self.working_image:
                image = self.working_image
                log.info("Image not provided, loading working image")
            else:
                image = self.image
        self.working_image = image.crop(points)
        return self.working_image


    def image_path(self, path, filename, format):
        if not os.path.exists(path):
            try:
                os.makedirs(path)
                log.debug(f'Output image path does not exist, creating folder {path}')
            except FileExistsError:
                log.debug(f'Output image path already created by a different thread')
        if callable(filename):
            filename = filename()
        try:
            filename = str(filename)
            return f'{path}/{filename}.{format.lower()}'
        except:
            raise ValueError('Filename is not a valid string and can not be converted to one.')


    def save(self, image=None, path:str=conf['output_image_path'],
        filename=conf['output_image_filename'], format:str=conf['output_image_format']) -> str:
        if not image:
            if self.working_image:
                image = self.working_image
                log.info('Image not provided, using last working image')
            else:
                image = self.image
        path = self.image_path(path, filename, format)
        image.save(path, format)
        return path
