import yaml
import json


async def CREATE_DEAL(data, lang, activity_mode=False, created_by_display_name=None):
    message = f'<div><b>{created_by_display_name if activity_mode else ""}</b> has created a deal for customer'
    if lang == 'it':
        message = f'<div><b>{created_by_display_name if activity_mode else ""}</b> ha creato un accordo per un cliente'

    elif lang == 'de':
        message = f'<div><b>{created_by_display_name if activity_mode else ""}</b> hat einen deal für den kunden erstellt'

    if data and 'deal' in data:
        if 'company' in data["deal"]:
            if 'name' in data["deal"]["company"] and data["deal"]["company"]["name"]:
                try:
                    message += f' <u>{data["deal"]["company"]["name"]}</u>'
                except:
                    pass
    message += "</div>"
    return message


async def ADD_ATTACHMENT(data, lang, activity_mode=False, created_by_display_name=None):
    message = f'<div><b>{created_by_display_name if activity_mode else ""}</b> has uploaded a document:'
    if lang == 'it':
        message = f'<div><b>{created_by_display_name if activity_mode else ""}</b> ha caricato un documento: '
    if lang == 'de':
        message = f'<div><b>{created_by_display_name if activity_mode else ""}</b> hat ein dokument hochgeladen: '

    if data and 'filename' in data:
        try:
            message += f" {data['filename']}"
        except:
            pass
    message += "</div>"
    return message


async def DELETE_DEAL(data, lang, activity_mode=False, created_by_display_name=None):
    message = f'<div><b>{created_by_display_name if activity_mode else ""}</b> has deleted a deal <u>{data["company_name"] if "company_name" in data else ""}</u>'
    if lang == 'it':
        message = f'<div><b>{created_by_display_name if activity_mode else ""}</b> ha cancellato un accordo <u>{data["company_name"] if "company_name" in data else ""}</u>'

    if lang == 'de':
        message = f'<div><b>{created_by_display_name if activity_mode else ""}</b> hat einen deal <u>{data["company_name"] if "company_name" in data else ""}</u> gelöscht'
    if data and 'reason' in data:
        try:
            message += f", reason: {data['reason']}"
        except:
            pass
    message += "</div>"
    return message


async def UPDATE_DEAL(data, lang, activity_mode=False, created_by_display_name=None):
    text = '<div>'
    for attr in data['updated']:
        _old, _new = data['updated'][attr]
        if _old in (None, 'None'):
            if lang == 'en':
                text += f'<b>{created_by_display_name if activity_mode else ""}</b> has updated a deal <u>{data["company_name"] if "company_name" in data else ""}</u>, set property {translate_attribute(attr=attr, lang=lang)} to {_new}'
            elif lang == 'it':
                text += f'<b>{created_by_display_name if activity_mode else ""}</b> ha aggiornato un affare <u>{data["company_name"] if "company_name" in data else ""}</u>,  ha impostato la proprietà {translate_attribute(attr=attr, lang=lang)} su {_new}'
            elif lang == 'de':
                text += f'<b>{created_by_display_name if activity_mode else ""}</b> ha aggiornato un affare <u>{data["company_name"] if "company_name" in data else ""}</u>, hat die Eigenschaft {translate_attribute(attr=attr, lang=lang)} auf {_new} gesetzt'

        elif _new in (None, 'None'):
            if lang == 'en':
                text += f'<b>{created_by_display_name if activity_mode else ""}</b> has updated a deal <u>{data["company_name"] if "company_name" in data else ""}</u>, cleared property {translate_attribute(attr=attr, lang=lang)} from {_old}'
            elif lang == 'it':
                text += f'<b>{created_by_display_name if activity_mode else ""}</b> ha aggiornato un affare <u>{data["company_name"] if "company_name" in data else ""}</u>, ha cancellato la proprietà {attr} da {_old}'
            elif lang == 'de':
                text += f'<b>{created_by_display_name if activity_mode else ""}</b> hat einen Deal aktualisiert <u>{data["company_name"] if "company_name" in data else ""}/u>, hat Eigenschaft {translate_attribute(attr=attr, lang=lang)} von {_old} gelöscht'

        else:
            if lang == 'en':
                text += f'<b>{created_by_display_name if activity_mode else ""}</b> as updated a deal <u>{data["company_name"] if "company_name" in data else ""}</u>, changed property {translate_attribute(attr=attr, lang=lang)} from {_old} to {_new}'
            elif lang == 'it':
                text += f'<b>{created_by_display_name if activity_mode else ""}</b> ha aggiornato un affare <u>{data["company_name"] if "company_name" in data else ""}</u>,ha cambiato la proprietà {translate_attribute(attr=attr, lang=lang)} da {_old} a {_new}'
            elif lang == 'de':
                text += f'<b>{created_by_display_name if activity_mode else ""}</b> hat einen Deal aktualisiert <u>{data["company_name"] if "company_name" in data else ""}</u>, hat die Eigenschaft {translate_attribute(attr=attr, lang=lang)} von {_old} in {_new} geändert'
    text += '</div>'

    return text


async def ADD_EXTERNAL_POST_FROM_IMPRESA(data, lang):
    del data["action"]
    if lang == 'en':
        message = f'<div>{yaml.dump(json.loads(json.dumps(data)))} </div>'

        return message


supported_actions = ('CREATE_DEAL', 'UPDATE_DEAL', 'DELETE_DEAL', 'ADD_ATTACHMENT', 'ADD_EXTERNAL_POST_FROM_IMPRESA')


async def messages(handler, data, lang='en', activity_mode=False, created_by_display_name=None):
    if not data or 'action' not in data:
        return "TODO / missing action in flow"

    a = data['action']
    if data['action'] not in supported_actions:
        return f"TODO / action {data['action']} is not implemented"

    if a == 'CREATE_DEAL': return await CREATE_DEAL(data, lang, activity_mode=activity_mode, created_by_display_name=created_by_display_name)
    if a == 'UPDATE_DEAL': return await UPDATE_DEAL(data, lang, activity_mode=activity_mode, created_by_display_name=created_by_display_name)
    if a == 'DELETE_DEAL': return await DELETE_DEAL(data, lang, activity_mode=activity_mode, created_by_display_name=created_by_display_name)
    if a == 'ADD_ATTACHMENT': return await ADD_ATTACHMENT(data, lang, activity_mode=activity_mode, created_by_display_name=created_by_display_name)
    if a == 'ADD_EXTERNAL_POST_FROM_IMPRESA': return await ADD_EXTERNAL_POST_FROM_IMPRESA(data, lang)

    return "NOT IMPLEMENTED"


def translate_attribute(attr: str, lang: str):
    attribute_translations = {
        'deal classification': {'en': 'deal classification', 'it': 'classification_id', 'de': 'classification_id'},
        'company site': {'en': 'company site', 'it': 'company_name', 'de': 'company_name'},
        'service types': {'en': 'service types', 'it': 'service_type_ids', 'de': 'service_type_ids'},
        'short_description': {'en': 'short_description', 'it': 'descrizione dettagliata', 'de': 'kurze beschreibung'},
        'detailed_description': {'en': 'detailed description', 'it': 'breve descrizione', 'de': 'detaillierte beschreibung'},
        'potential_revenue': {'en': 'potential revenue', 'it': 'potential_revenue', 'de': 'potential_revenue'},
        'revenue_probability_percent': {'en': 'revenue probability percent', 'it': 'revenue_probability_percent', 'de': 'revenue_probability_percent'},
        'realrevenue': {'en': 'real revenue', 'it': 'real_revenue', 'de': 'real_revenue'},
        'contact person': {'en': 'contact person', 'it': 'contact_person_display_name', 'de': 'contact_person_display_name'},
        'sales person': {'en': 'sales person', 'it': 'sales_person_display_name', 'de': 'sales_person_display_name'},
        'sales team lead': {'en': 'sales team lead', 'it': 'sales_team_lead_display_name', 'de': 'sales_team_lead_display_name'},
        'participants': {'en': 'participants', 'it': 'participants_data', 'de': 'participants_data'},
        'deal stage': {'en': 'deal stage', 'it': 'stage_id', 'de': 'stage_id'},
        'deal status': {'en': 'deal status', 'it': 'status_id', 'de': 'status_id'},
        'estimated_closing_date': {'en': 'estimated closing date', 'it': 'estimated_closing_date', 'de': 'estimated_closing_date'},
        'closed_timestamp': {'en': 'closed timestamp', 'it': 'closed_timestamp', 'de': 'closed_timestamp'},
        'fiscal_period': {'en': 'fiscal_period', 'it': 'fiscal_period', 'de': 'fiscal_period'},
        'deal source': {'en': 'deal source', 'it': 'source_id', 'de': 'source_id'},
        'deal_quality': {'en': 'deal quality', 'it': 'qualità dell affare', 'de': 'deal-qualität'}}
    try:
        return attribute_translations[attr][lang]
    except:
        return attr