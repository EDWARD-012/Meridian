import { useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useCart } from '../context/CartContext'
import { useAuth } from '../context/AuthContext'
import { formatPrice } from '../api/client'

export default function CartPage() {
  const { cart, refreshCart, updateQty, removeItem } = useCart()
  const { isAuth } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    if (!isAuth) { navigate('/login'); return }
    refreshCart()
  }, [isAuth, refreshCart, navigate])

  if (!cart.items?.length) {
    return (
      <div className="container empty-state">
        <h3>Your cart is empty</h3>
        <p>Add something from the shop first.</p>
        <Link to="/" className="btn btn-primary" style={{ marginTop: '1rem' }}>Continue shopping</Link>
      </div>
    )
  }

  return (
    <div className="container">
      <h2 style={{ fontFamily: 'var(--font-display)', marginBottom: '1.5rem' }}>Your Cart</h2>
      <div className="cart-layout">
        <div>
          {cart.items.map((item) => (
            <div key={item.id} className="cart-item">
              <img src={item.product.image_url} alt={item.product.name} />
              <div>
                <h3>{item.product.name}</h3>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>{formatPrice(item.product.price)} each</p>
                <div className="qty-control">
                  <button onClick={() => updateQty(item.id, item.quantity - 1)} disabled={item.quantity <= 1}>−</button>
                  <span>{item.quantity}</span>
                  <button onClick={() => updateQty(item.id, item.quantity + 1)} disabled={item.quantity >= item.product.stock_quantity}>+</button>
                  <button className="btn btn-ghost" style={{ marginLeft: '0.5rem' }} onClick={() => removeItem(item.id)}>Remove</button>
                </div>
              </div>
              <strong>{formatPrice(item.line_total)}</strong>
            </div>
          ))}
        </div>
        <div className="summary-card">
          <h3 style={{ marginBottom: '1rem' }}>Summary</h3>
          <div className="summary-row"><span>Items</span><span>{cart.total_items}</span></div>
          <div className="summary-row total"><span>Subtotal</span><span>{formatPrice(cart.subtotal)}</span></div>
          <button className="btn btn-primary" style={{ width: '100%', marginTop: '1rem' }} onClick={() => navigate('/checkout')}>
            Proceed to checkout
          </button>
        </div>
      </div>
    </div>
  )
}
