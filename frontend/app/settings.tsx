import { useEffect } from 'react';
import { useRouter } from 'expo-router';

/** Settings is now part of the Profile page. This route redirects there. */
export default function SettingsRedirect() {
  const router = useRouter();
  useEffect(() => {
    router.replace('/profile' as any);
  }, [router]);
  return null;
}
