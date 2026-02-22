import React from 'react';
import { StyleSheet, View, ScrollView, Pressable } from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import { ThemedText } from '@/components/themed-text';
import { useColorScheme } from '@/hooks/use-color-scheme';
import { Colors } from '@/constants/theme';
import { getVisit } from '@/data/visits';

export default function MedsPage() {
  const { visitId } = useLocalSearchParams<{ visitId: string }>();
  const router = useRouter();
  const scheme = useColorScheme() ?? 'light';
  const colors = Colors[scheme];
  const insets = useSafeAreaInsets();

  const visit = getVisit(visitId ?? '');
  if (!visit) return null;

  return (
    <View style={[styles.screen, { backgroundColor: colors.background }]}>
      <View style={[styles.header, { paddingTop: insets.top + 8, backgroundColor: colors.headerBg, borderBottomColor: colors.border }]}>
        <Pressable onPress={() => router.back()} style={styles.backBtn} hitSlop={12}>
          <Ionicons name="chevron-back" size={24} color={colors.tint} />
          <ThemedText style={[styles.backText, { color: colors.tint }]}>Back</ThemedText>
        </Pressable>
        <View style={styles.titleRow}>
          <Ionicons name="medkit" size={22} color={colors.tint} />
          <ThemedText style={[styles.pageTitle, { color: colors.text }]}>Medications</ThemedText>
        </View>
        <ThemedText style={[styles.pageSubtitle, { color: colors.secondaryText }]}>{visit.visitDate}</ThemedText>
      </View>

      <ScrollView style={styles.scroll} contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
        {visit.medications.map((med, i) => (
          <View key={i} style={[styles.card, { backgroundColor: colors.surface, borderColor: colors.border }]}>
            <View style={styles.topRow}>
              <ThemedText style={[styles.name, { color: colors.text }]}>{med.name}</ThemedText>
              {med.isNew && (
                <View style={[styles.badge, { backgroundColor: colors.tint }]}>
                  <ThemedText style={styles.badgeText}>NEW</ThemedText>
                </View>
              )}
            </View>
            <ThemedText style={[styles.dosage, { color: colors.text }]}>
              {med.dosage} — {med.frequency}
            </ThemedText>
            {med.notes ? (
              <ThemedText style={[styles.notes, { color: colors.secondaryText }]}>{med.notes}</ThemedText>
            ) : null}
          </View>
        ))}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1 },
  header: { paddingHorizontal: 20, paddingBottom: 16, borderBottomWidth: 1 },
  backBtn: { flexDirection: 'row', alignItems: 'center', gap: 4, marginBottom: 12 },
  backText: { fontSize: 17, fontWeight: '500' },
  titleRow: { flexDirection: 'row', alignItems: 'center', gap: 10 },
  pageTitle: { fontSize: 24, fontWeight: '800' },
  pageSubtitle: { fontSize: 15, marginTop: 4 },
  scroll: { flex: 1 },
  content: { padding: 20 },
  card: { borderRadius: 14, padding: 18, borderWidth: 1, marginBottom: 12 },
  topRow: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' },
  name: { fontSize: 19, fontWeight: '700' },
  badge: { paddingHorizontal: 10, paddingVertical: 4, borderRadius: 8 },
  badgeText: { color: '#fff', fontSize: 12, fontWeight: '800', letterSpacing: 0.5 },
  dosage: { fontSize: 16, marginTop: 8, lineHeight: 22 },
  notes: { fontSize: 15, marginTop: 8, lineHeight: 22 },
});
