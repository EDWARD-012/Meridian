import { Link, NavLink } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { useCart } from '../context/CartContext'
import { useEffect } from 'react'

export default function Navbar() {
  const { user, logout, isAuth } = useAuth()
  const { cart, refreshCart } = useCart()

  useEffect(() => { if (isAuth) refreshCart() }, [isAuth, refreshCart])

  return (
    <nav className="navbar">
      <div className="container navbar-inner">
        <Link to="/" className="logo">Meridian<span>.</span></Link>
        <ul className="nav-links">
          <li><NavLink to="/" end>Shop</NavLink></li>
          {isAuth && <li><NavLink to="/orders">Orders</NavLink></li>}
        </ul>
        <div className="nav-actions">
          {isAuth ? (
            <>
              <Link to="/cart" className="btn btn-ghost cart-badge">
                Cart
                {cart.total_items > 0 && <span className="count">{cart.total_items}</span>}
              </Link>
              <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>{user?.username}</span>
              <button className="btn btn-outline" onClick={logout}>Logout</button>
            </>
          ) : (
            <>
              <Link to="/login" className="btn btn-ghost">Login</Link>
              <Link to="/register" className="btn btn-primary">Sign up</Link>
            </>
          )}
        </div>
      </div>
    </nav>
  )
}
