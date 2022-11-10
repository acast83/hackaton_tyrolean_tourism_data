import datetime
import tshared.utils.ipc as ipc


async def generate_pdf(request, document_type_id, id_instance):
    return await ipc.call(request, 'pdf_generator', 'GET', f'/{document_type_id}/{id_instance}')


async def lookup_pdf_generator_document_types(request, last_updated: datetime.datetime = None):
    return await ipc.lookup_base(request, 'pdf_generator', '/lookups/document_types', last_updated)

# {{ ipc_function }}{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}
