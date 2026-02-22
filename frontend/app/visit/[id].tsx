import React from 'react';
import { StyleSheet, View, ScrollView, Pressable } from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import { ThemedText } from '@/components/themed-text';
import { useColorScheme } from '@/hooks/use-color-scheme';
import { Colors } from '@/constants/theme';
import { getVisit } from '@/data/visits';

export default function VisitDetailScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const router = useRouter();
  const scheme = useColorScheme() ?? 'light';
  const colors = Colors[scheme];
  const insets = useSafeAreaInsets();

  const visit = getVisit(id ?? '');

  if (!visit) {
    return (
      <View style={[styles.screen, { backgroundColor: colors.background, paddingTop: insets.top + 40 }]}>
        <ThemedText style={{ color: colors.text, textAlign: 'center', fontSize: 18 }}>
          Visit not found.
        </ThemedText>
      </View>
    );
  }

  const newMeds = visit.medications.filter((m) => m.isNew).length;
  const doneLabs = visit.labTests.filter((l) => l.status === 'completed').length;
  const pendingLabs = visit.labTests.length - doneLabs;

  return (
    <View style={[styles.screen, { backgroundColor: colors.background }]}>
      {/* Header */}
      <View
        style={[styles.header, { paddingTop: insets.top + 8, backgroundColor: colors.headerBg, borderBottomColor: colors.border }]}
      >
        <Pressable onPress={() => router.back()} style={styles.backBtn} hitSlop={12}>
          <Ionicons name="chevron-back" size={24} color={colors.tint} />
          <ThemedText style={[styles.backText, { color: colors.tint }]}>Visits</ThemedText>
        </Pressable>
        <ThemedText style={[styles.headerDate, { color: colors.text }]}>{visit.visitDate}</ThemedText>
        <ThemedText style={[styles.headerDoctor, { color: colors.secondaryText }]}>
          {visit.doctorName} · {visit.specialty}
        </ThemedText>
        <ThemedText style={[styles.headerChief, { color: colors.text }]} numberOfLines={2}>
          {visit.chiefComplaint}
        </ThemedText>
      </View>

      <ScrollView style={styles.scroll} contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
        {/* ── Summary card (full width) ── */}
        <Pressable
          onPress={() => router.push({ pathname: '/visit/summary', params: { visitId: visit.id } })}
          style={[styles.bentoFull, { backgroundColor: colors.surface, borderColor: colors.border }]}
        >
          <View style={styles.bentoRow}>
            <View style={[styles.iconCircle, { backgroundColor: colors.tint + '15' }]}>
              <Ionicons name="chatbox-ellipses" size={20} color={colors.tint} />
            </View>
            <ThemedText style={[styles.bentoFullTitle, { color: colors.text }]}>What the Doctor Said</ThemedText>
            <Ionicons name="chevron-forward" size={18} color={colors.icon} />
          </View>
          <ThemedText style={[styles.bentoPreview, { color: colors.secondaryText }]} numberOfLines={3}>
            {visit.summaryText}
          </ThemedText>
        </Pressable>

        {/* ── 2 × 2 bento grid ── */}
        <View style={styles.gridRow}>
          {/* Diagnoses */}
          <Pressable
            onPress={() => router.push({ pathname: '/visit/diagnoses', params: { visitId: visit.id } })}
            style={[styles.bentoHalf, { backgroundColor: colors.surface, borderColor: colors.border }]}
          >
            <View style={[styles.iconCircle, { backgroundColor: '#EF444415' }]}>
              <Ionicons name="heart" size={20} color="#EF4444" />
            </View>
            <ThemedText style={[styles.bentoCount, { color: colors.text }]}>{visit.diagnoses.length}</ThemedText>
            <ThemedText style={[styles.bentoLabel, { color: colors.secondaryText }]}>Diagnoses</ThemedText>
            <ThemedText style={[styles.bentoHint, { color: colors.secondaryText }]} numberOfLines={1}>
              {visit.diagnoses[0]?.name}
            </ThemedText>
          </Pressable>

          {/* Medications */}
          <Pressable
            onPress={() => router.push({ pathname: '/visit/meds', params: { visitId: visit.id } })}
            style={[styles.bentoHalf, { backgroundColor: colors.surface, borderColor: colors.border }]}
          >
            <View style={[styles.iconCircle, { backgroundColor: colors.tint + '15' }]}>
              <Ionicons name="medkit" size={20} color={colors.tint} />
            </View>
            <ThemedText style={[styles.bentoCount, { color: colors.text }]}>{visit.medications.length}</ThemedText>
            <ThemedText style={[styles.bentoLabel, { color: colors.secondaryText }]}>Medications</ThemedText>
            {newMeds > 0 && (
              <View style={[styles.newBadge, { backgroundColor: colors.tint }]}>
                <ThemedText style={styles.newBadgeText}>{newMeds} new</ThemedText>
              </View>
            )}
          </Pressable>
        </View>

        <View style={styles.gridRow}>
          {/* Lab Tests */}
          <Pressable
            onPress={() => router.push({ pathname: '/visit/labs', params: { visitId: visit.id } })}
            style={[styles.bentoHalf, { backgroundColor: colors.surface, borderColor: colors.border }]}
          >
            <View style={[styles.iconCircle, { backgroundColor: '#F59E0B15' }]}>
              <Ionicons name="flask" size={20} color="#F59E0B" />
            </View>
            <ThemedText style={[styles.bentoCount, { color: colors.text }]}>{visit.labTests.length}</ThemedText>
            <ThemedText style={[styles.bentoLabel, { color: colors.secondaryText }]}>Lab Tests</ThemedText>
            <ThemedText style={[styles.bentoHint, { color: colors.secondaryText }]} numberOfLines={1}>
              {doneLabs} done · {pendingLabs} pending
            </ThemedText>
          </Pressable>

          {/* Follow-Ups */}
          <Pressable
            onPress={() => router.push({ pathname: '/visit/appointments', params: { visitId: visit.id } })}
            style={[styles.bentoHalf, { backgroundColor: colors.surface, borderColor: colors.border }]}
          >
            <View style={[styles.iconCircle, { backgroundColor: '#8B5CF615' }]}>
              <Ionicons name="calendar" size={20} color="#8B5CF6" />
            </View>
            <ThemedText style={[styles.bentoCount, { color: colors.text }]}>{visit.followUps.length}</ThemedText>
            <ThemedText style={[styles.bentoLabel, { color: colors.secondaryText }]}>Follow-Ups</ThemedText>
            <ThemedText style={[styles.bentoHint, { color: colors.secondaryText }]} numberOfLines={1}>
              {visit.followUps[0]?.date}
            </ThemedText>
          </Pressable>
        </View>

        {/* ── Transcript card (full width) ── */}
        <Pressable
          onPress={() => router.push({ pathname: '/visit/transcript', params: { visitId: visit.id } })}
          style={[styles.bentoFull, { backgroundColor: colors.surface, borderColor: colors.border, paddingVertical: 16 }]}
        >
          <View style={styles.bentoRow}>
            <View style={[styles.iconCircle, { backgroundColor: '#6B728015' }]}>
              <Ionicons name="chatbubbles" size={20} color="#6B7280" />
            </View>
            <ThemedText style={[styles.bentoFullTitle, { color: colors.text }]}>Full Transcript</ThemedText>
            <ThemedText style={[styles.countLabel, { color: colors.secondaryText }]}>
              {visit.transcript.length} entries
            </ThemedText>
            <Ionicons name="chevron-forward" size={18} color={colors.icon} />
          </View>
        </Pressable>

        <View style={{ height: 30 }} />
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1 },
  header: {
    paddingHorizontal: 20,
    paddingBottom: 16,
    borderBottomWidth: 1,
  },
  backBtn: { flexDirection: 'row', alignItems: 'center', gap: 4, marginBottom: 12 },
  backText: { fontSize: 17, fontWeight: '500' },
  headerDate: { fontSize: 26, fontWeight: '800' },
  headerDoctor: { fontSize: 15, marginTop: 4 },
  headerChief: { fontSize: 16, marginTop: 8, fontWeight: '500', lineHeight: 22 },

  scroll: { flex: 1 },
  scrollContent: { padding: 16 },

  /* Full-width bento card */
  bentoFull: {
    borderRadius: 16,
    padding: 18,
    borderWidth: 1,
    marginBottom: 12,
  },
  bentoRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
  },
  bentoFullTitle: { fontSize: 17, fontWeight: '700', flex: 1 },
  bentoPreview: { fontSize: 15, lineHeight: 22, marginTop: 10 },

  /* Half-width bento cards */
  gridRow: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 12,
  },
  bentoHalf: {
    flex: 1,
    borderRadius: 16,
    padding: 18,
    borderWidth: 1,
  },
  iconCircle: {
    width: 40,
    height: 40,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 12,
  },
  bentoCount: { fontSize: 34, fontWeight: '800', lineHeight: 38 },
  bentoLabel: { fontSize: 14, fontWeight: '600', marginTop: 2 },
  bentoHint: { fontSize: 12, marginTop: 8, lineHeight: 16 },
  newBadge: {
    marginTop: 8,
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 8,
    alignSelf: 'flex-start',
  },
  newBadgeText: { color: '#fff', fontSize: 12, fontWeight: '700' },
  countLabel: { fontSize: 13, marginRight: 2 },
});
