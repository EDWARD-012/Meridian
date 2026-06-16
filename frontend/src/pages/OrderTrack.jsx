import { useEffect, useState } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import api, { formatPrice, formatDate } from '../api/client'
import { useAuth } from '../context/AuthContext'

const STATUS_ORDER = ['pending', 'confirmed', 'processing', 'shipped', 'out_for_delivery', 'delivered']

export default function OrderTrack() {
  const { id } = useParams()
  const [order, setOrder] = useState(null)
  const { isAuth } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    if (!isAuth) { navigate('/login'); return }
    api.get(`/orders/${id}/track/`).then(({ data }) => setOrder(data)).catch(() => navigate('/orders'))
  }, [id, isAuth, navigate])

  if (!order) return <div className="container"><p>Loading...</p></div>

  const currentIdx = STATUS_ORDER.indexOf(order.status)

  return (
    <div className="container" style={{ maxWidth: '720px' }}>
      <Link to="/orders" style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>← Back to orders</Link>
      <h2 style={{ fontFamily: 'var(--font-display)', margin: '1rem 0 0.5rem' }}>Track Order #{order.id}</h2>
      <span className={`status-pill ${order.status}`}>{order.status.replace(/_/g, ' ')}</span>

      <div className="summary-card" style={{ marginTop: '1.5rem', position: 'static' }}>
        <div className="summary-row"><span>Total</span><span>{formatPrice(order.total_amount)}</span></div>
        <div className="summary-row"><span>Payment</span><span style={{ textTransform: 'capitalize' }}>{order.payment?.status}</span></div>
        <div className="summary-row"><span>Method</span><span style={{ textTransform: 'uppercase' }}>{order.payment?.payment_method}</span></div>
        {order.payment?.transaction_id && (
          <div className="summary-row"><span>Txn ID</span><span>{order.payment.transaction_id}</span></div>
        )}
      </div>

      <h3 style={{ marginTop: '2rem', fontFamily: 'var(--font-display)' }}>Tracking Timeline</h3>
      <div className="tracking-timeline">
        {order.tracking_events?.map((ev, i) => {
          const evIdx = STATUS_ORDER.indexOf(ev.status)
          const cls = evIdx < currentIdx ? 'done' : evIdx === currentIdx ? 'active' : ''
          return (
            <div key={ev.id || i} className={`track-event ${cls}`}>
              <div className="status">{ev.status.replace(/_/g, ' ')}</div>
              <div className="msg">{ev.message}{ev.location ? ` · ${ev.location}` : ''}</div>
              <div className="time">{formatDate(ev.recorded_at)}</div>
            </div>
          )
        })}
      </div>

      <h3 style={{ marginTop: '2rem', fontFamily: 'var(--font-display)' }}>Items</h3>
      {order.items?.map((item) => (
        <div key={item.id} className="cart-item">
          <img src={item.product.image_url} alt={item.product.name} />
          <div>
            <h3>{item.product.name}</h3>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Qty: {item.quantity}</p>
          </div>
          <strong>{formatPrice(item.subtotal)}</strong>
        </div>
      ))}
    </div>
  )
}
