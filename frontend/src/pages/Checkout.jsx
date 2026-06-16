import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api, { formatPrice } from '../api/client'
import { useAuth } from '../context/AuthContext'
import { useCart } from '../context/CartContext'

export default function Checkout() {
  const { isAuth } = useAuth()
  const { cart, refreshCart } = useCart()
  const navigate = useNavigate()
  const [addresses, setAddresses] = useState([])
  const [form, setForm] = useState({ full_name: '', line1: '', city: '', state: '', pincode: '', payment_method: 'cod' })
  const [addressId, setAddressId] = useState('')
  const [useNew, setUseNew] = useState(true)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!isAuth) { navigate('/login'); return }
    refreshCart()
    api.get('/orders/addresses/').then(({ data }) => {
      const list = data.results || data
      setAddresses(list)
      if (list.length) { setUseNew(false); setAddressId(String(list[0].id)) }
    })
  }, [isAuth, navigate, refreshCart])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      let addrId = addressId
      if (useNew) {
        const { data } = await api.post('/orders/addresses/', { ...form, is_default: true })
        addrId = data.id
      }
      const { data: order } = await api.post('/orders/place/', {
        address_id: Number(addrId),
        payment_method: form.payment_method,
      })
      navigate(`/orders/${order.id}/track`)
    } catch (err) {
      setError(err.response?.data?.detail || 'Checkout failed')
    } finally {
      setLoading(false)
    }
  }

  if (!cart.items?.length) {
    return (
      <div className="container empty-state">
        <h3>Nothing to checkout</h3>
        <button className="btn btn-primary" onClick={() => navigate('/')}>Go to shop</button>
      </div>
    )
  }

  return (
    <div className="container" style={{ maxWidth: '640px' }}>
      <h2 style={{ fontFamily: 'var(--font-display)', marginBottom: '1.5rem' }}>Checkout</h2>
      {error && <div className="form-error">{error}</div>}
      <form onSubmit={handleSubmit} className="form-card" style={{ maxWidth: '100%' }}>
        {addresses.length > 0 && (
          <div className="form-group">
            <label>
              <input type="radio" checked={!useNew} onChange={() => setUseNew(false)} /> Saved address
            </label>
            {!useNew && (
              <select value={addressId} onChange={(e) => setAddressId(e.target.value)} style={{ marginTop: '0.5rem' }}>
                {addresses.map((a) => (
                  <option key={a.id} value={a.id}>{a.full_name}, {a.line1}, {a.city}</option>
                ))}
              </select>
            )}
            <label style={{ marginTop: '0.75rem', display: 'block' }}>
              <input type="radio" checked={useNew} onChange={() => setUseNew(true)} /> New address
            </label>
          </div>
        )}
        {useNew && (
          <>
            {['full_name', 'line1', 'city', 'state', 'pincode'].map((f) => (
              <div key={f} className="form-group">
                <label>{f.replace('_', ' ')}</label>
                <input required value={form[f]} onChange={(e) => setForm({ ...form, [f]: e.target.value })} />
              </div>
            ))}
          </>
        )}
        <div className="form-group">
          <label>Payment method</label>
          <select value={form.payment_method} onChange={(e) => setForm({ ...form, payment_method: e.target.value })}>
            <option value="cod">Cash on Delivery</option>
            <option value="upi">UPI (simulated success)</option>
            <option value="card">Card (simulated success)</option>
          </select>
        </div>
        <div className="summary-row total" style={{ border: 'none', paddingTop: 0 }}>
          <span>Total</span><span>{formatPrice(cart.subtotal)}</span>
        </div>
        <button className="btn btn-primary" style={{ width: '100%', marginTop: '1rem' }} disabled={loading}>
          {loading ? 'Placing order...' : 'Place order'}
        </button>
      </form>
    </div>
  )
}
