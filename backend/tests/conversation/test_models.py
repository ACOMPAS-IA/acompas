import pytest
from pydantic import ValidationError

from app.services.conversation import (
    ChatMessage,
    ConversationRequest,
    ConversationResponse,
    DocumentInput,
)
from app.services.conversation.models import (
    MAX_ANSWER_CHARS,
    MAX_DOCUMENT_CHARS,
    MAX_DOCUMENTS,
    MAX_MESSAGES,
    MAX_QUESTION_CHARS,
)

from .conftest import DOCUMENT_TEXT, QUESTION


def user(content=QUESTION):
    return {"role": "user", "content": content}


def assistant(content="Respuesta previa inventada."):
    return {"role": "assistant", "content": content}


def payload(documents=None, messages=None):
    return {
        "documents": documents if documents is not None else [{"text": DOCUMENT_TEXT}],
        "messages": messages if messages is not None else [user()],
    }


def alternating(count):
    return [user() if index % 2 == 0 else assistant() for index in range(count)]


def test_limits_match_the_specification():
    assert (MAX_DOCUMENTS, MAX_DOCUMENT_CHARS, MAX_MESSAGES) == (3, 30_000, 21)
    assert (MAX_QUESTION_CHARS, MAX_ANSWER_CHARS) == (2_000, 8_000)


def test_minimal_request_is_valid():
    request = ConversationRequest.model_validate(payload())

    assert request.documents == [DocumentInput(text=DOCUMENT_TEXT)]
    assert request.messages == [ChatMessage(role="user", content=QUESTION)]


def test_request_at_every_limit_is_valid():
    messages = alternating(MAX_MESSAGES)
    messages[0] = user("p" * MAX_QUESTION_CHARS)
    messages[1] = assistant("r" * MAX_ANSWER_CHARS)

    request = ConversationRequest.model_validate(
        payload(
            documents=[{"text": "d" * MAX_DOCUMENT_CHARS}] * MAX_DOCUMENTS,
            messages=messages,
        )
    )

    assert len(request.documents) == MAX_DOCUMENTS
    assert len(request.messages) == MAX_MESSAGES


@pytest.mark.parametrize(
    "data",
    [
        pytest.param(payload(documents=[]), id="no-documents"),
        pytest.param(payload(documents=[{"text": "d"}] * (MAX_DOCUMENTS + 1)), id="too-many-documents"),
        pytest.param(payload(documents=[{"text": ""}]), id="empty-document"),
        pytest.param(payload(documents=[{"text": " \n\t "}]), id="blank-document"),
        pytest.param(payload(documents=[{"text": "d" * (MAX_DOCUMENT_CHARS + 1)}]), id="long-document"),
        pytest.param(payload(messages=[]), id="no-messages"),
        pytest.param(payload(messages=alternating(MAX_MESSAGES + 2)), id="too-many-messages"),
        pytest.param(payload(messages=[user("")]), id="empty-question"),
        pytest.param(payload(messages=[user("   ")]), id="blank-question"),
        pytest.param(payload(messages=[user("p" * (MAX_QUESTION_CHARS + 1))]), id="long-question"),
        pytest.param(
            payload(messages=[user(), assistant("r" * (MAX_ANSWER_CHARS + 1)), user()]),
            id="long-answer",
        ),
        pytest.param(payload(messages=[user(), assistant(" "), user()]), id="blank-answer"),
        pytest.param(payload(messages=[user(), user()]), id="not-alternating"),
        pytest.param(payload(messages=[user(), assistant(), assistant(), user()]), id="two-assistants"),
        pytest.param(payload(messages=[assistant(), user()]), id="starts-with-assistant"),
        pytest.param(payload(messages=[user(), assistant()]), id="ends-with-assistant"),
        pytest.param(payload(messages=[{"role": "system", "content": QUESTION}]), id="invalid-role"),
        pytest.param({**payload(), "model": "otro"}, id="unknown-root-field"),
        pytest.param(payload(documents=[{"text": DOCUMENT_TEXT, "name": "x"}]), id="unknown-document-field"),
        pytest.param(payload(messages=[{**user(), "id": 1}]), id="unknown-message-field"),
    ],
)
def test_invalid_requests_are_rejected(data):
    with pytest.raises(ValidationError):
        ConversationRequest.model_validate(data)


def test_models_are_immutable():
    request = ConversationRequest.model_validate(payload())
    response = ConversationResponse(answer="Respuesta.", truncated=False)

    with pytest.raises(ValidationError):
        request.documents = []
    with pytest.raises(ValidationError):
        request.messages[0].content = "otra"
    with pytest.raises(ValidationError):
        response.truncated = True
