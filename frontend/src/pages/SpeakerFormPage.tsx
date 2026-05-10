import { useEffect, useState, type FormEvent } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { speakersApi } from '../api/speakers'
import { Button } from '../components/Button'
import { Input } from '../components/Input'
import { TextArea } from '../components/TextArea'
import { Spinner } from '../components/Spinner'
import { describeError } from '../lib/errors'

export function SpeakerFormPage() {
  const { id } = useParams<{ id: string }>()
  const isEdit = !!id
  const speakerId = id ? Number(id) : null
  const navigate = useNavigate()

  const [name, setName] = useState('')
  const [bio, setBio] = useState('')
  const [photoUrl, setPhotoUrl] = useState('')
  const [loading, setLoading] = useState(isEdit)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!isEdit || speakerId === null) return
    speakersApi
      .get(speakerId)
      .then((sp) => {
        setName(sp.name)
        setBio(sp.bio)
        setPhotoUrl(sp.photo_url)
      })
      .catch((err) => setError(describeError(err, 'No pudimos cargar el ponente.')))
      .finally(() => setLoading(false))
  }, [isEdit, speakerId])

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError(null)
    setSubmitting(true)
    try {
      if (isEdit && speakerId !== null) {
        await speakersApi.update(speakerId, { name, bio, photo_url: photoUrl })
      } else {
        await speakersApi.create({ name, bio, photo_url: photoUrl })
      }
      navigate('/speakers')
    } catch (err) {
      setError(describeError(err, 'No pudimos guardar el ponente.'))
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) return <Spinner />

  return (
    <div className="max-w-2xl mx-auto px-4 py-6">
      <h1 className="text-2xl font-bold text-slate-900 mb-5">
        {isEdit ? 'Editar ponente' : 'Nuevo ponente'}
      </h1>
      <form onSubmit={onSubmit} className="bg-white border border-slate-200 rounded-lg p-6 shadow-sm flex flex-col gap-4">
        <Input
          label="Nombre"
          value={name}
          onChange={(e) => setName(e.target.value)}
          required
          minLength={1}
          maxLength={255}
        />
        <TextArea
          label="Biografía"
          value={bio}
          onChange={(e) => setBio(e.target.value)}
          maxLength={4000}
        />
        <Input
          label="URL de la foto (opcional)"
          type="url"
          value={photoUrl}
          onChange={(e) => setPhotoUrl(e.target.value)}
          maxLength={500}
          placeholder="https://…"
        />
        {error && <p className="text-sm text-red-600">{error}</p>}
        <div className="flex gap-2">
          <Button type="submit" disabled={submitting}>
            {submitting ? 'Guardando…' : isEdit ? 'Guardar cambios' : 'Crear ponente'}
          </Button>
          <Button type="button" variant="ghost" onClick={() => navigate(-1)}>
            Cancelar
          </Button>
        </div>
      </form>
    </div>
  )
}
