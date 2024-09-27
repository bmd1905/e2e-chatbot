"use client"

import Dashboard from "@/components/dashboard-03"
import { useAuth } from '@/hooks/useAuth'
import { useRouter } from 'next/navigation'
import { useEffect } from 'react'

export default function DashboardPage() {
    const { user, loading } = useAuth()
    const router = useRouter()

    useEffect(() => {
        if (!loading && !user) {
            router.push('/')
        }
    }, [user, loading, router])

    if (loading) {
        return <div>Loading...</div>
    }

    return user ? <Dashboard /> : null
}