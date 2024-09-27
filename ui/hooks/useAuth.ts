import { useState, useEffect } from 'react'
import api from '@/lib/api'

export function useAuth() {
    const [user, setUser] = useState(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        const checkAuth = async () => {
            const token = localStorage.getItem('token')
            if (token) {
                try {
                    const response = await api.get('/users/me')
                    setUser(response.data)
                } catch (error) {
                    localStorage.removeItem('token')
                }
            }
            setLoading(false)
        }
        checkAuth()
    }, [])

    const logout = () => {
        localStorage.removeItem('token')
        setUser(null)
    }

    return { user, loading, logout }
}