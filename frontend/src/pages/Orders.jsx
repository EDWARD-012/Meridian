import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import api, { formatPrice, formatDate } from '../api/client'
import { useAuth } from '../context/AuthContext'

export default function Orders() {
  const [orders, setOrders] = useState([])
  const { isAuth } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    if (!isAuth) { navigate('/login'); return }
    api.get('/orders/').then(({ data }) => setOrders(data.results || data))
  }, [isAuth, navigate])

  if (!orders.length) {
    return (
      <div className="container empty-state">
        <h3>No orders yet</h3>
        <Link to="/" className="btn btn-primary" style={{ marginTop: '1rem' }}>Start shopping</Link>
      </div>
    )
  }

  return (
    <div className="container" style={{ maxWidth: '720px' }}>
      <h2 style={{ fontFamily: 'var(--font-display)', marginBottom: '1.5rem' }}>Your Orders</h2>
      {orders.map((o) => (
        <Link key={o.id} to={`/orders/${o.id}/track`} className="order-card">
          <div>
            <strong>Order #{o.id}</strong>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>{formatDate(o.order_date)} · {o.item_count} items</p>
          </div>
          <div style={{ textAlign: 'right' }}>
            <span className={`status-pill ${o.status}`}>{o.status.replace(/_/g, ' ')}</span>
            <p style={{ marginTop: '0.35rem', fontWeight: 600 }}>{formatPrice(o.total_amount)}</p>
          </div>
        </Link>
      ))}
    </div>
  )
}
