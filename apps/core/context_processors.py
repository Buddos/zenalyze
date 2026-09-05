def get_theme_css(theme='light'):
    shared = {
        '--sidebar-bg': '#0f172a',
        '--sidebar-text': '#94a3b8',
        '--sidebar-text-hover': '#e2e8f0',
        '--sidebar-active-bg': 'rgba(102,126,234,0.15)',
        '--sidebar-active-text': '#a5b4fc',
        '--sidebar-border': 'rgba(255,255,255,0.06)',
        '--radius-sm': '8px',
        '--radius': '14px',
        '--radius-lg': '20px',
        '--transition': 'all 0.25s cubic-bezier(0.4, 0, 0.2, 1)',
    }

    themes = {
        'light': {
            '--bg-primary': '#f8fafc',
            '--bg-secondary': '#ffffff',
            '--text-primary': '#1e293b',
            '--text-secondary': '#64748b',
            '--text-muted': '#94a3b8',
            '--border-color': '#e2e8f0',
            '--card-bg': '#ffffff',
            '--navbar-bg': '#ffffff',
            '--link-color': '#667eea',
            '--link-hover': '#764ba2',
            '--link-active': '#5a52d5',
            '--success-bg': '#ecfdf5',
            '--success-text': '#065f46',
            '--success-border': '#a7f3d0',
            '--danger-bg': '#fef2f2',
            '--danger-text': '#991b1b',
            '--danger-border': '#fecaca',
            '--warning-bg': '#fffbeb',
            '--warning-text': '#92400e',
            '--warning-border': '#fde68a',
            '--info-bg': '#eff6ff',
            '--info-text': '#1e40af',
            '--info-border': '#bfdbfe',
            '--hover-bg': '#f1f5f9',
            '--shadow-sm': '0 1px 3px rgba(0,0,0,0.06)',
            '--shadow-md': '0 4px 15px rgba(0,0,0,0.08)',
            '--shadow-lg': '0 10px 30px rgba(0,0,0,0.12)',
            '--input-bg': '#ffffff',
            '--input-border': '#e2e8f0',
            '--input-focus': '#667eea',
            '--modal-overlay': 'rgba(0,0,0,0.5)',
        },
        'dark': {
            '--bg-primary': '#0f172a',
            '--bg-secondary': '#1e293b',
            '--text-primary': '#f1f5f9',
            '--text-secondary': '#94a3b8',
            '--text-muted': '#64748b',
            '--border-color': '#334155',
            '--card-bg': '#1e293b',
            '--navbar-bg': '#1e293b',
            '--link-color': '#818cf8',
            '--link-hover': '#a78bfa',
            '--link-active': '#6366f1',
            '--success-bg': '#064e3b',
            '--success-text': '#6ee7b7',
            '--success-border': '#065f46',
            '--danger-bg': '#7f1d1d',
            '--danger-text': '#fca5a5',
            '--danger-border': '#991b1b',
            '--warning-bg': '#78350f',
            '--warning-text': '#fde68a',
            '--warning-border': '#92400e',
            '--info-bg': '#1e3a8a',
            '--info-text': '#93c5fd',
            '--info-border': '#1e40af',
            '--hover-bg': '#1e293b',
            '--shadow-sm': '0 1px 3px rgba(0,0,0,0.3)',
            '--shadow-md': '0 4px 15px rgba(0,0,0,0.4)',
            '--shadow-lg': '0 10px 30px rgba(0,0,0,0.5)',
            '--input-bg': '#1e293b',
            '--input-border': '#334155',
            '--input-focus': '#818cf8',
            '--modal-overlay': 'rgba(0,0,0,0.7)',
        },
        'auto': {
            '--bg-primary': '#f8fafc',
            '--bg-secondary': '#ffffff',
            '--text-primary': '#1e293b',
            '--text-secondary': '#64748b',
            '--text-muted': '#94a3b8',
            '--border-color': '#e2e8f0',
            '--card-bg': '#ffffff',
            '--navbar-bg': '#ffffff',
            '--link-color': '#667eea',
            '--link-hover': '#764ba2',
            '--link-active': '#5a52d5',
            '--success-bg': '#ecfdf5',
            '--success-text': '#065f46',
            '--success-border': '#a7f3d0',
            '--danger-bg': '#fef2f2',
            '--danger-text': '#991b1b',
            '--danger-border': '#fecaca',
            '--warning-bg': '#fffbeb',
            '--warning-text': '#92400e',
            '--warning-border': '#fde68a',
            '--info-bg': '#eff6ff',
            '--info-text': '#1e40af',
            '--info-border': '#bfdbfe',
            '--hover-bg': '#f1f5f9',
            '--shadow-sm': '0 1px 3px rgba(0,0,0,0.06)',
            '--shadow-md': '0 4px 15px rgba(0,0,0,0.08)',
            '--shadow-lg': '0 10px 30px rgba(0,0,0,0.12)',
            '--input-bg': '#ffffff',
            '--input-border': '#e2e8f0',
            '--input-focus': '#667eea',
            '--modal-overlay': 'rgba(0,0,0,0.5)',
        }
    }

    selected_theme = theme if theme in themes else 'light'
    vars_dict = {**shared, **themes[selected_theme]}
    
    lines = [":root {"]
    for k, v in vars_dict.items():
        lines.append(f"    {k}: {v};")
    lines.append("}")
    
    if selected_theme == 'auto':
        lines.append("@media (prefers-color-scheme: dark) {")
        lines.append("    :root {")
        for k, v in themes['dark'].items():
            if k not in shared:
                lines.append(f"        {k}: {v};")
        lines.append("    }")
        lines.append("}")
        
    return "\n".join(lines)


def theme_context(request):
    theme = 'light'
    if request.user.is_authenticated:
        if hasattr(request.user, 'settings') and request.user.settings.theme:
            theme = request.user.settings.theme
        elif 'user_theme' in request.session:
            theme = request.session['user_theme']
    elif 'user_theme' in request.session:
        theme = request.session['user_theme']
    elif 'user_theme' in request.COOKIES:
        theme = request.COOKIES['user_theme']
        
    if theme not in ['light', 'dark', 'auto']:
        theme = 'light'

    calm_colors = {
        'primary': '#5D8AA8',
        'secondary': '#7FB685',
        'accent': '#B8B8D1',
        'light': '#F8F9FA',
        'dark': '#2C3E50',
        'text': '#34495E',
        'text_light': '#7F8C8D',
    }

    return {
        'current_theme': theme,
        'theme_css': get_theme_css(theme),
        'calm_colors': calm_colors,
        'SITE_NAME': 'Zenalyze',
    }
