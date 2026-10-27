import pytest

from app.services.conversation import ConversationRequest, ConversationResponse, ConversationService
from app.services.llm_gateway import LLMErrorCode, LLMGateway, LLMGatewayError
from app.services.prompts import DOCUMENT_OPEN_TAG, load_system_prompt

from .conftest import ANSWER, DOCUMENT_TEXT, QUESTION, FakeProvider


def make_request(document=DOCUMENT_TEXT, question=QUESTION):
    return ConversationRequest.model_validate(
        {"documents": [{"text": document}], "messages": [{"role": "user", "content": question}]}
    )


def test_answer_returns_text_and_not_truncated(llm_env):
    response = ConversationService(LLMGateway(FakeProvider())).answer(make_request())

    assert response == ConversationResponse(answer=ANSWER, truncated=False)


def test_max_tokens_marks_answer_as_truncated(llm_env):
    provider = FakeProvider(stop_reason="max_tokens")

    response = ConversationService(LLMGateway(provider)).answer(make_request())

    assert response == ConversationResponse(answer=ANSWER, truncated=True)


@pytest.mark.parametrize(
    "text, stop_reason, expected_answer, expected_truncated",
    [
        pytest.param("r" * 8_001, "end_turn", "r" * 8_000, True, id="over-limit-is-cut"),
        pytest.param("r" * 8_000, "end_turn", "r" * 8_000, False, id="at-limit-unchanged"),
        pytest.param(ANSWER, "end_turn", ANSWER, False, id="normal"),
        pytest.param("r" * 100, "max_tokens", "r" * 100, True, id="max-tokens"),
    ],
)
def test_answer_is_capped_at_max_answer_chars(llm_env, text, stop_reason, expected_answer, expected_truncated):
    provider = FakeProvider(text=text, stop_reason=stop_reason)

    response = ConversationService(LLMGateway(provider)).answer(make_request())

    assert response == ConversationResponse(answer=expected_answer, truncated=expected_truncated)


def test_gateway_receives_system_prompt_and_documents(llm_env):
    provider = FakeProvider()

    ConversationService(LLMGateway(provider)).answer(make_request())

    [llm_request] = provider.calls
    assert llm_request.system == load_system_prompt().text
    assert llm_request.messages[0].content.startswith(f"{DOCUMENT_OPEN_TAG}\n{DOCUMENT_TEXT}\n")
    assert llm_request.max_output_tokens is None


@pytest.mark.parametrize("code", list(LLMErrorCode))
def test_gateway_errors_propagate_unchanged(llm_env, code):
    error = LLMGatewayError(code, status_code=500, request_id="req-test-1")

    with pytest.raises(LLMGatewayError) as excinfo:
        ConversationService(LLMGateway(FakeProvider(error=error))).answer(make_request())

    assert excinfo.value is error


def test_not_configured_gateway_propagates(no_llm_env):
    provider = FakeProvider()

    with pytest.raises(LLMGatewayError) as excinfo:
        ConversationService(LLMGateway(provider)).answer(make_request())

    assert excinfo.value.code == LLMErrorCode.NOT_CONFIGURED
    assert provider.calls == []


@pytest.mark.parametrize("text", ["", "  \n "])
def test_empty_answer_is_a_provider_error(llm_env, text):
    with pytest.raises(LLMGatewayError) as excinfo:
        ConversationService(LLMGateway(FakeProvider(text=text))).answer(make_request())

    assert excinfo.value.code == LLMErrorCode.PROVIDER_ERROR


def test_no_state_is_kept_between_requests(llm_env):
    provider = FakeProvider()
    service = ConversationService(LLMGateway(provider))

    service.answer(make_request("Primer informe inventado de [PACIENTE].", "Primera pregunta"))
    service.answer(make_request("Segundo informe inventado.", "Segunda pregunta"))

    _, second = provider.calls
    assert len(second.messages) == 1
    assert "Primer informe" not in second.messages[0].content
    assert "Primera pregunta" not in second.messages[0].content
    assert set(vars(service)) == {"_gateway"}
