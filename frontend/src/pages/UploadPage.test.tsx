import { act, cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import {
  AnonymizationError,
  type AnonymizationResult,
  type AnonymizeText,
} from '../api/anonymization.ts'
import { SessionExpiredError } from '../api/client.ts'
import { UploadPage } from './UploadPage.tsx'

// Textos breves e inventados, con etiquetas de anonimización (ACO-032, sección 9).
const TEXT = 'Informe inventado de [PACIENTE]. Firma [SANITARIO_1].'
const VALID: AnonymizationResult = {
  status: 'validado',
  confidence: 0.93,
  anonymized_text: TEXT,
  entities_count: { PERSON: 1 },
  reason: null,
}
const ILLEGIBLE: AnonymizationResult = {
  status: 'ilegible',
  confidence: null,
  anonymized_text: null,
  entities_count: {},
  reason: 'texto_vacio',
}

afterEach(cleanup)

function uploadButton() {
  return screen.getByRole('button', { name: 'Subir y anonimizar' })
}

function selectFile(file: File) {
  fireEvent.change(screen.getByLabelText('Documento (.txt)'), {
    target: { files: [file] },
  })
}

async function submit() {
  await act(async () => {
    fireEvent.click(uploadButton())
  })
}

function txt(contents: string | ArrayBuffer, name = 'documento-sintetico.txt') {
  return new File([contents], name, { type: 'text/plain' })
}

describe('UploadPage', () => {
  it('muestra el selector y el botón deshabilitado sin fichero, sin cabecera ni pie', () => {
    const { container } = render(
      <UploadPage onResult={vi.fn()} anonymize={vi.fn()} />,
    )

    expect(screen.getByRole('heading', { name: 'Subir documento' })).toBeDefined()
    const input = screen.getByLabelText('Documento (.txt)') as HTMLInputElement
    expect(input.type).toBe('file')
    expect(input.accept).toContain('.txt')
    expect(uploadButton().hasAttribute('disabled')).toBe(true)
    expect(container.querySelector('main, header, nav, footer')).toBeNull()
  })

  it('rechaza un fichero que no es .txt sin llamar a la anonimización', async () => {
    const anonymize = vi.fn<AnonymizeText>()
    render(<UploadPage onResult={vi.fn()} anonymize={anonymize} />)

    selectFile(new File(['contenido'], 'documento.pdf', { type: 'application/pdf' }))
    await submit()

    expect((await screen.findByRole('alert')).textContent).toBe(
      'Solo se admiten documentos .txt en UTF-8.',
    )
    expect(anonymize).not.toHaveBeenCalled()
  })

  it('rechaza un fichero de más de 128 KiB sin leerlo ni llamar al API', async () => {
    const anonymize = vi.fn<AnonymizeText>()
    render(<UploadPage onResult={vi.fn()} anonymize={anonymize} />)

    selectFile(txt(new Uint8Array(128 * 1024 + 1).buffer, 'grande.txt'))
    await submit()

    expect((await screen.findByRole('alert')).textContent).toBe(
      'El documento supera el máximo de 30 000 caracteres.',
    )
    expect(anonymize).not.toHaveBeenCalled()
  })

  it('rechaza un texto de más de 30 000 caracteres y acepta exactamente 30 000', async () => {
    const anonymize = vi.fn<AnonymizeText>(async () => VALID)
    const onResult = vi.fn()
    render(<UploadPage onResult={onResult} anonymize={anonymize} />)

    selectFile(txt('a'.repeat(30_001), 'largo.txt'))
    await submit()

    expect((await screen.findByRole('alert')).textContent).toBe(
      'El documento supera el máximo de 30 000 caracteres.',
    )
    expect(anonymize).not.toHaveBeenCalled()

    cleanup()
    render(<UploadPage onResult={onResult} anonymize={anonymize} />)
    selectFile(txt('a'.repeat(30_000), 'justo.txt'))
    await submit()

    await waitFor(() =>
      expect(anonymize).toHaveBeenCalledWith('a'.repeat(30_000)),
    )
    expect(onResult).toHaveBeenCalledWith(VALID)
  })

  it('rechaza un fichero que no es UTF-8 válido sin llamar al API', async () => {
    const anonymize = vi.fn<AnonymizeText>()
    render(<UploadPage onResult={vi.fn()} anonymize={anonymize} />)

    selectFile(txt(new Uint8Array([0xff, 0xfe]).buffer, 'invalido.txt'))
    await submit()

    expect((await screen.findByRole('alert')).textContent).toBe(
      'El fichero no está codificado en UTF-8.',
    )
    expect(anonymize).not.toHaveBeenCalled()
  })

  it('lee un .txt válido, llama a la anonimización y entrega el resultado', async () => {
    const anonymize = vi.fn<AnonymizeText>(async () => VALID)
    const onResult = vi.fn()
    render(<UploadPage onResult={onResult} anonymize={anonymize} />)

    selectFile(txt(TEXT))
    await submit()

    await waitFor(() => expect(anonymize).toHaveBeenCalledWith(TEXT))
    expect(onResult).toHaveBeenCalledWith(VALID)
  })

  it('envía un fichero vacío para que el servidor devuelva ilegible', async () => {
    const anonymize = vi.fn<AnonymizeText>(async () => ILLEGIBLE)
    const onResult = vi.fn()
    render(<UploadPage onResult={onResult} anonymize={anonymize} />)

    selectFile(txt('', 'vacio.txt'))
    await submit()

    await waitFor(() => expect(anonymize).toHaveBeenCalledWith(''))
    expect(onResult).toHaveBeenCalledWith(ILLEGIBLE)
  })

  const ERRORS: Array<[string, string]> = [
    [
      'invalid_request',
      'No se ha podido procesar la petición. Inténtalo de nuevo.',
    ],
    ['text_too_long', 'El documento supera el máximo de 30 000 caracteres.'],
    [
      'anonymization_not_configured',
      'El servicio de anonimización no está disponible. Avisa al equipo.',
    ],
    ['forbidden', 'No tienes permiso para subir documentos.'],
    [
      'auth_unavailable',
      'El servicio de autenticación no está disponible. Inténtalo de nuevo.',
    ],
    [
      'request_failed',
      'No se ha podido anonimizar el documento. Inténtalo de nuevo.',
    ],
  ]

  it.each(ERRORS)('muestra el mensaje de %s', async (detail, message) => {
    const anonymize = vi.fn<AnonymizeText>(async () => {
      throw new AnonymizationError(detail)
    })
    render(<UploadPage onResult={vi.fn()} anonymize={anonymize} />)

    selectFile(txt(TEXT))
    await submit()

    expect((await screen.findByRole('alert')).textContent).toBe(message)
  })

  it('reintenta con el mismo fichero y muestra el estado de espera', async () => {
    let resolve!: (value: AnonymizationResult) => void
    const anonymize = vi
      .fn<AnonymizeText>()
      .mockRejectedValueOnce(new AnonymizationError('request_failed'))
      .mockImplementationOnce(
        () => new Promise<AnonymizationResult>((done) => (resolve = done)),
      )
    const onResult = vi.fn()
    render(<UploadPage onResult={onResult} anonymize={anonymize} />)

    selectFile(txt(TEXT))
    await submit()
    await screen.findByRole('alert')

    const retry = screen.getByRole('button', { name: 'Reintentar' })
    expect(retry.hasAttribute('disabled')).toBe(false)

    await act(async () => {
      fireEvent.click(retry)
    })

    expect(screen.getByRole('status').textContent).toContain(
      'Subiendo y anonimizando',
    )
    expect(
      screen.getByRole('button', { name: 'Procesando…' }).hasAttribute('disabled'),
    ).toBe(true)

    await act(async () => {
      resolve(VALID)
    })

    expect(anonymize).toHaveBeenCalledTimes(2)
    expect(anonymize.mock.calls[0][0]).toBe(TEXT)
    expect(anonymize.mock.calls[1][0]).toBe(TEXT)
    expect(onResult).toHaveBeenCalledWith(VALID)
  })

  it('no muestra un error local si la sesión ha caducado', async () => {
    const anonymize = vi.fn<AnonymizeText>(async () => {
      throw new SessionExpiredError()
    })
    const onResult = vi.fn()
    render(<UploadPage onResult={onResult} anonymize={anonymize} />)

    selectFile(txt(TEXT))
    await submit()

    await waitFor(() =>
      expect(
        screen
          .getByRole('button', { name: 'Subir y anonimizar' })
          .hasAttribute('disabled'),
      ).toBe(false),
    )
    expect(screen.queryByRole('alert')).toBeNull()
    expect(onResult).not.toHaveBeenCalled()
  })

  it('no expone el nombre del fichero ni el texto original', async () => {
    const anonymize = vi.fn<AnonymizeText>(async () => VALID)
    render(<UploadPage onResult={vi.fn()} anonymize={anonymize} />)

    selectFile(txt(TEXT, 'documento-sintetico.txt'))
    expect(screen.queryByText('documento-sintetico.txt')).toBeNull()

    await submit()

    await waitFor(() => expect(anonymize).toHaveBeenCalled())
    expect(screen.queryByText('documento-sintetico.txt')).toBeNull()
    expect(screen.queryByText(TEXT)).toBeNull()
  })
})
