import React from 'react';
import { StyleSheet, View, ScrollView, Pressable } from 'react-native';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import { ThemedText } from '@/components/themed-text';
import { useColorScheme } from '@/hooks/use-color-scheme';
import { Colors } from '@/constants/theme';
import { getUpcomingAppointments } from '@/data/visits';

export default function AllAppointmentsPage() {
  const router = useRouter();
  const scheme = useColorScheme() ?? 'light';
  const colors = Colors[scheme];
  const insets = useSafeAreaInsets();

  const appointments = getUpcomingAppointments();

  return (
    <View style={[styles.screen, { backgroundColor: colors.background }]}>
      <View style={[styles.header, { paddingTop: insets.top + 8, backgroundColor: colors.headerBg, borderBottomColor: colors.border }]}>
        <View style={styles.headerRow}>
          <Pressable onPress={() => router.back()} style={[styles.backBtn, { backgroundColor: colors.tint + '15' }]} hitSlop={12}>
            <Ionicons name="chevron-back" size={20} color={colors.tint} />
          </Pressable>
          <Ionicons name="calendar" size={22} color="#8B5CF6" />
          <ThemedText style={[styles.pageTitle, { color: colors.text }]}>All Appointments</ThemedText>
        </View>
        <ThemedText style={[styles.pageSubtitle, { color: colors.secondaryText }]}>
          {appointments.length} total across all visits
        </ThemedText>
      </View>

      <ScrollView style={styles.scroll} contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
        {appointments.length === 0 ? (
          <View style={styles.empty}>
            <Ionicons name="calendar-outline" size={48} color={colors.icon} />
            <ThemedText style={[styles.emptyText, { color: colors.secondaryText }]}>
              No upcoming appointments
            </ThemedText>
          </View>
        ) : (
          appointments.map((appt, i) => (
            <View key={i} style={[styles.card, { backgroundColor: colors.surface, borderColor: colors.border }]}>
              <ThemedText style={[styles.name, { color: colors.text }]}>{appt.description}</ThemedText>
              {appt.date ? (
                <View style={styles.infoRow}>
                  <Ionicons name="time-outline" size={18} color="#8B5CF6" />
                  <ThemedText style={[styles.infoText, { color: colors.text }]}>{appt.date}</ThemedText>
                </View>
              ) : null}
              {appt.provider ? (
                <View style={styles.infoRow}>
                  <Ionicons name="person-outline" size={18} color={colors.secondaryText} />
                  <ThemedText style={[styles.infoText, { color: colors.secondaryText }]}>{appt.provider}</ThemedText>
                </View>
              ) : null}
              <View style={[styles.fromVisit, { backgroundColor: colors.border }]}>
                <ThemedText style={[styles.fromText, { color: colors.secondaryText }]}>
                  From visit: {appt.fromVisit}
                </ThemedText>
              </View>
            </View>
          ))
        )}
        <View style={{ height: 30 }} />
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
  empty: { alignItems: 'center', paddingVertical: 60, gap: 12 },
  emptyText: { fontSize: 16 },
  card: { borderRadius: 14, padding: 18, borderWidth: 1, marginBottom: 12 },
  name: { fontSize: 18, fontWeight: '700', lineHeight: 24 },
  infoRow: { flexDirection: 'row', alignItems: 'center', gap: 8, marginTop: 10 },
  infoText: { fontSize: 16 },
  fromVisit: { alignSelf: 'flex-start', marginTop: 12, paddingHorizontal: 10, paddingVertical: 4, borderRadius: 8 },
  fromText: { fontSize: 12, fontWeight: '600' },
});
