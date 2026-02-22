import React from 'react';
import { StyleSheet, View, ScrollView, Pressable } from 'react-native';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';

import { AppHeader } from '@/components/app-header';
import { ThemedText } from '@/components/themed-text';
import { useColorScheme } from '@/hooks/use-color-scheme';
import { Colors } from '@/constants/theme';
import { getVisits } from '@/data/visits';

export default function VisitsScreen() {
  const scheme = useColorScheme() ?? 'light';
  const colors = Colors[scheme];
  const router = useRouter();
  const visits = getVisits();

  return (
    <View style={[styles.screen, { backgroundColor: colors.background }]}>
      <AppHeader title="Your Visits" subtitle={`${visits.length} visits on record`} />

      <ScrollView style={styles.scroll} contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
        {visits.map((visit, index) => {
          const newMeds = visit.medications.filter((m) => m.isNew).length;
          const pendingLabs = visit.labTests.filter((l) => l.status !== 'completed').length;

          return (
            <Pressable
              key={visit.id}
              onPress={() => router.push({ pathname: '/visit/[id]', params: { id: visit.id } })}
              style={[styles.card, { backgroundColor: colors.surface, borderColor: colors.border }]}
            >
              {/* Date + Latest badge */}
              <View style={styles.topRow}>
                <ThemedText style={[styles.date, { color: colors.text }]}>{visit.visitDate}</ThemedText>
                {index === 0 && (
                  <View style={[styles.latestBadge, { backgroundColor: colors.tint }]}>
                    <ThemedText style={styles.latestText}>Latest</ThemedText>
                  </View>
                )}
              </View>

              {/* Doctor + specialty */}
              <ThemedText style={[styles.doctor, { color: colors.secondaryText }]}>
                {visit.doctorName} · {visit.specialty}
              </ThemedText>

              {/* Chief complaint */}
              <ThemedText style={[styles.complaint, { color: colors.text }]} numberOfLines={2}>
                {visit.chiefComplaint}
              </ThemedText>

              {/* Stats row */}
              <View style={styles.statsRow}>
                <View style={styles.stat}>
                  <Ionicons name="heart-outline" size={14} color="#EF4444" />
                  <ThemedText style={[styles.statText, { color: colors.secondaryText }]}>
                    {visit.diagnoses.length}
                  </ThemedText>
                </View>
                <View style={styles.stat}>
                  <Ionicons name="medkit-outline" size={14} color={colors.tint} />
                  <ThemedText style={[styles.statText, { color: colors.secondaryText }]}>
                    {visit.medications.length}
                    {newMeds > 0 ? ` (${newMeds} new)` : ''}
                  </ThemedText>
                </View>
                <View style={styles.stat}>
                  <Ionicons name="flask-outline" size={14} color="#F59E0B" />
                  <ThemedText style={[styles.statText, { color: colors.secondaryText }]}>
                    {visit.labTests.length}
                    {pendingLabs > 0 ? ` (${pendingLabs} pending)` : ''}
                  </ThemedText>
                </View>
                <View style={styles.stat}>
                  <Ionicons name="calendar-outline" size={14} color="#8B5CF6" />
                  <ThemedText style={[styles.statText, { color: colors.secondaryText }]}>
                    {visit.followUps.length}
                  </ThemedText>
                </View>

                <View style={{ flex: 1 }} />
                <Ionicons name="chevron-forward" size={18} color={colors.icon} />
              </View>
            </Pressable>
          );
        })}

        <View style={{ height: 20 }} />
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1 },
  scroll: { flex: 1 },
  scrollContent: { paddingHorizontal: 20, paddingTop: 16 },
  card: {
    borderRadius: 16,
    padding: 18,
    marginBottom: 12,
    borderWidth: 1,
  },
  topRow: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' },
  date: { fontSize: 20, fontWeight: '800' },
  latestBadge: { paddingHorizontal: 10, paddingVertical: 4, borderRadius: 8 },
  latestText: { color: '#fff', fontSize: 12, fontWeight: '700' },
  doctor: { fontSize: 14, marginTop: 4 },
  complaint: { fontSize: 16, fontWeight: '500', marginTop: 10, lineHeight: 22 },
  statsRow: { flexDirection: 'row', alignItems: 'center', gap: 14, marginTop: 14, paddingTop: 14, borderTopWidth: 1, borderTopColor: '#E7E8E820' },
  stat: { flexDirection: 'row', alignItems: 'center', gap: 4 },
  statText: { fontSize: 13, fontWeight: '500' },
});
