import React from 'react';
import { StyleSheet, View, Pressable, Platform, Text } from 'react-native';
import { useRouter } from 'expo-router';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';

import { Colors } from '@/constants/theme';
import { useColorScheme } from '@/hooks/use-color-scheme';

interface AppHeaderProps {
  title: string;
  subtitle?: string;
}

export function AppHeader({ title, subtitle }: AppHeaderProps) {
  const router = useRouter();
  const scheme = useColorScheme() ?? 'light';
  const insets = useSafeAreaInsets();
  const colors = Colors[scheme];

  return (
    <View style={[styles.header, { backgroundColor: colors.headerBg, paddingTop: insets.top + 8, borderBottomColor: colors.border }]}>
      <View style={styles.row}>
        <View style={styles.logoRow}>
          <View style={[styles.logoIcon, { backgroundColor: colors.tint }]}>  
            <Ionicons name="pulse" size={18} color="#fff" />
          </View>
          <View>
            <Text style={[styles.appName, { color: colors.text }]}>MedScribe</Text>
            {subtitle ? (
              <Text style={[styles.subtitle, { color: colors.secondaryText }]}>{subtitle}</Text>
            ) : null}
          </View>
        </View>

        <Pressable
            onPress={() => router.push('/profile' as any)}
            style={({ pressed }) => [
              styles.avatar,
              { backgroundColor: colors.surface, borderColor: colors.border, opacity: pressed ? 0.7 : 1 },
            ]}
          >
            <Ionicons name="person" size={16} color={colors.tint} />
          </Pressable>
      </View>

      <Text style={[styles.pageTitle, { color: colors.text }]}>{title}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  header: {
    paddingHorizontal: 20,
    paddingBottom: 16,
    borderBottomWidth: 1,
  },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  logoRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
  },
  logoIcon: {
    width: 32,
    height: 32,
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
  },
  appName: {
    fontSize: 16,
    fontWeight: '700',
    letterSpacing: 0.2,
  },
  subtitle: {
    fontSize: 12,
    marginTop: 1,
  },
  avatar: {
    width: 34,
    height: 34,
    borderRadius: 17,
    borderWidth: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  pageTitle: {
    fontSize: 26,
    fontWeight: '800',
    marginTop: 14,
    letterSpacing: -0.5,
  },
});
