// components/UI/Background.js
export default function Background({ children, opacity = 10, overlay = true }) {
  return (
    <div className="relative min-h-screen">
      {/* Background Image Container */}
      <div className="fixed inset-0 -z-10 h-full w-full">
        {/* Background Image */}
        <div 
          className="absolute inset-0 bg-cover bg-center bg-no-repeat"
          style={{
            backgroundImage: `url('/background.png')`,
            opacity: `${opacity}%`,
          }}
        />
        
        {/* Optional Gradient Overlay */}
        {overlay && (
          <div className="absolute inset-0 bg-gradient-to-br from-blue-50/60 via-transparent to-purple-50/60 dark:from-gray-900/80 dark:via-gray-800/60 dark:to-gray-900/80" />
        )}
        
        {/* Optional Pattern Overlay */}
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-transparent via-transparent to-white/5 dark:to-gray-900/10" />
      </div>
      
      {/* Content */}
      <div className="relative z-10">
        {children}
      </div>
    </div>
  )
}