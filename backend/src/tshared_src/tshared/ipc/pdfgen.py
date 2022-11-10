import datetime
import tshared.utils.ipc as ipc


async def generate_original_pdf(request, document_type_id, id_ticket):
    return await ipc.call(request, 'pdfgen', 'PATCH', f'/{document_type_id}/{id_ticket}')


async def lookup_pdfgen_document_types(request, last_updated: datetime.datetime = None):
    return await ipc.lookup_base(request, 'pdfgen', '/lookups/document_types', last_updated)

# {{ ipc_function }}{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}
