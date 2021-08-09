from .settings import log
import fitz, os, uuid

def pdf2img(pdf_path:str, image_path:str, page_no:int) -> str:
    log.debug(f"pdf2img(pdf_path:{pdf_path}, image_path:{image_path}, page:{page_no})")
    pdf = fitz.open(pdf_path) # loads pdf as a fitz object

    # Trying to get the page, checking for wrong page number
    try:
        page_no = int(page_no) - 1
        page = pdf[page_no]
        log.info(f'pdf2img: Page {page_no} loaded')
    except ValueError:
        raise ValueError(f'pdf2img: {type(page_no)} can not be a page number: {page_no}')
    except:
        raise ValueError(f'pdf2img: Page not found: {page_no}, page count: {pdf.pageCount}')
    
    # Standarize output, no rotation, resolution and no alpha layer
    zoom = 1.33333333 # (1.33333333-->1056x816)   (2-->1584x1224)
    matrix = fitz.Matrix(zoom, zoom).preRotate(0)
    pixels = page.getPixmap(matrix=matrix, alpha=False)

    # Create folder if does not exist
    if not os.path.exists(image_path):
        os.makedirs(image_path)
        log.debug(f'pdf2img: image_path does not exist, creating folder {image_path}')
    
    # Save temp image
    temp_name = uuid.uuid4()
    temp_path = f"{image_path}/{temp_name}.png"
    pixels.writePNG(temp_path)
    log.debug(f'pdf2img: Temp PNG saved: {temp_path}')

    return temp_path



        
def test():
    pdf2img("./RRTest/ex/AAES/AAES - Top 10 Assets by Vurlnerabilities.PNG", "./", 1)