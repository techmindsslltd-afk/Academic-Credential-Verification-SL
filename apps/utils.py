
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
import os
from django.conf import settings
from xhtml2pdf import pisa
from django.contrib.staticfiles import finders

from xhtml2pdf import pisa


def link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those
    resources
    """
    result = finders.find(uri)
    if result:
        if not isinstance(result, (list, tuple)):
            result = [result]
            result = list(os.path.realpath(path) for path in result)
            path=result[0]
        else:
            sUrl = settings.STATIC_URL        # Typically /static/
            sRoot = settings.STATIC_ROOT      # Typically /home/userX/project_static/
            mUrl = settings.MEDIA_URL         # Typically /media/
            mRoot = settings.MEDIA_ROOT       # Typically /home/userX/project_static/media/

            if uri.startswith(mUrl):
                path = os.path.join(mRoot, uri.replace(mUrl, ""))
            elif uri.startswith(sUrl):
                path = os.path.join(sRoot, uri.replace(sUrl, ""))
            else:
                return uri
    # make sure that file exists
    if not os.path.isfile(path):
        raise Exception(
            'media URI must start with %s or %s' % (sUrl, mUrl)
                    )
    return path
        
def render_to_pdf_2(template_src, context_dict={}):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None

def render_pdf_view(template_src, context_dict={}):
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="report.pdf"'
    
    # Find the template and render it
    template = get_template(template_src)
    html = template.render(context_dict)

    # Create a PDF
    pisa_status = pisa.CreatePDF(
       html, dest=response, link_callback=fetch_resources
    )
    
    # Handle errors if any
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response



def fetch_resources(uri, rel):
    """
    Callback function to fetch resources for xhtml2pdf.
    Handles local and absolute paths.
    """
    if uri.startswith('http://') or uri.startswith('https://'):
        return uri  # for external URLs, return the URL itself

    # Construct the local path
    path = os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ""))
    
    # Check if the file exists
    if os.path.isfile(path):
        return path
    else:
        return ''  # or raise an exception if preferred