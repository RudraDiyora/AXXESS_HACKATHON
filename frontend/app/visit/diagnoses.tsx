import React from 'react';
import { StyleSheet, View, ScrollView, Pressable } from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import { ThemedText } from '@/components/themed-text';
import { useColorScheme } from '@/hooks/use-color-scheme';
import { Colors } from '@/constants/theme';
import { getVisit } from '@/data/visits';

export default function DiagnosesPage() {
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
        <View style={styles.headerRow}>
          <Pressable onPress={() => router.back()} style={[styles.backBtn, { backgroundColor: colors.tint + '15' }]} hitSlop={12}>
            <Ionicons name="chevron-back" size={20} color={colors.tint} />
          </Pressable>
          <Ionicons name="heart" size={22} color="#EF4444" />
          <ThemedText style={[styles.pageTitle, { color: colors.text }]}>Diagnoses</ThemedText>
        </View>
        <ThemedText style={[styles.pageSubtitle, { color: colors.secondaryText }]}>{visit.visitDate}</ThemedText>
      </View>

      <ScrollView style={styles.scroll} contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
        {visit.diagnoses.map((d, i) => (
          <View key={i} style={[styles.card, { backgroundColor: colors.surface, borderColor: colors.border }]}>
            <ThemedText style={[styles.name, { color: colors.text }]}>{d.name}</ThemedText>
            {d.icdCode ? (
              <View style={[styles.codeBadge, { backgroundColor: colors.border }]}>
                <ThemedText style={[styles.codeText, { color: colors.secondaryText }]}>ICD: {d.icdCode}</ThemedText>
              </View>
            ) : null}
            {d.notes ? (
              <ThemedText style={[styles.notes, { color: colors.secondaryText }]}>{d.notes}</ThemedText>
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
  headerRow: { flexDirection: 'row', alignItems: 'center', gap: 12 },
  backBtn: { width: 36, height: 36, borderRadius: 18, alignItems: 'center', justifyContent: 'center' },
  pageTitle: { fontSize: 24, fontWeight: '800' },
  pageSubtitle: { fontSize: 15, marginTop: 4 },
  scroll: { flex: 1 },
  content: { padding: 20 },
  card: { borderRadius: 14, padding: 18, borderWidth: 1, marginBottom: 12 },
  name: { fontSize: 19, fontWeight: '700', lineHeight: 26 },
  codeBadge: { alignSelf: 'flex-start', marginTop: 8, paddingHorizontal: 10, paddingVertical: 4, borderRadius: 8 },
  codeText: { fontSize: 13, fontWeight: '600' },
  notes: { fontSize: 16, marginTop: 10, lineHeight: 24 },
});
