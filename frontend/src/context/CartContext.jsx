import { createContext, useContext, useState, useCallback, useEffect } from 'react'
import api from '../api/client'
import { useAuth } from './AuthContext'

const CartContext = createContext(null)

export function CartProvider({ children }) {
  const { isAuth } = useAuth()
  const [cart, setCart] = useState({ items: [], total_items: 0, subtotal: 0 })
  const [loading, setLoading] = useState(false)

  const refreshCart = useCallback(async () => {
    if (!isAuth) { setCart({ items: [], total_items: 0, subtotal: 0 }); return }
    setLoading(true)
    try {
      const { data } = await api.get('/cart/')
      setCart(data)
    } catch {
      setCart({ items: [], total_items: 0, subtotal: 0 })
    } finally {
      setLoading(false)
    }
  }, [isAuth])

  const addToCart = async (productId, quantity = 1) => {
    const { data } = await api.post('/cart/items/', { product_id: productId, quantity })
    setCart(data)
    return data
  }

  const updateQty = async (itemId, quantity) => {
    const { data } = await api.patch(`/cart/items/${itemId}/`, { quantity })
    setCart(data)
  }

  const removeItem = async (itemId) => {
    const { data } = await api.delete(`/cart/items/${itemId}/remove/`)
    setCart(data)
  }

  useEffect(() => { refreshCart() }, [refreshCart])

  return (
    <CartContext.Provider value={{ cart, loading, refreshCart, addToCart, updateQty, removeItem }}>
      {children}
    </CartContext.Provider>
  )
}

export const useCart = () => useContext(CartContext)
