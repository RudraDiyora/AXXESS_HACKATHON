import { useTheme } from '@/contexts/theme-context';

export function useColorScheme() {
  const { scheme } = useTheme();
  return scheme;
}
