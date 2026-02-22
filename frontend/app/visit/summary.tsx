import React from 'react';
import { StyleSheet, View, ScrollView, Pressable } from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import { ThemedText } from '@/components/themed-text';
import { useColorScheme } from '@/hooks/use-color-scheme';
import { Colors } from '@/constants/theme';
import { getVisit } from '@/data/visits';

export default function VisitSummaryPage() {
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
        <ThemedText style={[styles.pageTitle, { color: colors.text }]}>What the Doctor Said</ThemedText>
        <ThemedText style={[styles.pageSubtitle, { color: colors.secondaryText }]}>{visit.visitDate}</ThemedText>
      </View>

      <ScrollView style={styles.scroll} contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
        <ThemedText style={[styles.body, { color: colors.text }]}>{visit.summaryText}</ThemedText>

        {visit.chiefComplaint ? (
          <View style={[styles.card, { backgroundColor: colors.surface, borderColor: colors.border }]}>
            <ThemedText style={[styles.cardLabel, { color: colors.secondaryText }]}>Reason for Visit</ThemedText>
            <ThemedText style={[styles.cardValue, { color: colors.text }]}>{visit.chiefComplaint}</ThemedText>
          </View>
        ) : null}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1 },
  header: { paddingHorizontal: 20, paddingBottom: 16, borderBottomWidth: 1 },
  backBtn: { flexDirection: 'row', alignItems: 'center', gap: 4, marginBottom: 12 },
  backText: { fontSize: 17, fontWeight: '500' },
  pageTitle: { fontSize: 24, fontWeight: '800' },
  pageSubtitle: { fontSize: 15, marginTop: 4 },
  scroll: { flex: 1 },
  content: { padding: 20 },
  body: { fontSize: 18, lineHeight: 30, fontWeight: '400' },
  card: { marginTop: 24, borderRadius: 14, padding: 18, borderWidth: 1 },
  cardLabel: { fontSize: 13, fontWeight: '600', textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 6 },
  cardValue: { fontSize: 17, fontWeight: '500', lineHeight: 24 },
});
