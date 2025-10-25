'use client'

import { useEffect } from 'react'

export function UIEnhancements() {
  useEffect(() => {
    // Add smooth scrolling behavior
    document.documentElement.style.scrollBehavior = 'smooth'
    
    // Add custom CSS for enhanced UI
    const style = document.createElement('style')
    style.textContent = `
      /* Enhanced animations */
      @keyframes fadeInUp {
        from {
          opacity: 0;
          transform: translateY(20px);
        }
        to {
          opacity: 1;
          transform: translateY(0);
        }
      }
      
      @keyframes slideInRight {
        from {
          opacity: 0;
          transform: translateX(20px);
        }
        to {
          opacity: 1;
          transform: translateX(0);
        }
      }
      
      @keyframes pulse {
        0%, 100% {
          opacity: 1;
        }
        50% {
          opacity: 0.5;
        }
      }
      
      @keyframes bounce {
        0%, 20%, 53%, 80%, 100% {
          transform: translate3d(0,0,0);
        }
        40%, 43% {
          transform: translate3d(0, -8px, 0);
        }
        70% {
          transform: translate3d(0, -4px, 0);
        }
        90% {
          transform: translate3d(0, -2px, 0);
        }
      }
      
      /* Enhanced button styles */
      .btn-enhanced {
        @apply transition-all duration-200 ease-in-out;
        @apply hover:scale-105 active:scale-95;
        @apply focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2;
      }
      
      /* Enhanced input styles */
      .input-enhanced {
        @apply transition-all duration-200 ease-in-out;
        @apply focus:ring-2 focus:ring-primary-500 focus:border-primary-500;
        @apply hover:border-gray-400 dark:hover:border-gray-500;
      }
      
      /* Enhanced card styles */
      .card-enhanced {
        @apply transition-all duration-200 ease-in-out;
        @apply hover:shadow-lg hover:shadow-gray-200/50 dark:hover:shadow-gray-800/50;
        @apply hover:-translate-y-1;
      }
      
      /* Enhanced message bubble animations */
      .message-bubble {
        animation: fadeInUp 0.3s ease-out;
      }
      
      .message-bubble.user {
        animation: slideInRight 0.3s ease-out;
      }
      
      /* Enhanced loading states */
      .loading-shimmer {
        background: linear-gradient(90deg, 
          rgba(255,255,255,0) 0%, 
          rgba(255,255,255,0.2) 50%, 
          rgba(255,255,255,0) 100%);
        background-size: 200% 100%;
        animation: shimmer 1.5s infinite;
      }
      
      @keyframes shimmer {
        0% {
          background-position: -200% 0;
        }
        100% {
          background-position: 200% 0;
        }
      }
      
      /* Enhanced scrollbar */
      .scrollbar-enhanced::-webkit-scrollbar {
        width: 6px;
      }
      
      .scrollbar-enhanced::-webkit-scrollbar-track {
        background: transparent;
      }
      
      .scrollbar-enhanced::-webkit-scrollbar-thumb {
        background: rgba(156, 163, 175, 0.3);
        border-radius: 3px;
      }
      
      .scrollbar-enhanced::-webkit-scrollbar-thumb:hover {
        background: rgba(156, 163, 175, 0.5);
      }
      
      /* Dark mode scrollbar */
      .dark .scrollbar-enhanced::-webkit-scrollbar-thumb {
        background: rgba(75, 85, 99, 0.3);
      }
      
      .dark .scrollbar-enhanced::-webkit-scrollbar-thumb:hover {
        background: rgba(75, 85, 99, 0.5);
      }
      
      /* Enhanced focus states */
      .focus-enhanced:focus {
        @apply outline-none ring-2 ring-primary-500 ring-offset-2;
      }
      
      /* Enhanced hover states */
      .hover-enhanced:hover {
        @apply transform scale-105;
      }
      
      /* Enhanced transitions */
      .transition-enhanced {
        @apply transition-all duration-300 ease-in-out;
      }
      
      /* Enhanced shadows */
      .shadow-enhanced {
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
      }
      
      .shadow-enhanced-lg {
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
      }
      
      /* Enhanced gradients */
      .gradient-primary {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      }
      
      .gradient-secondary {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
      }
      
      /* Enhanced text effects */
      .text-gradient {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
      }
      
      /* Enhanced backdrop blur */
      .backdrop-blur-enhanced {
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
      }
    `
    document.head.appendChild(style)
    
    return () => {
      document.head.removeChild(style)
    }
  }, [])

  return null
}

