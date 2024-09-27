"use client"

import React from 'react'
import { useAuth } from '@/hooks/useAuth'
import Login from "@/components/authentication-04"
import { useRouter } from 'next/navigation'

export default function Home() {
    const { user, loading } = useAuth()
    const router = useRouter()

    const handleLoginSuccess = async (userData: any) => {
        // Redirect to Dashboard after successful login
        router.push('/dashboard')
    }

    if (loading) {
        return <div>Loading...</div>
    }

    if (user) {
        router.push('/dashboard')
        return null
    }

    return <Login onLoginSuccess={handleLoginSuccess} />
}