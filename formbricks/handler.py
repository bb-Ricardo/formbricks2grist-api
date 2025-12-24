from app.lib import strip_tags, grab
from app.models import InternalWebhookContent, InternalWebhookField
from formbricks.client import FormbricksClient
from formbricks.models import FormbricksWebhook


def normalize_webhook_content(content: FormbricksWebhook, client: FormbricksClient) -> InternalWebhookContent:

    # need to stay in this order to parse answer correctly
    contact_info_items = ["firstName", "lastName", "email", "phone", "company"]

    return_item = InternalWebhookContent(
        survey_id=content.data.surveyId,
        webhook_id=content.data.id)

    # look up survey
    survey_data = client.get_survey(content.data.surveyId)

    if survey_data is None or survey_data.get("data") is None:
        raise RuntimeError(f"unable to get survey with ID: {content.data.surveyId}")

    return_item.survey_name = grab(survey_data, "data.name", fallback="Registrations")

    # iterate over questions
    for survey_question in grab(survey_data, "data.questions") or list():

        question_id = survey_question.get("id")
        question_title = strip_tags(grab(survey_question, "headline.default", fallback=""))
        question_type = survey_question.get("type")
        question_column_type = "Text"

        question_answer = content.data.data.get(question_id)

        if question_answer is None:
            continue

        if question_type == "contactInfo":

            for key, part in enumerate(contact_info_items):
                return_item.data.append(
                    InternalWebhookField(
                        id=f"{question_id}_{part}",
                        label=f'{question_title} - {grab(survey_question, f"{part}.placeholder.default")}',
                        type=question_column_type,
                        value=question_answer[key]
                    )
                )
        else:

            if question_type == "date":
                question_column_type = "Date"
            elif question_type == "multipleChoiceMulti":
                question_answer = ", ".join(question_answer)

            return_item.data.append(
                InternalWebhookField(
                    id=question_id,
                    label=question_title,
                    type=question_column_type,
                    value=question_answer
                )
            )

    return return_item
