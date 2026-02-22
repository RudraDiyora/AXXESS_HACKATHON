import React from 'react';
import { StyleSheet, View, Pressable, Platform, Text } from 'react-native';
import { BottomTabBarProps } from '@react-navigation/bottom-tabs';
import { Ionicons } from '@expo/vector-icons';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import { Colors } from '@/constants/theme';
import { useColorScheme } from '@/hooks/use-color-scheme';

const TAB_ICONS: Record<string, { active: keyof typeof Ionicons.glyphMap; inactive: keyof typeof Ionicons.glyphMap }> = {
  record: { active: 'mic', inactive: 'mic-outline' },
  summary: { active: 'clipboard', inactive: 'clipboard-outline' },
  medications: { active: 'heart', inactive: 'heart-outline' },
};

const TAB_LABELS: Record<string, string> = {
  record: 'Record',
  summary: 'Visit',
  medications: 'Care Plan',
};

export function FloatingTabBar({ state, navigation }: BottomTabBarProps) {
  const scheme = useColorScheme() ?? 'light';
  const colors = Colors[scheme];
  const insets = useSafeAreaInsets();

  return (
    <View style={[styles.container, {
      backgroundColor: colors.headerBg,
      borderTopColor: colors.border,
      paddingBottom: Math.max(insets.bottom, 8),
    }]}>
      {state.routes
        .filter((route) => TAB_ICONS[route.name])
        .map((route) => {
          const isFocused = state.routes[state.index].name === route.name;
          const icons = TAB_ICONS[route.name];
          const label = TAB_LABELS[route.name] ?? route.name;

          return (
            <Pressable
              key={route.key}
              onPress={() => {
                const event = navigation.emit({
                  type: 'tabPress',
                  target: route.key,
                  canPreventDefault: true,
                });
                if (!isFocused && !event.defaultPrevented) {
                  navigation.navigate(route.name);
                }
              }}
              style={styles.tab}
            >
              {isFocused && <View style={[styles.indicator, { backgroundColor: colors.tint }]} />}
              <Ionicons
                name={isFocused ? icons.active : icons.inactive}
                size={22}
                color={isFocused ? colors.tint : colors.tabIconDefault}
              />
              <Text style={[styles.label, { color: isFocused ? colors.tint : colors.tabIconDefault }]}>
                {label}
              </Text>
            </Pressable>
          );
        })}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    borderTopWidth: 1,
    paddingTop: 8,
  },
  tab: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    gap: 4,
    paddingVertical: 4,
    position: 'relative',
  },
  indicator: {
    position: 'absolute',
    top: -8,
    width: 24,
    height: 3,
    borderRadius: 2,
  },
  label: {
    fontSize: 11,
    fontWeight: '600',
    letterSpacing: 0.1,
  },
});
