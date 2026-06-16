import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import api, { formatPrice } from '../api/client'
import { useAuth } from '../context/AuthContext'
import { useCart } from '../context/CartContext'

export default function ProductDetail() {
  const { slug } = useParams()
  const [product, setProduct] = useState(null)
  const [qty, setQty] = useState(1)
  const { isAuth } = useAuth()
  const { addToCart } = useCart()
  const navigate = useNavigate()

  useEffect(() => {
    api.get(`/catalog/products/${slug}/`).then(({ data }) => setProduct(data))
  }, [slug])

  if (!product) return <div className="container"><p>Loading...</p></div>

  const handleAdd = async () => {
    if (!isAuth) { navigate('/login'); return }
    await addToCart(product.id, qty)
    navigate('/cart')
  }

  return (
    <div className="container" style={{ maxWidth: '800px' }}>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
        <img
          src={product.image_url}
          alt={product.name}
          style={{ borderRadius: 'var(--radius)', border: '1px solid var(--border)' }}
        />
        <div>
          <div className="cat">{product.category_name}</div>
          <h1 style={{ fontFamily: 'var(--font-display)', fontSize: '1.75rem', marginBottom: '0.75rem' }}>{product.name}</h1>
          <p style={{ color: 'var(--text-muted)', marginBottom: '1rem' }}>{product.description}</p>
          <p className="price" style={{ fontSize: '1.5rem', marginBottom: '1rem' }}>{formatPrice(product.price)}</p>
          <div className="qty-control" style={{ marginBottom: '1rem' }}>
            <button onClick={() => setQty(Math.max(1, qty - 1))}>−</button>
            <span>{qty}</span>
            <button onClick={() => setQty(Math.min(product.stock_quantity, qty + 1))}>+</button>
          </div>
          <button className="btn btn-primary" onClick={handleAdd} disabled={!product.stock_quantity}>
            Add to cart
          </button>
        </div>
      </div>
    </div>
  )
}
