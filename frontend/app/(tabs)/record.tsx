import React, { useState, useRef, useCallback } from 'react';
import {
  StyleSheet,
  View,
  Pressable,
  ScrollView,
  Platform,
  Alert,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';

import { AppHeader } from '@/components/app-header';
import { ThemedText } from '@/components/themed-text';
import { WaveformVisualizer } from '@/components/waveform-visualizer';
import { useColorScheme } from '@/hooks/use-color-scheme';
import { Colors } from '@/constants/theme';
import { useAppData } from '@/contexts/data-context';
import type { TranscriptEntry } from '@/types/consultation';
import type { VisitRecord } from '@/data/visits';

export default function RecordScreen() {
  const scheme = useColorScheme() ?? 'light';
  const colors = Colors[scheme];
  const { visits, addVisit } = useAppData();
  const [recording, setRecording] = useState(false);
  const [elapsed, setElapsed] = useState(0);
  const [transcript, setTranscript] = useState<TranscriptEntry[]>([]);
  const timer = useRef<ReturnType<typeof setInterval> | null>(null);

  const formatTime = (secs: number) => {
    const m = Math.floor(secs / 60).toString().padStart(2, '0');
    const s = (secs % 60).toString().padStart(2, '0');
    return `${m}:${s}`;
  };

  const startRecording = useCallback(() => {
    setRecording(true);
    setElapsed(0);
    setTranscript([]);
    timer.current = setInterval(() => setElapsed((e) => e + 1), 1000);
    // TODO: connect to your FastAPI backend websocket
  }, []);

  const stopRecording = useCallback(() => {
    setRecording(false);
    if (timer.current) clearInterval(timer.current);

    // After recording stops, build a new visit from the transcript data.
    // In production this would come from the backend API response.
    // For now we create a placeholder visit that gets added to the data store.
    if (transcript.length > 0) {
      const now = new Date();
      const dateStr = now.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' });
      const newVisit: VisitRecord = {
        id: String(Date.now()),
        doctorName: 'New Doctor',
        specialty: 'General',
        visitDate: dateStr,
        chiefComplaint: 'Recorded visit',
        summaryText: 'This visit was just recorded. The summary will be generated once the transcript is processed by the backend.',
        diagnoses: [],
        medications: [],
        followUps: [],
        labTests: [],
        transcript,
      };
      addVisit(newVisit);
      Alert.alert('Visit Saved', 'Your recorded visit has been added to your history.');
    }
  }, [transcript, addVisit]);

  const toggleRecording = () => (recording ? stopRecording() : startRecording());

  return (
    <View style={[styles.screen, { backgroundColor: colors.background }]}>
      <AppHeader
        title="Record Visit"
        subtitle={recording ? 'Listening to your doctor...' : 'Record your doctor visit'}
      />

      <ScrollView
        style={styles.outerScroll}
        contentContainerStyle={styles.outerContent}
        showsVerticalScrollIndicator={false}
        keyboardShouldPersistTaps="handled"
      >
        {/* Waveform + Mic */}
        <View style={[styles.vizCard, { backgroundColor: colors.surface, borderColor: colors.border, shadowColor: colors.cardShadow }]}>
          <WaveformVisualizer active={recording} color={colors.tint} />

          <ThemedText style={[styles.timer, { color: recording ? colors.tint : colors.icon }]}>
            {formatTime(elapsed)}
          </ThemedText>

          <Pressable
            onPress={toggleRecording}
            style={({ pressed }) => [
              styles.micButton,
              {
                backgroundColor: recording ? '#EF4444' : colors.tint,
                transform: [{ scale: pressed ? 0.9 : 1 }],
              },
            ]}
          >
            <Ionicons name={recording ? 'stop' : 'mic'} size={32} color="#fff" />
          </Pressable>

          <ThemedText style={[styles.hint, { color: colors.secondaryText }]}>
            {recording ? 'Tap to stop recording' : 'Tap to start recording'}
          </ThemedText>
        </View>

        {/* Live Transcript */}
        <View style={styles.transcriptSection}>
          <View style={styles.sectionHeader}>
            <Ionicons name="chatbubbles-outline" size={18} color={colors.tint} />
            <ThemedText style={[styles.sectionTitle, { color: colors.text }]}>
              Live Transcript
            </ThemedText>
          </View>
          <View style={[styles.transcriptBox, { backgroundColor: colors.surface, borderColor: colors.border }]}>
            {transcript.length === 0 && (
              <View style={styles.emptyState}>
                <Ionicons name="chatbubble-ellipses-outline" size={40} color={colors.icon} />
                <ThemedText style={[styles.placeholder, { color: colors.secondaryText }]}>
                  {recording
                    ? 'Listening...'
                    : 'Press the button above to start recording your doctor visit.'}
                </ThemedText>
              </View>
            )}
            {transcript.map((entry, i) => (
              <View key={i} style={styles.transcriptEntry}>
                <View style={[styles.speakerBadge, {
                  backgroundColor: entry.speaker === 'doctor' ? colors.tint + '15' : '#10B98115'
                }]}>
                  <Ionicons
                    name={entry.speaker === 'doctor' ? 'person' : 'person-outline'}
                    size={12}
                    color={entry.speaker === 'doctor' ? colors.tint : '#10B981'}
                  />
                  <ThemedText style={[styles.speakerLabel, {
                    color: entry.speaker === 'doctor' ? colors.tint : '#10B981'
                  }]}>
                    {entry.speaker === 'doctor' ? 'Dr' : 'Pt'}
                  </ThemedText>
                </View>
                <ThemedText style={[styles.transcriptText, { color: colors.text }]}>{entry.text}</ThemedText>
              </View>
            ))}
          </View>
        </View>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1 },
  outerScroll: { flex: 1 },
  outerContent: { paddingHorizontal: 20, paddingTop: 20, paddingBottom: 30 },
  vizCard: {
    borderRadius: 20,
    padding: 24,
    alignItems: 'center',
    borderWidth: 1,
    ...Platform.select({
      ios: { shadowOffset: { width: 0, height: 4 }, shadowOpacity: 0.08, shadowRadius: 12 },
      android: { elevation: 4 },
      default: {},
    }),
  },
  timer: {
    fontSize: 44,
    fontWeight: '200',
    fontVariant: ['tabular-nums'],
    marginVertical: 12,
    letterSpacing: 2,
  },
  micButton: {
    width: 72,
    height: 72,
    borderRadius: 36,
    alignItems: 'center',
    justifyContent: 'center',
    ...Platform.select({
      ios: { shadowColor: '#000', shadowOffset: { width: 0, height: 4 }, shadowOpacity: 0.2, shadowRadius: 8 },
      android: { elevation: 8 },
      default: {},
    }),
  },
  hint: { marginTop: 10, fontSize: 13, fontWeight: '500' },
  transcriptSection: { marginTop: 20 },
  sectionHeader: { flexDirection: 'row', alignItems: 'center', gap: 8, marginBottom: 10 },
  sectionTitle: { fontSize: 16, fontWeight: '700' },
  transcriptBox: {
    borderWidth: 1,
    borderRadius: 16,
    padding: 16,
    minHeight: 120,
  },
  emptyState: { alignItems: 'center', paddingVertical: 20, gap: 10 },
  placeholder: { fontSize: 14, textAlign: 'center' },
  transcriptEntry: { flexDirection: 'row', marginBottom: 12, gap: 10, alignItems: 'flex-start' },
  speakerBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 10,
    gap: 4,
  },
  speakerLabel: { fontSize: 11, fontWeight: '700' },
  transcriptText: { flex: 1, fontSize: 14, lineHeight: 20 },
});
