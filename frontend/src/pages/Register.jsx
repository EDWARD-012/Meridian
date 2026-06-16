import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Register() {
  const [form, setForm] = useState({ username: '', email: '', password: '', phone: '' })
  const [error, setError] = useState('')
  const { register } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    try {
      await register(form)
      navigate('/')
    } catch (err) {
      const data = err.response?.data
      setError(data?.username?.[0] || data?.detail || 'Registration failed')
    }
  }

  return (
    <div className="container">
      <form className="form-card" onSubmit={handleSubmit}>
        <h2>Create account</h2>
        {error && <div className="form-error">{error}</div>}
        {['username', 'email', 'password', 'phone'].map((f) => (
          <div key={f} className="form-group">
            <label>{f.charAt(0).toUpperCase() + f.slice(1)}</label>
            <input
              type={f === 'password' ? 'password' : 'text'}
              value={form[f]}
              onChange={(e) => setForm({ ...form, [f]: e.target.value })}
              required={f !== 'phone'}
            />
          </div>
        ))}
        <button className="btn btn-primary" style={{ width: '100%' }}>Sign up</button>
        <p className="form-footer">Already have an account? <Link to="/login">Login</Link></p>
      </form>
    </div>
  )
}
