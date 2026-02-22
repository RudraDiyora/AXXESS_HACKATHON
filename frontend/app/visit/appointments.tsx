import React from 'react';
import { StyleSheet, View, ScrollView, Pressable } from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import { ThemedText } from '@/components/themed-text';
import { useColorScheme } from '@/hooks/use-color-scheme';
import { Colors } from '@/constants/theme';
import { getVisit } from '@/data/visits';

export default function AppointmentsPage() {
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
          <Ionicons name="calendar" size={22} color="#8B5CF6" />
          <ThemedText style={[styles.pageTitle, { color: colors.text }]}>Follow-Up Appointments</ThemedText>
        </View>
        <ThemedText style={[styles.pageSubtitle, { color: colors.secondaryText }]}>{visit.visitDate}</ThemedText>
      </View>

      <ScrollView style={styles.scroll} contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
        {visit.followUps.map((fu, i) => (
          <View key={i} style={[styles.card, { backgroundColor: colors.surface, borderColor: colors.border }]}>
            <ThemedText style={[styles.name, { color: colors.text }]}>{fu.description}</ThemedText>
            {fu.date ? (
              <View style={styles.infoRow}>
                <Ionicons name="time-outline" size={18} color={colors.secondaryText} />
                <ThemedText style={[styles.infoText, { color: colors.secondaryText }]}>{fu.date}</ThemedText>
              </View>
            ) : null}
            {fu.provider ? (
              <View style={styles.infoRow}>
                <Ionicons name="person-outline" size={18} color={colors.secondaryText} />
                <ThemedText style={[styles.infoText, { color: colors.secondaryText }]}>{fu.provider}</ThemedText>
              </View>
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
  name: { fontSize: 19, fontWeight: '700', lineHeight: 26 },
  infoRow: { flexDirection: 'row', alignItems: 'center', gap: 8, marginTop: 10 },
  infoText: { fontSize: 16 },
});
