import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import App from './App.tsx'

describe('App', () => {
  it('pinta el nombre ACOMPAS', () => {
    render(<App />)

    expect(screen.getByRole('heading', { name: 'ACOMPAS' })).toBeDefined()
  })
})
