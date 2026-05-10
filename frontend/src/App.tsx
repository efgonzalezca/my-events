import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { AuthProvider } from './auth/AuthContext'
import { ProtectedRoute } from './auth/ProtectedRoute'
import { Header } from './components/Header'
import { ToastProvider } from './components/Toast'
import { LoginPage } from './pages/LoginPage'
import { RegisterPage } from './pages/RegisterPage'
import { EventsListPage } from './pages/EventsListPage'
import { EventDetailPage } from './pages/EventDetailPage'
import { EventFormPage } from './pages/EventFormPage'
import { MyEventsPage } from './pages/MyEventsPage'
import { ProfilePage } from './pages/ProfilePage'
import { SpeakersPage } from './pages/SpeakersPage'
import { SpeakerFormPage } from './pages/SpeakerFormPage'
import { AdminUsersPage } from './pages/AdminUsersPage'

export default function App() {
  return (
    <BrowserRouter>
      <ToastProvider>
        <AuthProvider>
          <div className="min-h-screen bg-slate-50">
            <Header />
            <main>
            <Routes>
              <Route path="/" element={<Navigate to="/events" replace />} />
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />

              <Route path="/events" element={<EventsListPage />} />
              <Route path="/events/:id" element={<EventDetailPage />} />
              <Route
                path="/events/new"
                element={
                  <ProtectedRoute roles={['organizer', 'admin']}>
                    <EventFormPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/events/:id/edit"
                element={
                  <ProtectedRoute roles={['organizer', 'admin']}>
                    <EventFormPage />
                  </ProtectedRoute>
                }
              />

              <Route
                path="/me/events"
                element={
                  <ProtectedRoute roles={['organizer', 'admin']}>
                    <MyEventsPage />
                  </ProtectedRoute>
                }
              />

              <Route
                path="/profile"
                element={
                  <ProtectedRoute>
                    <ProfilePage />
                  </ProtectedRoute>
                }
              />

              <Route path="/speakers" element={<SpeakersPage />} />
              <Route
                path="/speakers/new"
                element={
                  <ProtectedRoute roles={['organizer', 'admin']}>
                    <SpeakerFormPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/speakers/:id/edit"
                element={
                  <ProtectedRoute roles={['organizer', 'admin']}>
                    <SpeakerFormPage />
                  </ProtectedRoute>
                }
              />

              <Route
                path="/admin/users"
                element={
                  <ProtectedRoute roles={['admin']}>
                    <AdminUsersPage />
                  </ProtectedRoute>
                }
              />

              <Route path="*" element={<NotFound />} />
            </Routes>
          </main>
          </div>
        </AuthProvider>
      </ToastProvider>
    </BrowserRouter>
  )
}

function NotFound() {
  return (
    <div className="max-w-md mx-auto mt-16 px-4 text-center">
      <h1 className="text-2xl font-bold text-slate-900">Página no encontrada</h1>
      <p className="text-slate-500 text-sm mt-2">
        La ruta que buscas no existe.
      </p>
    </div>
  )
}
