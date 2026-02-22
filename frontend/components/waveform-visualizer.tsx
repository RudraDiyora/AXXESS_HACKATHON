import React, { useEffect } from 'react';
import { StyleSheet, View } from 'react-native';
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withRepeat,
  withTiming,
  withDelay,
  withSequence,
  Easing,
  cancelAnimation,
} from 'react-native-reanimated';

const BAR_COUNT = 28;
const BAR_WIDTH = 3;
const BAR_GAP = 3;
const MAX_HEIGHT = 36;
const MIN_HEIGHT = 4;

interface WaveformVisualizerProps {
  active: boolean;
  color?: string;
}

/**
 * Animated frequency-bar visualizer that simulates audio waveforms.
 * Each bar oscillates at a randomised frequency to mimic real-time STT input.
 */
export function WaveformVisualizer({ active, color = '#4F8EF7' }: WaveformVisualizerProps) {
  const bars = Array.from({ length: BAR_COUNT }, (_, i) => (
    <Bar key={i} index={i} active={active} color={color} />
  ));

  return <View style={styles.container}>{bars}</View>;
}

function Bar({ index, active, color }: { index: number; active: boolean; color: string }) {
  const height = useSharedValue(MIN_HEIGHT);

  useEffect(() => {
    if (active) {
      const duration = 300 + Math.random() * 400;
      const peak = MIN_HEIGHT + Math.random() * (MAX_HEIGHT - MIN_HEIGHT);
      height.value = withDelay(
        index * 30,
        withRepeat(
          withSequence(
            withTiming(peak, { duration, easing: Easing.inOut(Easing.sin) }),
            withTiming(MIN_HEIGHT + Math.random() * 12, {
              duration: duration * 0.8,
              easing: Easing.inOut(Easing.sin),
            }),
          ),
          -1,
          true,
        ),
      );
    } else {
      cancelAnimation(height);
      height.value = withTiming(MIN_HEIGHT, { duration: 400 });
    }
  }, [active]);

  const animatedStyle = useAnimatedStyle(() => ({
    height: height.value,
  }));

  return <Animated.View style={[styles.bar, { backgroundColor: color }, animatedStyle]} />;
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    justifyContent: 'center',
    height: MAX_HEIGHT,
    gap: BAR_GAP,
  },
  bar: {
    width: BAR_WIDTH,
    borderRadius: BAR_WIDTH / 2,
    minHeight: MIN_HEIGHT,
  },
});
