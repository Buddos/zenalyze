import React from 'react'
import { cn } from '@/lib/utils'

export interface BackgroundProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode
  variant?: 'default' | 'gradient' | 'calm' | 'card'
}

const Background: React.FC<BackgroundProps> = ({
  children,
  className,
  variant = 'default',
  ...props
}) => {
  const variantClasses = {
    default: 'bg-background',
    gradient: 'bg-gradient-hero',
    calm: 'bg-gradient-calm',
    card: 'bg-gradient-card',
  }

  return (
    <div
      className={cn(
        'min-h-screen transition-all duration-300',
        variantClasses[variant],
        className
      )}
      {...props}
    >
      {children}
    </div>
  )
}

export default Background
