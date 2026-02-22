import React, { useState, useRef, useCallback, useEffect } from 'react';
import {
  StyleSheet,
  View,
  Pressable,
  ScrollView,
  Platform,
  Alert,
  ActivityIndicator,
} from 'react-native';
import {
  useAudioRecorder,
  AudioModule,
  RecordingPresets,
  setAudioModeAsync,
} from 'expo-audio';
import { Ionicons } from '@expo/vector-icons';

import { AppHeader } from '@/components/app-header';
import { ThemedText } from '@/components/themed-text';
import { WaveformVisualizer } from '@/components/waveform-visualizer';
import { useColorScheme } from '@/hooks/use-color-scheme';
import { Colors } from '@/constants/theme';
import { useAppData } from '@/contexts/data-context';
import { runFullPipeline, pipelineResponseToVisitRecord } from '@/services/api';
import type { TranscriptEntry } from '@/types/consultation';

export default function RecordScreen() {
  const scheme = useColorScheme() ?? 'light';
  const colors = Colors[scheme];
  const { patient, addVisit } = useAppData();
  const [recording, setRecording] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [elapsed, setElapsed] = useState(0);
  const [transcript, setTranscript] = useState<TranscriptEntry[]>([]);
  const [error, setError] = useState<string | null>(null);
  const audioRecorder = useAudioRecorder(RecordingPresets.HIGH_QUALITY);
  const timer = useRef<ReturnType<typeof setInterval> | null>(null);

  // Request microphone permission on mount
  useEffect(() => {
    (async () => {
      const status = await AudioModule.requestRecordingPermissionsAsync();
      if (!status.granted) {
        Alert.alert('Permission Required', 'Microphone access is needed to record visits.');
      }
    })();
  }, []);

  const formatTime = (secs: number) => {
    const m = Math.floor(secs / 60).toString().padStart(2, '0');
    const s = (secs % 60).toString().padStart(2, '0');
    return `${m}:${s}`;
  };

  const startRecording = useCallback(async () => {
    try {
      setError(null);

      // Configure audio session for recording
      await setAudioModeAsync({
        allowsRecording: true,
        playsInSilentMode: true,
      });

      // Prepare and start recording
      await audioRecorder.prepareToRecordAsync();
      audioRecorder.record();

      setRecording(true);
      setElapsed(0);
      setTranscript([]);
      timer.current = setInterval(() => setElapsed((e) => e + 1), 1000);
    } catch (err) {
      console.error('Failed to start recording:', err);
      setError('Failed to start recording. Please check microphone permissions.');
    }
  }, [audioRecorder]);

  const stopRecording = useCallback(async () => {
    setRecording(false);
    if (timer.current) clearInterval(timer.current);

    try {
      setProcessing(true);
      setError(null);

      // Stop the recording — URI available on audioRecorder.uri
      await audioRecorder.stop();
      const uri = audioRecorder.uri;

      // Reset audio mode
      await setAudioModeAsync({ allowsRecording: false });

      if (!uri) throw new Error('No audio file was created');

      // Send audio to backend pipeline
      const response = await runFullPipeline(uri, patient.name, patient.age);

      // Transform API response into a VisitRecord
      const newVisit = pipelineResponseToVisitRecord(response);

      // Display transcript from the processed result
      setTranscript(newVisit.transcript);

      // Save visit
      addVisit(newVisit);
      Alert.alert(
        'Visit Processed',
        'Your visit has been transcribed, analyzed, and saved successfully.',
      );
    } catch (err: any) {
      console.error('Pipeline error:', err);
      const msg = err.message || 'Failed to process recording. Please try again.';
      setError(msg);
      Alert.alert('Processing Error', msg);
    } finally {
      setProcessing(false);
    }
  }, [audioRecorder, patient, addVisit]);

  const toggleRecording = () => {
    if (processing) return;
    recording ? stopRecording() : startRecording();
  };

  return (
    <View style={[styles.screen, { backgroundColor: colors.background }]}>
      <AppHeader
        title="Record Visit"
        subtitle={
          processing
            ? 'Processing your recording...'
            : recording
              ? 'Listening to your doctor...'
              : 'Record your doctor visit'
        }
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

          {processing ? (
            <View style={[styles.micButton, { backgroundColor: colors.tint, opacity: 0.8 }]}>
              <ActivityIndicator size="large" color="#fff" />
            </View>
          ) : (
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
          )}

          <ThemedText style={[styles.hint, { color: colors.secondaryText }]}>
            {processing
              ? 'Transcribing & analyzing your visit...'
              : recording
                ? 'Tap to stop recording'
                : 'Tap to start recording'}
          </ThemedText>
        </View>

        {/* Error message */}
        {error && (
          <View style={[styles.errorCard, { backgroundColor: '#FEE2E2', borderColor: '#FECACA' }]}>
            <Ionicons name="alert-circle" size={16} color="#DC2626" />
            <ThemedText style={styles.errorText}>{error}</ThemedText>
          </View>
        )}

        {/* Live Transcript */}
        <View style={styles.transcriptSection}>
          <View style={styles.sectionHeader}>
            <Ionicons name="chatbubbles-outline" size={18} color={colors.tint} />
            <ThemedText style={[styles.sectionTitle, { color: colors.text }]}>
              Transcript
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
    lineHeight: 48,
    fontWeight: '200',
    fontVariant: ['tabular-nums'],
    marginVertical: 12,
    letterSpacing: 2,
    zIndex: 2,
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
  errorCard: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginTop: 12,
    padding: 14,
    borderRadius: 12,
    borderWidth: 1,
  },
  errorText: { color: '#DC2626', fontSize: 13, flex: 1, fontWeight: '500' },
});
