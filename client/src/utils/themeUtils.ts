/**
 * Theme Utility Functions
 * 
 * Provides theme-aware class utilities for consistent styling across
 * dark and light modes. All components should use these utilities instead
 * of hardcoded color classes.
 */

import { useTheme } from '@/context/ThemeContext';

/**
 * Theme-aware class mappings for common UI elements
 */
export interface ThemeClasses {
  background: {
    primary: string;
    secondary: string;
    card: string;
    muted: string;
    hover: string;
  };
  text: {
    primary: string;
    secondary: string;
    muted: string;
    white: string;
    inverse: string;
  };
  border: {
    default: string;
    light: string;
    muted: string;
  };
  interactive: {
    hover: {
      background: string;
      text: string;
    };
  };
}

/**
 * Hook that returns theme-aware CSS classes based on the current theme
 * 
 * @returns ThemeClasses object with theme-appropriate Tailwind classes
 * 
 * @example
 * ```tsx
 * const classes = useThemeClasses();
 * 
 * return (
 *   <div className={classes.background.card}>
 *     <p className={classes.text.primary}>Content</p>
 *   </div>
 * );
 * ```
 */
export function useThemeClasses(): ThemeClasses {
  const { resolvedTheme } = useTheme();
  const isDark = resolvedTheme === 'dark';

  return {
    background: {
      primary: isDark ? 'bg-slate-900' : 'bg-white',
      secondary: isDark ? 'bg-slate-800' : 'bg-slate-50',
      card: isDark ? 'bg-slate-800' : 'bg-white',
      muted: isDark ? 'bg-slate-900/50' : 'bg-slate-50',
      hover: isDark ? 'hover:bg-slate-700' : 'hover:bg-slate-100',
    },
    text: {
      primary: isDark ? 'text-slate-100' : 'text-slate-900',
      secondary: isDark ? 'text-slate-400' : 'text-slate-600',
      muted: isDark ? 'text-slate-500' : 'text-slate-500',
      white: isDark ? 'text-white' : 'text-slate-900',
      inverse: isDark ? 'text-slate-900' : 'text-slate-100',
    },
    border: {
      default: isDark ? 'border-slate-700' : 'border-slate-200',
      light: isDark ? 'border-slate-800' : 'border-slate-300',
      muted: isDark ? 'border-slate-600' : 'border-slate-400',
    },
    interactive: {
      hover: {
        background: isDark ? 'hover:bg-slate-700' : 'hover:bg-slate-100',
        text: isDark ? 'hover:text-slate-100' : 'hover:text-slate-900',
      },
    },
  };
}

/**
 * Get theme-aware background class
 * 
 * @param variant - Background variant: 'primary' | 'secondary' | 'card' | 'muted'
 * @returns Theme-appropriate background class
 */
export function getBackgroundClass(variant: 'primary' | 'secondary' | 'card' | 'muted' = 'card'): string {
  const { resolvedTheme } = useTheme();
  const isDark = resolvedTheme === 'dark';

  const classes = {
    primary: isDark ? 'bg-slate-900' : 'bg-white',
    secondary: isDark ? 'bg-slate-800' : 'bg-slate-50',
    card: isDark ? 'bg-slate-800' : 'bg-white',
    muted: isDark ? 'bg-slate-900/50' : 'bg-slate-50',
  };

  return classes[variant];
}

/**
 * Get theme-aware text class
 * 
 * @param variant - Text variant: 'primary' | 'secondary' | 'muted' | 'white'
 * @returns Theme-appropriate text class
 */
export function getTextClass(variant: 'primary' | 'secondary' | 'muted' | 'white' = 'primary'): string {
  const { resolvedTheme } = useTheme();
  const isDark = resolvedTheme === 'dark';

  const classes = {
    primary: isDark ? 'text-slate-100' : 'text-slate-900',
    secondary: isDark ? 'text-slate-400' : 'text-slate-600',
    muted: isDark ? 'text-slate-500' : 'text-slate-500',
    white: isDark ? 'text-white' : 'text-slate-900',
  };

  return classes[variant];
}

/**
 * Get theme-aware border class
 * 
 * @param variant - Border variant: 'default' | 'light' | 'muted'
 * @returns Theme-appropriate border class
 */
export function getBorderClass(variant: 'default' | 'light' | 'muted' = 'default'): string {
  const { resolvedTheme } = useTheme();
  const isDark = resolvedTheme === 'dark';

  const classes = {
    default: isDark ? 'border-slate-700' : 'border-slate-200',
    light: isDark ? 'border-slate-800' : 'border-slate-300',
    muted: isDark ? 'border-slate-600' : 'border-slate-400',
  };

  return classes[variant];
}
