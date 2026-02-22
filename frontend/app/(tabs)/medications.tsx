import React from 'react';
import { StyleSheet, View, ScrollView, Pressable } from 'react-native';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';

import { AppHeader } from '@/components/app-header';
import { ThemedText } from '@/components/themed-text';
import { useColorScheme } from '@/hooks/use-color-scheme';
import { Colors } from '@/constants/theme';
import { getCurrentMedications, getUpcomingAppointments, getPendingLabs } from '@/data/visits';
import { useAppData } from '@/contexts/data-context';

export default function CarePlanScreen() {
  const router = useRouter();
  const scheme = useColorScheme() ?? 'light';
  const colors = Colors[scheme];

  // Access visits from context to trigger re-renders when new visits are added
  const { visits } = useAppData();

  // These helpers read from the module-level store (synced via DataProvider)
  const meds = getCurrentMedications();
  const appointments = getUpcomingAppointments();
  const labs = getPendingLabs();

  return (
    <View style={[styles.screen, { backgroundColor: colors.background }]}>
      <AppHeader title="Care Plan" subtitle="Your current plan of care" />

      <ScrollView style={styles.scroll} contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
        {/* ── Medications (full width bento) ── */}
        <View style={[styles.bentoFull, { backgroundColor: colors.surface, borderColor: colors.border }]}>
          <View style={styles.bentoHeader}>
            <View style={[styles.iconCircle, { backgroundColor: colors.tint + '15' }]}>
              <Ionicons name="medkit" size={20} color={colors.tint} />
            </View>
            <View style={{ flex: 1 }}>
              <ThemedText style={[styles.bentoTitle, { color: colors.text }]}>Your Medications</ThemedText>
              <ThemedText style={[styles.bentoSub, { color: colors.secondaryText }]}>
                {meds.length} active · {meds.filter((m) => m.isNew).length} new
              </ThemedText>
            </View>
          </View>

          {meds.map((med, i) => (
            <View
              key={i}
              style={[styles.medItem, i > 0 && { borderTopWidth: 1, borderTopColor: colors.border }]}
            >
              <View style={styles.medTop}>
                <ThemedText style={[styles.medName, { color: colors.text }]}>{med.name}</ThemedText>
                {med.isNew && (
                  <View style={[styles.newBadge, { backgroundColor: colors.tint }]}>
                    <ThemedText style={styles.newBadgeText}>NEW</ThemedText>
                  </View>
                )}
              </View>
              <ThemedText style={[styles.medDose, { color: colors.secondaryText }]}>
                {med.dosage} — {med.frequency}
              </ThemedText>
              {med.notes ? (
                <ThemedText style={[styles.medNotes, { color: colors.secondaryText }]}>{med.notes}</ThemedText>
              ) : null}
            </View>
          ))}
        </View>

        {/* ── 2-column: Appointments + Labs ── */}
        <View style={styles.gridRow}>
          {/* Appointments */}
          <Pressable
            onPress={() => router.push('/all-appointments' as any)}
            style={[styles.bentoHalf, { backgroundColor: colors.surface, borderColor: colors.border }]}
          >
            <View style={[styles.iconCircle, { backgroundColor: '#8B5CF615' }]}>
              <Ionicons name="calendar" size={20} color="#8B5CF6" />
            </View>
            <ThemedText style={[styles.halfCount, { color: colors.text }]}>{appointments.length}</ThemedText>
            <ThemedText style={[styles.halfLabel, { color: colors.secondaryText }]}>Appointments</ThemedText>
            <ThemedText style={[styles.viewAll, { color: colors.tint }]}>View all →</ThemedText>
          </Pressable>

          {/* Pending Labs */}
          <Pressable
            onPress={() => router.push('/all-labs' as any)}
            style={[styles.bentoHalf, { backgroundColor: colors.surface, borderColor: colors.border }]}
          >
            <View style={[styles.iconCircle, { backgroundColor: '#F59E0B15' }]}>
              <Ionicons name="flask" size={20} color="#F59E0B" />
            </View>
            <ThemedText style={[styles.halfCount, { color: colors.text }]}>{labs.length}</ThemedText>
            <ThemedText style={[styles.halfLabel, { color: colors.secondaryText }]}>Pending Labs</ThemedText>
            <ThemedText style={[styles.viewAll, { color: colors.tint }]}>View all →</ThemedText>
          </Pressable>
        </View>

        <View style={{ height: 20 }} />
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1 },
  scroll: { flex: 1 },
  scrollContent: { padding: 16 },

  /* Full-width bento */
  bentoFull: {
    borderRadius: 16,
    padding: 18,
    borderWidth: 1,
    marginBottom: 12,
  },
  bentoHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    marginBottom: 4,
  },
  bentoTitle: { fontSize: 18, fontWeight: '800' },
  bentoSub: { fontSize: 13, marginTop: 2 },

  /* Medication items */
  medItem: { paddingVertical: 14 },
  medTop: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' },
  medName: { fontSize: 17, fontWeight: '700' },
  medDose: { fontSize: 15, marginTop: 4 },
  medNotes: { fontSize: 14, marginTop: 4, lineHeight: 20 },
  newBadge: { paddingHorizontal: 10, paddingVertical: 4, borderRadius: 8 },
  newBadgeText: { color: '#fff', fontSize: 11, fontWeight: '800', letterSpacing: 0.5 },

  /* Grid */
  gridRow: { flexDirection: 'row', gap: 12, marginBottom: 12 },
  bentoHalf: { flex: 1, borderRadius: 16, padding: 18, borderWidth: 1 },
  iconCircle: { width: 40, height: 40, borderRadius: 12, alignItems: 'center', justifyContent: 'center', marginBottom: 10 },
  halfCount: { fontSize: 30, fontWeight: '800', lineHeight: 34 },
  halfLabel: { fontSize: 14, fontWeight: '600', marginTop: 2 },

  viewAll: { fontSize: 13, fontWeight: '700', marginTop: 14, textAlign: 'center' },
});
