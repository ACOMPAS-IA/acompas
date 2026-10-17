import pytest
from pydantic import ValidationError

from app.services.llm_gateway import LLMMessage, LLMRequest, LLMResponse


def user(content="Pregunta inventada"):
    return LLMMessage(role="user", content=content)


def assistant(content="Respuesta inventada"):
    return LLMMessage(role="assistant", content=content)


def test_valid_request():
    request = LLMRequest(
        system="Prompt inventado",
        messages=[user(), assistant(), user("Otra pregunta")],
    )

    assert [message.role for message in request.messages] == ["user", "assistant", "user"]
    assert request.max_output_tokens is None


def test_request_accepts_max_output_tokens():
    request = LLMRequest(system="Prompt", messages=[user()], max_output_tokens=10)

    assert request.max_output_tokens == 10


@pytest.mark.parametrize(
    "build",
    [
        pytest.param(lambda: LLMRequest(system="Prompt", messages=[]), id="sin-mensajes"),
        pytest.param(lambda: LLMRequest(system="", messages=[user()]), id="system-vacio"),
        pytest.param(lambda: LLMRequest(system="  \n", messages=[user()]), id="system-espacios"),
        pytest.param(lambda: LLMRequest(system="Prompt", messages=[user("")]), id="mensaje-vacio"),
        pytest.param(
            lambda: LLMRequest(system="Prompt", messages=[user(" \t ")]), id="mensaje-espacios"
        ),
        pytest.param(
            lambda: LLMRequest(system="Prompt", messages=[assistant(), user()]),
            id="primero-assistant",
        ),
        pytest.param(
            lambda: LLMRequest(system="Prompt", messages=[user(), assistant()]),
            id="ultimo-assistant",
        ),
        pytest.param(
            lambda: LLMRequest(system="Prompt", messages=[user()], max_output_tokens=0),
            id="max-tokens-cero",
        ),
        pytest.param(
            lambda: LLMRequest(system="Prompt", messages=[user()], max_output_tokens=-1),
            id="max-tokens-negativo",
        ),
        pytest.param(
            lambda: LLMRequest(
                system="Prompt", messages=[LLMMessage(role="system", content="Texto")]
            ),
            id="rol-no-valido",
        ),
        pytest.param(
            lambda: LLMRequest(system="Prompt", messages=[user()], patient_id="x"),
            id="campo-extra",
        ),
    ],
)
def test_invalid_request_is_rejected(build):
    with pytest.raises(ValidationError):
        build()


@pytest.mark.parametrize(
    "instance, field, value",
    [
        (user(), "content", "Otro"),
        (LLMRequest(system="Prompt", messages=[user()]), "system", "Otro"),
        (
            LLMResponse(
                text="Texto", model="modelo", input_tokens=1, output_tokens=1, stop_reason=None
            ),
            "text",
            "Otro",
        ),
    ],
)
def test_models_are_immutable(instance, field, value):
    with pytest.raises(ValidationError):
        setattr(instance, field, value)


def test_response_fields():
    response = LLMResponse(
        text="Texto", model="modelo", input_tokens=3, output_tokens=5, stop_reason="end_turn"
    )

    assert response.model_dump() == {
        "text": "Texto",
        "model": "modelo",
        "input_tokens": 3,
        "output_tokens": 5,
        "stop_reason": "end_turn",
    }
