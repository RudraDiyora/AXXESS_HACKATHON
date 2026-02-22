import React, { createContext, useContext, useState, useCallback } from 'react';
import { useColorScheme as useSystemScheme } from 'react-native';

type SchemeOverride = 'light' | 'dark' | 'system';

interface ThemeContextValue {
  scheme: 'light' | 'dark';
  override: SchemeOverride;
  setOverride: (o: SchemeOverride) => void;
  isDark: boolean;
  toggleDarkMode: () => void;
}

const ThemeContext = createContext<ThemeContextValue>({
  scheme: 'light',
  override: 'system',
  setOverride: () => {},
  isDark: false,
  toggleDarkMode: () => {},
});

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const systemScheme = useSystemScheme() ?? 'light';
  const [override, setOverride] = useState<SchemeOverride>('system');

  const scheme: 'light' | 'dark' =
    override === 'system' ? systemScheme : override;

  const toggleDarkMode = useCallback(() => {
    setOverride((prev) => {
      if (prev === 'system') return systemScheme === 'dark' ? 'light' : 'dark';
      return prev === 'dark' ? 'light' : 'dark';
    });
  }, [systemScheme]);

  return (
    <ThemeContext.Provider value={{ scheme, override, setOverride, isDark: scheme === 'dark', toggleDarkMode }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  return useContext(ThemeContext);
}
