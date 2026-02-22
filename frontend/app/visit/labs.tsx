import React from 'react';
import { StyleSheet, View, ScrollView, Pressable } from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import { ThemedText } from '@/components/themed-text';
import { useColorScheme } from '@/hooks/use-color-scheme';
import { Colors } from '@/constants/theme';
import { getVisit } from '@/data/visits';

export default function LabsPage() {
  const { visitId } = useLocalSearchParams<{ visitId: string }>();
  const router = useRouter();
  const scheme = useColorScheme() ?? 'light';
  const colors = Colors[scheme];
  const insets = useSafeAreaInsets();

  const visit = getVisit(visitId ?? '');
  if (!visit) return null;

  const statusColor = (s: string) => (s === 'completed' ? '#10B981' : s === 'ordered' ? '#F59E0B' : '#6B7280');
  const statusLabel = (s: string) => (s === 'completed' ? 'Done' : s === 'ordered' ? 'Upcoming' : 'Pending');

  return (
    <View style={[styles.screen, { backgroundColor: colors.background }]}>
      <View style={[styles.header, { paddingTop: insets.top + 8, backgroundColor: colors.headerBg, borderBottomColor: colors.border }]}>
        <Pressable onPress={() => router.back()} style={styles.backBtn} hitSlop={12}>
          <Ionicons name="chevron-back" size={24} color={colors.tint} />
          <ThemedText style={[styles.backText, { color: colors.tint }]}>Back</ThemedText>
        </Pressable>
        <View style={styles.titleRow}>
          <Ionicons name="flask" size={22} color="#F59E0B" />
          <ThemedText style={[styles.pageTitle, { color: colors.text }]}>Lab Tests</ThemedText>
        </View>
        <ThemedText style={[styles.pageSubtitle, { color: colors.secondaryText }]}>{visit.visitDate}</ThemedText>
      </View>

      <ScrollView style={styles.scroll} contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
        {visit.labTests.map((lab, i) => (
          <View key={i} style={[styles.card, { backgroundColor: colors.surface, borderColor: colors.border }]}>
            <View style={styles.topRow}>
              <ThemedText style={[styles.name, { color: colors.text }]}>{lab.name}</ThemedText>
              <View style={[styles.statusBadge, { backgroundColor: statusColor(lab.status) + '18' }]}>
                <ThemedText style={[styles.statusText, { color: statusColor(lab.status) }]}>
                  {statusLabel(lab.status)}
                </ThemedText>
              </View>
            </View>
            {lab.result ? (
              <View style={styles.resultRow}>
                <ThemedText style={[styles.resultLabel, { color: colors.secondaryText }]}>Result:</ThemedText>
                <ThemedText style={[styles.resultValue, { color: colors.text }]}>{lab.result}</ThemedText>
              </View>
            ) : null}
            {lab.date ? (
              <View style={styles.infoRow}>
                <Ionicons name="calendar-outline" size={16} color={colors.secondaryText} />
                <ThemedText style={[styles.infoText, { color: colors.secondaryText }]}>{lab.date}</ThemedText>
              </View>
            ) : null}
            {lab.notes ? (
              <ThemedText style={[styles.notes, { color: colors.secondaryText }]}>{lab.notes}</ThemedText>
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
  name: { fontSize: 19, fontWeight: '700', flex: 1, marginRight: 10 },
  statusBadge: { paddingHorizontal: 10, paddingVertical: 4, borderRadius: 8 },
  statusText: { fontSize: 13, fontWeight: '700' },
  resultRow: { flexDirection: 'row', alignItems: 'center', gap: 6, marginTop: 10 },
  resultLabel: { fontSize: 15, fontWeight: '500' },
  resultValue: { fontSize: 17, fontWeight: '700' },
  infoRow: { flexDirection: 'row', alignItems: 'center', gap: 6, marginTop: 8 },
  infoText: { fontSize: 15 },
  notes: { fontSize: 15, marginTop: 8, lineHeight: 22 },
});
