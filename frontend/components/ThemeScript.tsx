'use client'

export function ThemeScript() {
  const themeScript = `
    (function() {
      try {
        // Get stored theme preference
        const storedTheme = localStorage.getItem('theme');
        const store = localStorage.getItem('tradingai-store');
        
        let themeToApply = 'light';
        
        if (store) {
          try {
            const parsed = JSON.parse(store);
            const settingsTheme = parsed?.state?.settings?.theme || 'light';
            
            if (settingsTheme === 'system') {
              // Use system preference
              themeToApply = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
            } else {
              themeToApply = settingsTheme;
            }
          } catch (e) {
            // Fall back to storedTheme or light
            themeToApply = storedTheme || 'light';
          }
        } else if (storedTheme) {
          themeToApply = storedTheme;
        }
        
        // Apply theme immediately to prevent flash
        const root = document.documentElement;
        root.classList.remove('light', 'dark');
        root.classList.add(themeToApply);
        root.setAttribute('data-theme', themeToApply);
      } catch (e) {
        // Fallback to light theme
        document.documentElement.classList.add('light');
        document.documentElement.setAttribute('data-theme', 'light');
      }
    })();
  `

  return (
    <script
      dangerouslySetInnerHTML={{
        __html: themeScript,
      }}
    />
  )
}

