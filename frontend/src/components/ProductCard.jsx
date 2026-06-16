import { Link } from 'react-router-dom'
import { formatPrice } from '../api/client'

export default function ProductCard({ product, onAdd }) {
  const lowStock = product.stock_quantity <= 5

  return (
    <article className="product-card">
      <Link to={`/product/${product.slug}`}>
        <div className="img-wrap">
          <img src={product.image_url || 'https://via.placeholder.com/400'} alt={product.name} loading="lazy" />
        </div>
      </Link>
      <div className="info">
        <div className="cat">{product.category_name}</div>
        <Link to={`/product/${product.slug}`}><h3>{product.name}</h3></Link>
        <div className="meta">
          <span className="price">{formatPrice(product.price)}</span>
          <span className={lowStock ? 'stock-low' : 'stock-ok'}>
            {product.stock_quantity > 0 ? `${product.stock_quantity} left` : 'Out of stock'}
          </span>
        </div>
        <button
          className="btn btn-primary"
          style={{ width: '100%', marginTop: '0.75rem' }}
          disabled={product.stock_quantity === 0}
          onClick={() => onAdd?.(product)}
        >
          Add to cart
        </button>
      </div>
    </article>
  )
}
