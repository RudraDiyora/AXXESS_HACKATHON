import React from 'react';
import { StyleSheet, View, ScrollView, Pressable } from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import { ThemedText } from '@/components/themed-text';
import { useColorScheme } from '@/hooks/use-color-scheme';
import { Colors } from '@/constants/theme';
import { getVisit } from '@/data/visits';

export default function TranscriptPage() {
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
          <Ionicons name="chatbubbles" size={22} color="#6B7280" />
          <ThemedText style={[styles.pageTitle, { color: colors.text }]}>Full Transcript</ThemedText>
        </View>
        <ThemedText style={[styles.pageSubtitle, { color: colors.secondaryText }]}>
          {visit.visitDate} · {visit.transcript.length} entries
        </ThemedText>
      </View>

      <ScrollView style={styles.scroll} contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
        {visit.transcript.map((entry, i) => (
          <View key={i} style={[styles.entry, i > 0 && { borderTopWidth: 1, borderTopColor: colors.border }]}>
            <View
              style={[
                styles.speakerBadge,
                { backgroundColor: entry.speaker === 'doctor' ? colors.tint + '15' : '#10B98115' },
              ]}
            >
              <Ionicons
                name={entry.speaker === 'doctor' ? 'person' : 'person-outline'}
                size={14}
                color={entry.speaker === 'doctor' ? colors.tint : '#10B981'}
              />
              <ThemedText
                style={[styles.speakerLabel, { color: entry.speaker === 'doctor' ? colors.tint : '#10B981' }]}
              >
                {entry.speaker === 'doctor' ? 'Doctor' : 'Patient'}
              </ThemedText>
            </View>
            <ThemedText style={[styles.entryText, { color: colors.text }]}>{entry.text}</ThemedText>
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
  entry: { paddingVertical: 16 },
  speakerBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    alignSelf: 'flex-start',
    paddingHorizontal: 10,
    paddingVertical: 5,
    borderRadius: 10,
    gap: 6,
    marginBottom: 8,
  },
  speakerLabel: { fontSize: 14, fontWeight: '700' },
  entryText: { fontSize: 17, lineHeight: 26 },
});
