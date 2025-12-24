from grist.client import GristClient
from grist.models import GristColumn, GristTable
from app.settings import get_settings
from app.models import InternalWebhookContent, InternalWebhookField
from typing import List
from app.lib import grab
import logging
from app.lib import time_cache

logger = logging.getLogger(__name__)


def add_webhook_row(data: InternalWebhookContent, grist: GristClient) -> InternalWebhookContent:

    logger.info("requesting grist")

    grist_status, grist_tables = grist.list_tables()
    if grist_status != 200:
        raise ValueError(f"Unable to request Grist table list (status: {grist_status}): {grist_tables}")

    existing_table_name = None

    # find an existing table
    for table in grist_tables or list():
        if table.get("id") == data.survey_name.replace(" ", "_"):
            existing_table_name = table.get("id")
            break

    table_column_registration_id = GristColumn(
        id='regID',
        fields={
            'label': "Registration ID",
            'type': 'Int',
            'isFormula': True,
            'formula': '$id'
        }
    )

    table_column_paid = GristColumn(
        id='paid',
        fields={
            'label': 'Paid',
            'type': 'Choice',
            'formula': '"No"',
            'isFormula': False,
            'widgetOptions': {
                "widget": "TextBox",
                "choices": [
                    "Yes",
                    "No",
                    "Canceled"
                ],
                "alignment": "left",
                "choiceOptions": {}
            }
        }
    )

    table_data = GristTable(
        id=data.survey_name
    )

    table_data.columns.append(table_column_registration_id)
    for question in data.data or list():
        table_data.columns.append(GristColumn(
                id=question.id,
                fields={
                    "label": question.label,
                    "type": question.type
                }
            )
        )

    table_data.columns.append(table_column_paid)

    # create new table
    if existing_table_name is None:
        grist.add_table(table_data.model_dump())
    else:
        grist_status, existing_table_data = grist.list_cols(existing_table_name)

        if grist_status != 200:
            raise ValueError(f"Unable to request Grist columns (status: {grist_status}): {existing_table_data}")

        columns_to_add = list()

        existing_table_data_ids = [x.get("id") for x in existing_table_data]
        for column in table_data.columns:
            if column.id not in existing_table_data_ids:
                columns_to_add.append(column.model_dump())

        # add missing columns to existing table
        if len(columns_to_add) > 0:
            grist.add_cols(existing_table_name, columns_to_add)

    # add record data to table
    record_data = {x.id: x.value for x in data.data}

    grist_status, record_ids = grist.add_record(existing_table_name, record_data)

    if not 200 >= grist_status <= 299:
        raise ValueError(f"Unable to add Grist record to table (status: {grist_status}): {record_ids}")

    grist_status, records = grist.list_records(existing_table_name, {"id": record_ids})

    if grist_status != 200:
        raise ValueError(f"Unable to request newly added Grist record (status: {grist_status}): {records}")

    if len(records) != 1:
        raise ValueError(f"record returned for latest added id has len of {len(records)}")

    data.data = list()
    for column in table_data.columns:
        data.data.append(InternalWebhookField(
            id=column.id,
            value=records[0].get(column.id) or "",
            label=column.fields.get("label"),
            type=column.fields.get("type")
        ))

    logger.info(f"request finished - ID: {data.webhook_id}")

    return data


@time_cache(20)
def grist_export(grist_client: GristClient) -> List:

    settings = get_settings().grist

    return_data = []
    if len(settings.public_list_columns) == 0:
        return return_data

    status_code, table_data = grist_client.list_cols(settings.table_name.replace(" ", "_"))

    if status_code >= 300:
        return return_data

    status_code, records = grist_client.list_records(settings.table_name.replace(" ", "_"), filter_option={})

    if status_code >= 300:
        return return_data

    id_field_mapping = {grab(x, "fields.label"): x.get("id") for x in table_data}

    for record in records:
        item = {}
        for column_label in settings.public_list_columns:
            if id_field_mapping.get(column_label) is None:
                continue
            item[column_label] = record.get(id_field_mapping.get(column_label))
        return_data.append(item)

    return return_data
