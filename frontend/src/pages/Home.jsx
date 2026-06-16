import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../api/client'
import Hero3D from '../components/Hero3D'
import ProductCard from '../components/ProductCard'
import { useAuth } from '../context/AuthContext'
import { useCart } from '../context/CartContext'
import { useNavigate } from 'react-router-dom'

export default function Home() {
  const [products, setProducts] = useState([])
  const [categories, setCategories] = useState([])
  const [activeCat, setActiveCat] = useState('')
  const [loading, setLoading] = useState(true)
  const [toast, setToast] = useState('')
  const { isAuth } = useAuth()
  const { addToCart } = useCart()
  const navigate = useNavigate()

  useEffect(() => {
    api.get('/catalog/categories/').then(({ data }) => setCategories(data.results || data))
  }, [])

  useEffect(() => {
    setLoading(true)
    const params = activeCat ? { category: activeCat } : {}
    api.get('/catalog/products/', { params })
      .then(({ data }) => setProducts(data.results || data))
      .finally(() => setLoading(false))
  }, [activeCat])

  const handleAdd = async (product) => {
    if (!isAuth) { navigate('/login'); return }
    try {
      await addToCart(product.id)
      setToast(`${product.name} added to cart`)
      setTimeout(() => setToast(''), 2500)
    } catch (e) {
      setToast(e.response?.data?.detail || 'Could not add to cart')
      setTimeout(() => setToast(''), 3000)
    }
  }

  return (
    <div className="container">
      <section className="hero">
        <div className="hero-text">
          <h1>Curated goods,<br />delivered with care.</h1>
          <p>A full-stack e-commerce platform built with Django REST API and MySQL — catalog, cart, orders, and live tracking.</p>
          <Link to="/#products" className="btn btn-primary">Browse collection</Link>
        </div>
        <Hero3D />
      </section>

      <section id="products">
        <div className="section-head">
          <h2>Collection</h2>
        </div>
        <div className="filter-bar">
          <button className={`filter-chip ${!activeCat ? 'active' : ''}`} onClick={() => setActiveCat('')}>All</button>
          {categories.map((c) => (
            <button
              key={c.id}
              className={`filter-chip ${activeCat === c.slug ? 'active' : ''}`}
              onClick={() => setActiveCat(c.slug)}
            >
              {c.name}
            </button>
          ))}
        </div>
        {loading ? (
          <p style={{ color: 'var(--text-muted)' }}>Loading products...</p>
        ) : (
          <div className="product-grid">
            {products.map((p) => <ProductCard key={p.id} product={p} onAdd={handleAdd} />)}
          </div>
        )}
      </section>
      {toast && <div className="toast">{toast}</div>}
    </div>
  )
}
